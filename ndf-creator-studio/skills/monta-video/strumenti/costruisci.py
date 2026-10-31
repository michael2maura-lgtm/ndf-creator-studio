"""Passo 6: costruisce la pagina HyperFrames del reel (video + sottotitoli + titoli + finale).

Uso:  python3 strumenti/costruisci.py <nome-lavoro> [--zone]
      --zone colora di rosso le zone che Instagram copre e la faccia: solo per le prove, non per il video finale.

Legge da lavori/<nome>/: tagliato.mp4, parole.json, faccia.json, piano.json
  piano.json (lo scrive Claude, tempi in secondi del video TAGLIATO):
  {"stile": "ndf",
   "correzioni": {"effeccamento": "affiancamento"},        sostituzioni nel testo dei sottotitoli
   "aggiungi": [{"testo": "persone.", "da": 50.1, "a": 50.7}],  parole che Whisper ha saltato
   "colore": "argento",                                     facoltativo: look del girato (strumenti/colore.py)
   "titoli": [{"da": 1.3, "a": 3.6, "sopra": "nel network", "grande": "NON SI GUADAGNA", "sotto": "", "colore": "accento"}],
   "finale_da": 76.0, "finale_testo": "COMMENTA INFO", "finale_sotto": "qui sotto"}   (testo e sotto: facoltativi)
Scrive lavori/<nome>/reel/ (index.html + file), pronta per hyperframes render.
"""
import html
import json
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import STUDIO, cartella_lavoro, cartella_stile, con_le_scelte, durata, leggi, trova  # noqa: E402
import colore as look_girato  # noqa: E402
import grafica  # noqa: E402
import scene  # noqa: E402
import sottotitoli  # noqa: E402
import split  # noqa: E402
import suoni_reel  # noqa: E402

# zone sicure di Instagram: regole/instagram.md
ZONA = {"alto": 220, "basso": 1470, "lati": 35, "destra_pulsanti": 980, "pulsanti_da": 1155}
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"


def colore(stile, nome):
    return stile["colori"].get(nome or "testo", nome or stile["colori"]["testo"])


def righe(font, testo, larghezza, spaziatura=0):
    """Quante righe occupa il testo andando a capo tra le parole, e la parola più larga."""
    def largo(s):
        return font.getlength(s) + spaziatura * len(s)
    parole = testo.split()
    n, riga, piu_larga = 1, "", 0
    for p in parole:
        piu_larga = max(piu_larga, largo(p))
        prova = f"{riga} {p}".strip()
        if riga and largo(prova) > larghezza:
            n, riga = n + 1, p
        else:
            riga = prova
    return n, piu_larga


def dimensione_titolo(t, stile, cart_stile, larghezza, y_alto, y_basso, extra=0):
    """La dimensione più grande (fino a quella dello stile) con cui il titolo entra in larghezza e in altezza.
    Si misura con il font vero: una parola lunga ("DISORGANIZZATE") o un blocco alto non escono mai dalla zona."""
    from PIL import ImageFont
    ft, fc, tt = stile["font"]["titoli"], stile["font"]["corsivo"], stile["titoli"]
    corsivo = ImageFont.truetype(os.path.join(cart_stile, fc["file"]), tt["dimensione_corsivo"])
    alt_cors = sum(righe(corsivo, t[k], larghezza)[0] * tt["dimensione_corsivo"] * 1.05 + 8
                   for k in ("sopra", "sotto") if t.get(k))
    size = tt["dimensione_grande"]
    while size > 60:
        f = ImageFont.truetype(os.path.join(cart_stile, ft["file"]), size)
        try:
            f.set_variation_by_axes([ft.get("peso", 800)])
        except (OSError, AttributeError):
            pass
        n, piu_larga = righe(f, t["grande"], larghezza, spaziatura=-2)
        if piu_larga <= larghezza and y_alto + n * size * 0.95 + alt_cors + extra <= y_basso:
            break
        size -= 4
    return size


def parole_corrette(parole, piano):
    """Applica correzioni e aggiunte. Le correzioni di più parole lavorano sul testo unito."""
    parole = sorted(parole + piano.get("aggiungi", []), key=lambda w: w["da"])
    for sbagliato, giusto in piano.get("correzioni", {}).items():
        pezzi_s, pezzi_g = sbagliato.split(), giusto.split()
        n = len(pezzi_s)
        i = 0
        while i <= len(parole) - n:
            finestra = [re.sub(r"[^\w']", "", parole[i + k]["testo"]).lower() for k in range(n)]
            if finestra == [p.lower() for p in pezzi_s]:
                punto = re.sub(r"[\w']", "", parole[i + n - 1]["testo"])
                da, a = parole[i]["da"], parole[i + n - 1]["a"]
                passo = (a - da) / len(pezzi_g)
                nuove = [{"testo": g, "da": round(da + k * passo, 2), "a": round(da + (k + 1) * passo, 2)}
                         for k, g in enumerate(pezzi_g)]
                nuove[-1]["testo"] += punto
                parole[i:i + n] = nuove
                i += len(pezzi_g)
            else:
                i += 1
    return parole


def zone_rosse(faccia):
    """Le zone che Instagram copre (rosso) e la faccia (giallo): solo per le prove."""
    return (f'<div class="zona" style="top:0;height:{ZONA["alto"]}px;left:0;right:0"></div>'
            f'<div class="zona" style="top:{ZONA["basso"]}px;bottom:0;left:0;right:0"></div>'
            f'<div class="zona" style="top:{ZONA["pulsanti_da"]}px;bottom:0;left:{ZONA["destra_pulsanti"]}px;right:0"></div>'
            f'<div class="zona" style="top:{faccia["occhi"]}px;height:{faccia["mento"] - faccia["occhi"]}px;'
            f'left:{faccia["sinistra"]}px;width:{faccia["destra"] - faccia["sinistra"]}px;background:rgba(255,255,0,.25)"></div>')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    cart = cartella_lavoro(args[0])
    piano = leggi(os.path.join(cart, "piano.json"))
    cart_stile = cartella_stile(piano.get("stile", "ndf"))
    stile = con_le_scelte(piano.get("stile", "ndf"), leggi(os.path.join(cart_stile, "stile.json")))
    faccia = leggi(os.path.join(cart, "faccia.json"))
    parole = parole_corrette(leggi(os.path.join(cart, "parole.json")), piano)
    # colore del girato: quello del piano ("colore": "argento"), se no quello scelto nella pagina, se no l'originale
    video = look_girato.applica(cart, piano.get("colore", stile.get("colore_scelto", stile.get("colore"))))  # "colore" = look di serie dello stile
    D = min(durata(video), piano.get("durata_max", 10 ** 6))  # durata_max: per le prove corte
    if stile.get("motore") == "grafica":  # stili con motion graphics: tutto in strumenti/grafica.py
        grafica.costruisci(cart, piano, stile, cart_stile, parole, faccia, D,
                           zone_rosse(faccia) if "--zone" in sys.argv else "")
        return
    split_on = piano.get("layout") == "split"
    if split_on:  # la persona scende: anche faccia e scritte scendono con lei
        faccia = dict(faccia, occhi=faccia["occhi"] + split.SPOSTA, mento=faccia["mento"] + split.SPOSTA)

    reel = os.path.join(cart, "reel")
    os.makedirs(os.path.join(reel, "assets"), exist_ok=True)
    dest_video = os.path.join(reel, "assets", "tagliato.mp4")
    if os.path.exists(dest_video):
        os.remove(dest_video)
    try:
        os.link(video, dest_video)
    except OSError:
        shutil.copy2(video, dest_video)
    font = {}
    for ruolo, f in stile["font"].items():
        shutil.copy2(os.path.join(cart_stile, f["file"]), os.path.join(reel, "assets", os.path.basename(f["file"])))
        font[ruolo] = f

    # dove stanno le scritte: sotto il mento, dentro la zona sicura
    y_sub = min(max(faccia["mento"] + 170, 900), ZONA["basso"] - 80)
    y_tit = min(max(faccia["mento"] + 60, 900), ZONA["basso"] - 330)
    ts, tt, fin = stile["sottotitoli"], stile["titoli"], stile["finale"]
    titoli = piano.get("titoli", [])
    finale_da = piano.get("finale_da", D - fin["secondi"])

    # solo quello che comincia prima della fine del video (con "durata_max" o un taglio, il resto si blocca nel render)
    scene_piano = [x for x in piano.get("scene", []) if x["da"] < D - 0.2]
    titoli = [x for x in titoli if x["da"] < D - 0.2]
    liste = [x for x in piano.get("liste", []) if x["da"] < D - 0.2]
    chiave = {p.lower() for p in piano.get("parole_chiave", [])}

    def coperto(t):
        return any(x["da"] <= t < x["a"] for x in titoli + scene_piano + liste
                   + [p for p in piano.get("pannelli", []) if p.get("frase") or p.get("pieno")]) or t >= finale_da

    margine = 1080 - ZONA["destra_pulsanti"] + 10  # stesso margine a sinistra e a destra: mai sotto i pulsanti
    larghezza = 1080 - 2 * margine - 10
    limite = ZONA["basso"] - 10
    corpo, tl = [], []
    css_sott = ""
    propri = stile.get("sottotitoli_nome") if stile.get("sottotitoli_nome") not in (None, "ndf-classico") else None
    if stile.get("sottotitoli_scelti") or propri:  # scelti nella pagina, o quelli dello stile (strumenti/sottotitoli.py)
        nascondi = [(x["da"], x["a"]) for x in titoli + scene_piano + liste
                    + [p for p in piano.get("pannelli", []) if p.get("frase") or p.get("pieno")]] + [(finale_da, D + 1)]
        css_sott, c_sott, tl_sott, f_sott = sottotitoli.parti(stile.get("sottotitoli_scelti") or propri, parole, chiave, y_sub + 40,
                                                            nascondi, stile["colori"])
        corpo += c_sott
        tl += tl_sott
        for f in f_sott:
            shutil.copy2(os.path.join(STUDIO, "font", f), os.path.join(reel, "assets", f))
    # sottotitoli dello stile: una parola alla volta, nascosta sotto i titoli e nel finale
    for i, w in enumerate(parole if not css_sott else []):
        testo = re.sub(r"[.,;:!?\"«»]", "", w["testo"]).strip()
        if not testo or coperto(w["da"]):
            continue
        fine = parole[i + 1]["da"] if i + 1 < len(parole) else w["a"]
        fine = min(fine, w["da"] + 0.9)
        if ts.get("maiuscolo"):
            testo = testo.upper()
        # le parole chiave nel colore d'accento; ogni parola "salta" dentro (piccola, poi grande), come nel vecchio kit
        stile_parola = f' style="color:{stile["colori"]["accento"]}"' if testo.lower() in chiave else ""
        corpo.append(f'<div class="sub" id="w{i}"{stile_parola}>{html.escape(testo)}</div>')
        tl.append(f'tl.set("#w{i}",{{opacity:1}},{w["da"]:.3f});'
                  f'tl.fromTo("#w{i}",{{scale:0.7}},{{scale:1,duration:0.12,ease:"back.out(2)"}},{w["da"]:.3f});'
                  f'tl.set("#w{i}",{{opacity:0}},{fine:.3f});')

    for n, t in enumerate(titoli):
        blocco = []
        if t.get("sopra"):
            blocco.append(f'<div class="cors">{html.escape(t["sopra"])}</div>')
        size = dimensione_titolo(t, stile, cart_stile, larghezza, y_tit, limite)
        blocco.append(f'<div class="grande" id="t{n}g" style="color:{colore(stile, t.get("colore"))};font-size:{size}px">'
                      f'{html.escape(t["grande"])}</div>')
        if t.get("sotto"):
            blocco.append(f'<div class="cors acc">{html.escape(t["sotto"])}</div>')
        corpo.append(f'<div class="tit" id="t{n}">{"".join(blocco)}</div>')
        uscita = max(t["a"], t["da"] + tt["durata_minima"]) - tt["uscita"]
        tl.append(f'tl.fromTo("#t{n}",{{opacity:0,y:50,scale:0.96}},{{opacity:1,y:0,scale:1,duration:{tt["entrata"]},ease:"power3.out"}},{t["da"]:.3f});'
                  # prima il corsivo, un attimo dopo la parola grande
                  + (f'tl.fromTo("#t{n}g",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.25,ease:"power3.out"}},{t["da"] + 0.15:.3f});'
                     if t.get("sopra") else "")
                  + f'tl.to("#t{n}",{{opacity:0,duration:{tt["uscita"]}}},{uscita:.3f});')

    # elenchi sopra la persona: le parole si sommano una sotto l'altra, l'ultima nel colore d'accento
    for n, l in enumerate(liste):
        voci = l["voci"]
        righe = "".join(f'<div class="grande" id="l{n}v{k}" style="font-size:{l.get("dimensione", 84)}px;opacity:0;'
                        f'color:{stile["colori"]["accento"] if k == len(voci) - 1 else stile["colori"]["testo"]}">{html.escape(v)}</div>'
                        for k, (v, _) in enumerate(voci))
        corpo.append(f'<div class="tit" id="l{n}" style="opacity:1">{righe}</div>')
        for k, (_, t0) in enumerate(voci):
            tl.append(f'tl.fromTo("#l{n}v{k}",{{opacity:0,y:40,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.22,ease:"power3.out"}},{t0:.3f});')
        tl.append(f'tl.to("#l{n} .grande",{{opacity:0,duration:0.2}},{l["a"] - 0.2:.3f});')

    # scene a tutto schermo (strumenti/scene.py): la scritta può essere grande, c'è tutto lo schermo
    for n, s in enumerate(scene_piano):
        if s["tipo"] == "clip":
            shutil.copy2(trova(s["clip"] + ".mp4", "clip"), os.path.join(reel, "assets", f"clip-{s['clip']}.mp4"))
        size = 150 if not s.get("grande") else dimensione_titolo(dict(s, sotto=s.get("sotto")), dict(stile, titoli=dict(tt, dimensione_grande=150,
                                 dimensione_corsivo=78)), cart_stile, 1080 - 240, 600, 1350)
        if s["tipo"] == "immagine":
            shutil.copy2(trova(s["immagine"] + ".jpg", "immagini"), os.path.join(reel, "assets", f"img-{s['immagine']}.jpg"))
        div, anim = scene.costruisci_scena(s, n, stile["colori"], size)
        corpo.append(div)
        tl.append(anim + scene.entrata(s, n))
    if any(s.get("entrata") == "lampo" for s in scene_piano):
        corpo.append(scene.LAMPO)

    # effetti sulla persona (la voce e i sottotitoli continuano): "bianconero" = grigio, sfocato e quasi buio sulle
    # frasi negative; "griglia" = l'inquadratura si moltiplica in una griglia di copie di te
    for n, x in enumerate(piano.get("effetti_video", [])):
        da, a = x["da"], x["a"]
        if x["tipo"] == "bianconero":
            tl.append(f'tl.fromTo("#bg",{{filter:"grayscale(0) blur(0px) brightness(1)"}},{{filter:"grayscale(1) blur(7px) brightness(0.45)",duration:0.25,immediateRender:false}},{da:.3f});'
                      f'tl.to("#bg",{{filter:"grayscale(1) blur(0px) brightness(0.9)",duration:0.3}},{da + 0.35:.3f});'
                      f'tl.set("#bg",{{filter:"none"}},{a:.3f});')
        elif x["tipo"] == "griglia":
            celle = "".join(f'<video id="gv{n}_{k}" src="assets/tagliato.mp4" muted playsinline data-start="{da:.3f}" '
                            f'data-media-start="{da:.3f}" data-duration="{a - da:.3f}"></video>' for k in range(12))
            corpo.append(f'<div class="griglia-v" id="gr{n}">{celle}</div>')
            tl.append(f'tl.set("#gr{n}",{{opacity:1}},{da:.3f});tl.set("#gr{n}",{{opacity:0}},{a:.3f});')
            for k in range(12):
                tl.append(f'tl.fromTo("#gv{n}_{k}",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:0.15,immediateRender:false}},{da + 0.03 * k:.3f});')

    # zoom a scatti: a ogni pezzo del taglio l'inquadratura si stringe o si allarga, centrata sulla faccia
    if piano.get("zoom"):
        cx = (faccia["sinistra"] + faccia["destra"]) / 2
        cy = (faccia["occhi"] + faccia["mento"]) / 2
        tl.append(f'gsap.set("#bg",{{transformOrigin:"{cx:.0f}px {cy:.0f}px"}});')
        for k, seg in enumerate(leggi(os.path.join(cart, "segmenti.json"))):
            tl.append(f'tl.set("#bg",{{scale:{1.0 if k % 2 == 0 else piano["zoom"]}}},{seg["inizio"]:.3f});')

    if split_on:
        tl.append(f'gsap.set("#bg",{{y:{split.SPOSTA}}});')
        corpo.insert(0, '<div id="split-fondo"></div>')
        for n, p in enumerate(piano.get("pannelli", [])):
            div, anim = split.pannello(p, n, stile["colori"], parole, chiave)
            corpo.append(div)
            tl.append(anim)

    audio_extra = suoni_reel.prepara(piano, stile, cart_stile, reel, D)

    testo_fin = piano.get("finale_testo", fin["testo"])
    sotto_fin = piano.get("finale_sotto", "qui sotto")
    size_fin = dimensione_titolo({"grande": testo_fin, "sotto": sotto_fin}, stile, cart_stile, larghezza, y_tit, limite,
                                 extra=100)  # la freccia
    corpo.append(f'<div class="tit" id="fin"><div class="grande" style="color:{colore(stile, fin["colore"])};font-size:{size_fin}px">'
                 f'{html.escape(testo_fin)}</div><div class="cors">{html.escape(sotto_fin)}</div>'
                 f'<div class="freccia" id="freccia">↓</div></div>')
    tl.append(f'tl.fromTo("#fin",{{opacity:0,y:50}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{finale_da:.3f});'
              f'tl.fromTo("#freccia",{{y:0}},{{y:24,duration:0.45,repeat:{int((D - finale_da) / 0.45)},yoyo:true,ease:"sine.inOut"}},{finale_da + 0.4:.3f});')

    zone = zone_rosse(faccia) if "--zone" in sys.argv else ""

    c = stile["colori"]
    ombra = "0 4px 18px rgba(0,0,0,.65), 0 1px 3px rgba(0,0,0,.8)"
    pagina = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
@font-face{{font-family:'{font["titoli"]["famiglia"]}';src:url('assets/{os.path.basename(font["titoli"]["file"])}');font-weight:100 900}}
@font-face{{font-family:'{font["corsivo"]["famiglia"]}';src:url('assets/{os.path.basename(font["corsivo"]["file"])}');font-style:italic}}
html,body{{margin:0;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden}}
#bg{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
.sub{{position:absolute;left:{margine}px;right:{margine}px;top:{y_sub}px;text-align:center;opacity:0;
 font-family:'{font["titoli"]["famiglia"]}';font-weight:{font["titoli"]["peso"]};font-size:{ts["dimensione"]}px;
 color:{colore(stile, ts["colore"])};letter-spacing:-1px;text-shadow:{ombra}}}
.tit{{position:absolute;left:{margine}px;right:{margine}px;top:{y_tit}px;text-align:center;opacity:0;text-wrap:balance}}
.grande{{font-family:'{font["titoli"]["famiglia"]}';font-weight:{font["titoli"]["peso"]};font-size:{tt["dimensione_grande"]}px;
 line-height:.95;letter-spacing:-2px;text-shadow:{ombra}}}
.cors{{font-family:'{font["corsivo"]["famiglia"]}';font-style:italic;font-size:{tt["dimensione_corsivo"]}px;line-height:1.05;
 color:{c["testo"]};text-shadow:{ombra};margin:4px 0}}
.cors.acc{{color:{c["accento_luce"]}}}
.freccia{{font-family:'{font["titoli"]["famiglia"]}';font-weight:800;font-size:90px;color:{c["testo"]};text-shadow:{ombra}}}
.zona{{position:absolute;background:rgba(255,0,0,.35);z-index:50}}
.tit,.sub{{z-index:30}}
{scene.CSS}
{scene.CSS_ADS}
.griglia-v{{position:absolute;inset:0;z-index:25;opacity:0;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);
 gap:10px;background:#000;filter:grayscale(1)}}
.griglia-v video{{width:100%;height:100%;object-fit:cover}}
{'.grande{{text-shadow:0 0 28px ' + c["accento"] + 'cc,0 0 60px ' + c["accento"] + '77,0 4px 14px rgba(0,0,0,.6)}}' if stile.get("bagliore") else ''}
{split.CSS if split_on else ''}
{css_sott}
</style>
<script src="{GSAP}"></script>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1080" data-height="1920">
<audio id="voce" src="assets/tagliato.mp4" data-start="0" data-media-start="0" data-duration="{D:.3f}" data-volume="1"></audio>
<video id="bg" src="assets/tagliato.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{D:.3f}"></video>
{chr(10).join(audio_extra)}
{chr(10).join(corpo)}
{zone}
</div>
<script>
const tl = gsap.timeline({{paused: true}});
function contaNumero(sel, fino, da, dur) {{
  const el = document.querySelector(sel); const o = {{v: 0}};
  tl.to(o, {{v: fino, duration: dur, ease: "power2.out", onUpdate: () => {{ el.textContent = Math.round(o.v); }}}}, da);
}}
{sottotitoli.JS}
{chr(10).join(tl)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    with open(os.path.join(reel, "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina)
    with open(os.path.join(reel, "hyperframes.json"), "w", encoding="utf-8") as f:
        json.dump({"paths": {"assets": "assets"}}, f)
    n_sub = sum(1 for x in corpo if 'class="sub"' in x or 'class="st"' in x)
    print(f"Reel costruito: {n_sub} sottotitoli, {len(titoli)} titoli, {len(scene_piano)} scene, "
          f"{len(audio_extra)} suoni, finale da {finale_da:.1f} s, durata {D:.1f} s")
    print(f"Sottotitoli a y {y_sub}, titoli da y {y_tit} (mento a y {faccia['mento']})")


if __name__ == "__main__":
    main()
