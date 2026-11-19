"""Effetti di scritte e carte (18/11/2026), rifatti da noi guardando come si muovono gli effetti di riferimento
(mai copiato il codice). Motore grafica, tempi del video TAGLIATO. Mentre ci sono, i sottotitoli si nascondono.

 {"tipo": "cancella", "da", "a", "testo": "la vecchia me", "testo_da": t, "via": t}
     Scritta che si cancella: sopra la testa una frase in corsivo si scrive lettera per lettera, poi una passata di
     luce la cancella da sinistra a destra ("via": quando parte la passata). Per quello che lasci andare, il prima.
 {"tipo": "lettere", "da", "a", "testo": "METODO", "sotto": "in tre passi", "sotto_da": t}
     Lettere che cadono: le lettere di una parola cadono dall'alto una alla volta e rimbalzano, poi sotto si scrive
     una riga piccola in corsivo. Per la parola chiave all'inizio di un video. Parola corta (max 10 lettere).
 {"tipo": "ventaglio", "da", "a", "carte": [["programmi", t], ["montatore", t]], "chiudi": t}
     Carte a ventaglio: davanti al petto si apre una mano di carte, una per ogni cosa detta, e alla fine si richiude.
     Una carta può essere una foto: {"testo": "...", "t": t, "secondo": s} (un fotogramma del video) o
     {"t": t, "immagine": "nome.jpg"} (da DATI/immagini). Da 2 a 5 carte. Per un elenco di cose.
 {"tipo": "polaroid", "da", "a", "foto": [["prima", t], ["tre ore", t, secondo]]}
     Polaroid: le foto in cornice bianca cadono una alla volta e si posano attorno a te, con la didascalia scritta
     a mano. La foto è un fotogramma del video (al "secondo" dato, se no a caso) o "immagine" da DATI/immagini.
     Al massimo 4. Per un ricordo, un prima e dopo, un racconto.
 {"tipo": "vocale", "da", "a", "testo": "riga sopra (facoltativa)"}
     Messaggio vocale: sul petto compare un messaggio vocale; il tasto parte, l'onda si colora mentre "suona" e il
     tempo scorre. Per "gli ho mandato un vocale", "ti scrivo", un messaggio.
"""
import html
import os
import random
import shutil
import subprocess

from comune import DATI, FFMPEG

E = html.escape


def _css(r):
    if getattr(r, "css_carte", False):
        return
    r.css_carte = True
    for f in ("InterTight.ttf", "InstrumentSerif-Italic.ttf", "Caveat.ttf", "PlayfairDisplay-Italic.ttf"):
        r.font_extra(f)
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}"
        "@font-face{font-family:'ISerifI';src:url('assets/InstrumentSerif-Italic.ttf')}"
        "@font-face{font-family:'Caveat';src:url('assets/Caveat.ttf');font-weight:400 700}"
        "@font-face{font-family:'PlayI';src:url('assets/PlayfairDisplay-Italic.ttf');font-weight:400 900}"
        ".ec-riga{position:absolute;left:20px;right:20px;text-align:center;white-space:nowrap;z-index:31;line-height:1}"
        ".ec-riga span{display:inline-block;opacity:0}"
        ".ec-ombra{text-shadow:0 0 22px rgba(0,0,0,.55),0 4px 14px rgba(0,0,0,.6),0 1px 3px rgba(0,0,0,.55)}"
        ".ec-luce{position:absolute;top:-25%;width:90px;height:150%;opacity:0;filter:blur(7px);transform:skewX(-18deg);"
        "background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,252,245,.85),rgba(255,255,255,0))}"
        ".ec-perno{position:absolute;width:0;height:0;z-index:31}"
        ".ec-carta{position:absolute;border-radius:26px;box-shadow:0 16px 34px rgba(0,0,0,.42);overflow:hidden;"
        "display:flex;align-items:flex-start;justify-content:center;text-align:center;font-family:'Inter Tight';"
        "font-weight:800;line-height:1.02;padding:30px 18px;box-sizing:border-box;opacity:0}"
        ".ec-carta img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}"
        ".ec-carta em{position:absolute;right:20px;bottom:10px;font-style:normal;font-weight:900;font-size:110px;line-height:1;opacity:.22}"
        ".ec-pol{position:absolute;background:#FBF9F4;border-radius:6px;box-shadow:0 16px 30px rgba(0,0,0,.45);"
        "padding:16px 16px 0;box-sizing:border-box;opacity:0;z-index:31}"
        ".ec-pol img{display:block;object-fit:cover;border-radius:2px}"
        ".ec-pol div{font:700 44px/62px Caveat;color:#28242A;text-align:center;white-space:nowrap}"
        ".ec-voc{position:absolute;opacity:0;z-index:31;font-family:'Inter Tight'}"
        ".ec-voc .bolla{position:relative;height:132px;border-radius:66px;background:#fff;box-shadow:0 16px 34px rgba(0,0,0,.38);"
        "display:flex;align-items:center;gap:22px;padding:0 36px 0 24px;box-sizing:border-box}"
        ".ec-voc .tasto{position:relative;width:86px;height:86px;border-radius:50%;flex:none;display:grid;place-items:center}"
        ".ec-voc .onda{position:relative;flex:1;height:76px}"
        ".ec-voc .onda>div{position:absolute;inset:0;display:flex;align-items:center;gap:6px}"
        ".ec-voc .onda i{flex:1;border-radius:5px}"
        ".ec-voc .ora{font-weight:700;font-size:32px;color:#55555D;font-variant-numeric:tabular-nums;width:74px;text-align:right}"
        ".ec-voc .sopra{font-weight:800;font-size:28px;letter-spacing:.16em;color:#fff;margin:0 0 12px 26px;"
        "text-shadow:0 2px 10px rgba(0,0,0,.6)}"
        "</style>")


def _cima(faccia):
    return faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95


def _cx(faccia):
    return (faccia["sinistra"] + faccia["destra"]) / 2


def _foto(r, nome, secondo=None, immagine=None, w=240, h=240, faccia=None):
    """Una foto per carte e polaroid: un'immagine di DATI/immagini o un fotogramma del video tagliato,
    ritagliato attorno alla faccia. Ritorna il nome del file in assets, o None."""
    dest = os.path.join(r.assets, nome)
    if immagine:
        src = os.path.join(DATI, "immagini", immagine)
        if not os.path.exists(src):
            return None
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-vf", vf, "-q:v", "3", dest], capture_output=True)
    else:
        lato = 900
        cy = (faccia["occhi"] + faccia["mento"]) / 2 if faccia else 900
        y0 = int(max(0, min(cy - lato * 0.45, 1920 - lato)))
        x0 = int(max(0, min(_cx(faccia) - lato / 2, 1080 - lato))) if faccia else 90
        alto = int(lato * h / w)
        vf = f"crop={lato}:{alto}:{x0}:{y0},scale={w}:{h}"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(secondo or 0, 0):.2f}", "-i",
                        os.path.join(r.assets, "tagliato.mp4"), "-frames:v", "1", "-vf", vf, "-q:v", "3", dest], capture_output=True)
    return nome if os.path.exists(dest) else None


# ---------------------------------------------------------------- scritta che si cancella
def cancella(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    testo = e.get("testo", "")
    td = e.get("testo_da", da)
    via = e.get("via", a - 0.9)
    dim = max(min(150, int(1000 / (max(len(testo), 3) * 0.4))), 70)
    y = max(_cima(faccia) - dim * 1.05, 210)
    lettere = [c for c in testo]
    spans = "".join(f'<span id="ec{n}l{k}">{"&nbsp;" if c == " " else E(c)}</span>' for k, c in enumerate(lettere))
    sposta = max(min(_cx(faccia) - 540, 120), -120)   # centrata sulla persona, non sul telefono
    r.corpo.append(f'<div class="ec-riga ec-ombra" id="ec{n}" style="top:{y:.0f}px;transform:translateX({sposta:.0f}px);font-family:ISerifI;font-size:{dim}px;'
                   f'color:{r.stile["colori"].get("testo", "#fff")}"><span style="position:relative;opacity:1">{spans}'
                   f'<i class="ec-luce" id="ec{n}p" style="left:-120px"></i></span></div>')
    T = r.tl.append
    passo = min(0.06, 0.9 / max(len(lettere), 1))
    via = min(max(via, td + passo * len(lettere) + 0.35), a - 0.75)   # prima si legge tutta, poi si cancella
    for k in range(len(lettere)):
        T(f'tl.fromTo("#ec{n}l{k}",{{opacity:0,y:10,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.22,'
          f'ease:"power2.out",immediateRender:false}},{td + k * passo:.3f});')
    durata_via = 0.6
    T(f'tl.fromTo("#ec{n}p",{{opacity:0,left:-120}},{{opacity:1,duration:.08,immediateRender:false}},{via:.3f});'
      f'tl.to("#ec{n}p",{{left:"100%",duration:{durata_via},ease:"none"}},{via:.3f});'
      f'tl.to("#ec{n}p",{{opacity:0,duration:.12}},{via + durata_via:.3f});')
    for k in range(len(lettere)):
        T(f'tl.to("#ec{n}l{k}",{{opacity:0,x:18,filter:"blur(8px)",duration:.18}},{via + 0.05 + durata_via * k / max(len(lettere), 1):.3f});')
    T(f'tl.set("#ec{n}",{{opacity:0}},{a:.3f});')
    r.suono_libreria("hyperframes/sparkle.mp3", td, 0.22)
    r.suono_libreria("hyperframes/whoosh-short.mp3", via, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- lettere che cadono
def lettere(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    testo = e.get("testo", "").upper()[:12]
    sotto = e.get("sotto", "")
    c = r.stile["colori"]
    dim = max(min(190, int(940 / (max(len(testo), 3) * 0.66))), 90)
    y = max(_cima(faccia) - dim * 1.25 - (40 if sotto else 0), 200)
    rnd = random.Random(len(testo) * 7 + 3)
    spans = "".join(f'<span id="el{n}l{k}">{"&nbsp;" if ch == " " else E(ch)}</span>' for k, ch in enumerate(testo))
    acc = c.get("accento_luce", "#FFB27A")   # il colore chiaro: quello pieno sparisce su sfondi caldi
    r.corpo.append(f'<div class="ec-riga ec-ombra" style="top:{y:.0f}px;font-family:\'Inter Tight\';font-weight:900;font-size:{dim}px;'
                   f'letter-spacing:-.02em;color:{c.get("testo", "#fff")}" id="el{n}">{spans}</div>')
    if sotto:
        ds = max(min(78, int(920 / (max(len(sotto), 3) * 0.47))), 48)
        r.corpo.append(f'<div class="ec-riga ec-ombra" id="el{n}s" style="top:{y + dim * 0.98:.0f}px;font-family:PlayI;font-weight:700;'
                       f'font-size:{ds}px;color:{acc};clip-path:inset(-30% 100% -30% 0)">{E(sotto)}</div>')
    T = r.tl.append
    for k in range(len(testo)):
        t = da + 0.05 + k * 0.08
        T(f'tl.fromTo("#el{n}l{k}",{{opacity:0,y:-260,rotation:{rnd.choice([-1, 1]) * rnd.uniform(7, 15):.0f}}},'
          f'{{opacity:1,y:0,rotation:0,duration:.6,ease:"bounce.out",immediateRender:false}},{t:.3f});')
        if k % 2 == 0:
            r.suono_libreria("hyperframes/click-soft.mp3", t + 0.28, 0.25)
    fine = da + 0.05 + len(testo) * 0.08 + 0.4
    if sotto:
        ts = e.get("sotto_da", fine)
        T(f'tl.fromTo("#el{n}s",{{clipPath:"inset(-30% 100% -30% 0%)"}},{{clipPath:"inset(-30% 0% -30% 0%)",duration:.55,'
          f'ease:"power1.inOut",immediateRender:false}},{ts:.3f});')
        r.suono_libreria("hyperframes/whoosh-short.mp3", ts, 0.18)
    T(f'tl.to(["#el{n}","#el{n}s"],{{opacity:0,y:-30,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- carte a ventaglio
def ventaglio(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    carte = []
    for x in e.get("carte", [])[:5]:
        if isinstance(x, dict):
            carte.append(x)
        else:
            carte.append({"testo": x[0], "t": x[1]})
    q = len(carte)
    if not q:
        return
    passo = {1: 0, 2: 34, 3: 30, 4: 25, 5: 21}[q]
    angoli = [(k - (q - 1) / 2) * passo for k in range(q)]
    W, H = 250, 340
    raggio = 520
    py = 1880
    tinte = [(c.get("accento", "#E86530"), "#fff"), ("#FBF8F2", c.get("scuro", "#141414")),
             (c.get("scuro", "#141414"), c.get("testo", "#fff")), (c.get("accento_luce", "#FFB27A"), c.get("scuro", "#141414"))]
    pezzi = []
    for k, ct in enumerate(carte):
        fondo, inchiostro = tinte[k % len(tinte)]
        dentro = ""
        if ct.get("immagine") or ct.get("secondo") is not None:
            f = _foto(r, f"vent-{n}-{k}.jpg", ct.get("secondo"), ct.get("immagine"), W, H, faccia)
            if f:
                dentro = f'<img src="assets/{f}">'
        testo = ct.get("testo", "")
        if testo:
            dim = max(min(58, int(205 / (max(max(len(p) for p in testo.split()), 3) * 0.63))), 30)
            if dentro:
                dentro += (f'<b style="position:absolute;left:12px;right:12px;bottom:14px;background:{fondo};color:{inchiostro};'
                           f'border-radius:12px;padding:8px 6px;font-size:{min(dim, 40)}px">{E(testo)}</b>')
            else:
                dentro = f'<span style="font-size:{dim}px">{E(testo)}</span><em>{k + 1}</em>'
        pezzi.append(f'<div class="ec-perno" style="left:540px;top:{py}px"><div id="ev{n}c{k}" style="position:absolute;left:0;top:0">'
                     f'<div class="ec-carta" id="ev{n}k{k}" style="left:{-W / 2:.0f}px;top:{-raggio - H / 2:.0f}px;width:{W}px;height:{H}px;'
                     f'background:{fondo};color:{inchiostro}">{dentro}</div></div></div>')
    r.corpo.append(f'<div id="ev{n}">{"".join(pezzi)}</div>')
    T = r.tl.append
    chiudi = e.get("chiudi", a - 0.5)
    for k, ct in enumerate(carte):
        t = max(ct.get("t", da + k * 0.25), da)
        T(f'tl.set("#ev{n}c{k}",{{transformOrigin:"0px 0px"}},{da:.3f});'
          f'tl.fromTo("#ev{n}k{k}",{{opacity:0}},{{opacity:1,duration:.15,immediateRender:false}},{t:.3f});'
          f'tl.fromTo("#ev{n}c{k}",{{rotation:0,y:420}},{{rotation:{angoli[k]:.1f},y:0,duration:.5,ease:"back.out(1.5)",immediateRender:false}},{t:.3f});')
        r.suono_libreria("hyperframes/whoosh-short.mp3", t, 0.2)
        r.suono("pop", t + 0.25, 0.18)
    T(f'tl.to("[id^=ev{n}c]",{{rotation:0,duration:.25,ease:"power2.in"}},{chiudi:.3f});'
      f'tl.to("[id^=ev{n}c]",{{y:520,duration:.3,ease:"power2.in"}},{chiudi + 0.22:.3f});'
      f'tl.set("#ev{n}",{{opacity:0}},{a:.3f});')
    r.suono_libreria("hyperframes/whoosh-short.mp3", chiudi, 0.22)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- polaroid
def polaroid(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    foto = []
    for x in e.get("foto", [])[:4]:
        if isinstance(x, dict):
            foto.append(x)
        else:
            foto.append({"testo": x[0], "t": x[1], "secondo": x[2] if len(x) > 2 else None})
    if not foto:
        return
    W, F = 270, 238
    H = 16 + F + 64
    alto, basso = max(_cima(faccia) + 120, 420), min(faccia["mento"] + 60, 1280)
    posti = [(150, alto, -8), (930, alto - 40, 7), (155, basso, 6), (925, basso - 30, -6)]
    rnd = random.Random(n)
    pezzi = []
    for k, ft in enumerate(foto):
        sec = ft.get("secondo")
        if sec is None and not ft.get("immagine"):
            sec = rnd.uniform(0.2, max(r.D - 0.5, 0.3))
        f = _foto(r, f"pol-{n}-{k}.jpg", sec, ft.get("immagine"), F, F, faccia)
        x, y, gira = posti[k]
        img = f'<img src="assets/{f}" style="width:{F}px;height:{F}px">' if f else f'<i style="display:block;width:{F}px;height:{F}px;background:#ccc"></i>'
        pezzi.append(f'<div class="ec-pol" id="ep{n}k{k}" style="left:{x - W / 2:.0f}px;top:{y - H / 2:.0f}px;width:{W}px;height:{H}px">'
                     f'{img}<div>{E(ft.get("testo", ""))}</div></div>')
        posti[k] = (x, y, gira)
    r.corpo.append(f'<div id="ep{n}">{"".join(pezzi)}</div>')
    T = r.tl.append
    for k, ft in enumerate(foto):
        t = max(ft.get("t", da + k * 0.3), da)
        gira = posti[k][2]
        lato = -1 if posti[k][0] < 540 else 1
        T(f'tl.fromTo("#ep{n}k{k}",{{opacity:0,x:{lato * 60},y:-620,rotation:{gira + lato * 22},scale:1.25}},'
          f'{{opacity:1,x:0,y:0,rotation:{gira},scale:1,duration:.5,ease:"back.out(1.3)",immediateRender:false}},{t:.3f});')
        r.suono_libreria("hyperframes/whoosh-short.mp3", max(t - 0.05, 0), 0.15)
        r.suono_libreria("hyperframes/click-soft.mp3", t + 0.3, 0.35)
    T(f'tl.to("[id^=ep{n}k]",{{opacity:0,scale:.85,duration:.3,stagger:.05}},{a - 0.4:.3f});'
      f'tl.set("#ep{n}",{{opacity:0}},{a:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- messaggio vocale
def vocale(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    acc = c.get("accento", "#E86530")
    W = 780
    y = min(faccia["mento"] + 200, 1330)
    rnd = random.Random(9)
    altezze = [int(14 + 58 * abs(rnd.gauss(0.45, 0.28))) for _ in range(34)]
    altezze = [min(h, 72) for h in altezze]
    barre = lambda col: "".join(f'<i style="height:{h}px;background:{col}"></i>' for h in altezze)
    gioca = (f'<svg id="ew{n}g" width="38" height="42" viewBox="0 0 38 42" style="position:absolute;left:28px;top:22px">'
             f'<path d="M4 3 L35 21 L4 39 Z" fill="#fff"/></svg>'
             f'<svg id="ew{n}f" width="36" height="40" viewBox="0 0 36 40" style="position:absolute;left:25px;top:23px;opacity:0">'
             f'<rect x="3" y="2" width="10" height="36" rx="3" fill="#fff"/><rect x="23" y="2" width="10" height="36" rx="3" fill="#fff"/></svg>')
    suona_da, suona_a = da + 0.55, a - 0.45
    secondi = max(int(round(suona_a - suona_da)), 1)
    ore = "".join(f'<span id="ew{n}o{s}" style="{"" if s == 0 else "display:none"}">0:{s:02d}</span>' for s in range(secondi + 1))
    sopra = f'<div class="sopra">{E(e["testo"].upper())}</div>' if e.get("testo") else ""
    r.corpo.append(f'<div class="ec-voc" id="ew{n}" style="left:{540 - W / 2:.0f}px;top:{y:.0f}px;width:{W}px">{sopra}'
                   f'<div class="bolla"><span class="tasto" style="background:{acc}">{gioca}</span>'
                   f'<div class="onda"><div>{barre("#CFCFD6")}</div><div id="ew{n}c" style="clip-path:inset(0 100% 0 0)">{barre(acc)}</div></div>'
                   f'<span class="ora">{ore}</span></div></div>')
    T = r.tl.append
    T(f'tl.fromTo("#ew{n}",{{opacity:0,y:60,scale:.9}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.8)",immediateRender:false}},{da:.3f});'
      f'tl.set("#ew{n}g",{{opacity:0}},{suona_da:.3f});tl.set("#ew{n}f",{{opacity:1}},{suona_da:.3f});'
      f'tl.fromTo("#ew{n} .tasto",{{scale:1}},{{scale:.86,duration:.08,yoyo:true,repeat:1,immediateRender:false}},{suona_da - 0.08:.3f});'
      f'tl.fromTo("#ew{n}c",{{clipPath:"inset(0% 100% 0% 0%)"}},{{clipPath:"inset(0% 0% 0% 0%)",duration:{suona_a - suona_da:.2f},'
      f'ease:"none",immediateRender:false}},{suona_da:.3f});'
      f'tl.set("#ew{n}g",{{opacity:1}},{suona_a:.3f});tl.set("#ew{n}f",{{opacity:0}},{suona_a:.3f});')
    for s in range(1, secondi + 1):
        t = min(suona_da + s, suona_a)
        T(f'tl.set("#ew{n}o{s - 1}",{{display:"none"}},{t:.3f});tl.set("#ew{n}o{s}",{{display:"inline"}},{t:.3f});')
    T(f'tl.to("#ew{n}",{{opacity:0,y:40,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    r.suono("pop", da, 0.25)
    r.suono_libreria("hyperframes/click-soft.mp3", suona_da - 0.05, 0.4)
    r.nascondi.append((da, a))


TIPI = {"cancella": cancella, "lettere": lettere, "ventaglio": ventaglio, "polaroid": polaroid, "vocale": vocale}
