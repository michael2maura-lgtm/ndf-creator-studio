"""Grafiche del modello "Energia" (15/11/2026): tutto il testo sta SOPRA la testa. Rifatte da noi guardando un reel
che piace a Michael (mai copiate): una riga piccola con quello che dici (i sottotitoli, stile.json "sott_sopra": true)
e sotto, sulle parole importanti, il pezzo forte. Due colori che si alternano: colore del brand e "accento2".

Nel piano (tempi del video TAGLIATO):
 {"tipo": "forte", "da", "a", "sopra": "io mi sono", "testo": "STUFATA", "modo": "gigante" | "targa", "colore": 1 | 2}
     "sopra" = le parole dette appena prima, in una riga piccola sopra. La parola gigante passa dietro la testa
     (ritaglio, lento: ~30 s per secondo; "dietro": false per tenerla davanti).
 {"tipo": "numeri", "da" (= la prima voce), "a", "voci": [["cosa tagliare", t, "✂️"], ["cosa dire", t, "⏱️"]]}
     passi numerati in alto: 1, 2, 3 grandi a colori alternati, la frase e un'icona; ogni voce al secondo in cui la dici.
     gigante = parola enorme bianca; targa = riga su una targa inclinata colorata. I sottotitoli continuano sopra.
 {"tipo": "pila", "a", "voci": [["programmi", t], ["montatore", t]], "finale": ["STRESS", t]}
     le parole entrano una sotto l'altra mentre le dici, colori alternati; l'ultima su una targa. Sotto, un velo scuro.
 {"tipo": "schermata", "da", "a", "testo": "NO", "sotto": "la riga piccola", "colore": 1 | 2}
     schermo pieno di colore con la parola enorme: per una frase secca. Dura poco (0,6-1,5 s).
 {"tipo": "fondo", "da", "a", "sfondo": "blu" | "brand" | "carta" | "scuro"}
     la persona staccata dallo sfondo (ritaglio.py, lento: mezzo minuto per secondo), più piccola in basso con un
     bordino bianco, davanti a un fondo nuovo; sopra resta mezzo schermo libero per le scritte (forte, pila).
     Su "carta" (chiaro) usa solo targhe, non parole giganti bianche.
 {"tipo": "icona", "da", "a", "icona": "orologio" | "x" | "spunta" | "soldi" | "cuore" | "fulmine", "lato": "destra" | "sinistra"}
 {"tipo": "icona", "da", "a", "emoji": "🏠"}     la riserva quando non c'è un disegno animato adatto: un'emoji che salta fuori
     un disegno animato accanto alla testa che fa vedere la parola detta: l'orologio con le lancette che girano
     ("5 minuti", "tre ore"), la X rossa che si disegna ("non serve", "niente"), la spunta ("fatto"), i soldi che
     cadono, il cuore che batte, il fulmine. Il format vive di queste trovate: una ogni 4-6 secondi.
"""
import html

E = html.escape


def _colori(r):
    c = r.stile["colori"]
    return c["accento"], c.get("accento2", "#2F7DF6")


def _css(r):
    if getattr(r, "css_sopra", False):
        return
    r.css_sopra = True
    ft = r.stile["font"]["titoli"]
    fam = f"font-family:'{ft['famiglia']}';font-weight:{ft.get('peso', 900)};font-stretch:{ft.get('larghezza', 100)}%"
    r.font_extra("PlusJakartaSans.ttf")
    r.corpo.append(
        "<style>@font-face{font-family:'Plus Jakarta Sans';src:url('assets/PlusJakartaSans.ttf');font-weight:200 800}"
        ".es-riga{position:absolute;left:60px;right:60px;text-align:center;z-index:31;opacity:0;font-family:'Plus Jakarta Sans',sans-serif;"
        "font-weight:600;font-size:46px;line-height:1.2;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.8)}"
        ".es-n{position:absolute;left:70px;right:60px;z-index:31}"
        f".es-n .r{{display:flex;align-items:center;gap:26px;height:118px;opacity:0}}.es-n b{{{fam};font-size:118px;line-height:1;width:80px;text-align:center}}"
        ".es-n span{flex:1;font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:44px;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.8)}"
        ".es-n img{width:74px;height:74px;object-fit:contain}"
        f".es-f{{position:absolute;left:60px;right:60px;text-align:center;z-index:31;opacity:0;{fam};color:#fff;line-height:1}}"
        ".es-g{white-space:nowrap;letter-spacing:-2px;text-transform:uppercase;text-shadow:0 8px 30px rgba(0,0,0,.55)}"
        ".es-t span{display:inline-block;white-space:nowrap;padding:12px 30px 16px;transform:rotate(-3deg) skewX(-6deg);"
        "border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.35)}"
        ".es-velo{position:absolute;left:0;right:0;top:0;height:1150px;z-index:29;opacity:0;"
        "background:linear-gradient(rgba(10,10,14,.88) 0%,rgba(10,10,14,.75) 60%,rgba(10,10,14,0) 100%)}"
        f".es-p{{position:absolute;left:60px;right:60px;text-align:center;z-index:31;{fam};line-height:1.05}}"
        ".es-p div{font-size:84px;opacity:0;text-transform:lowercase;text-shadow:0 4px 22px rgba(0,0,0,.75),0 1px 3px rgba(0,0,0,.6)}"
        ".es-p .es-t{margin-top:16px}"
        ".es-s{position:absolute;inset:0;z-index:40;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center}"
        f".es-s b{{{fam};white-space:nowrap;color:#fff;line-height:1;letter-spacing:-6px;text-transform:uppercase}}"
        ".es-s i{font-style:normal;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:46px;color:#fff;margin-top:30px}"
        "</style>")


def _misura(testo, largo, massimo, r=None):
    """Grandezza del carattere perché il testo stia in una riga larga `largo` px (Archivo larga: ~0,78 em a lettera).
    Con `r`, tiene conto della grandezza dei titoli scelta nella pagina (70-140%), sempre dentro la riga."""
    g = 1.0
    if r is not None:
        g = max(70, min(140, int((r.stile.get("ritocchi_titoli") or {}).get("grandezza") or 100))) / 100
    lettera = 0.78 if r is None or r.stile["font"]["titoli"].get("larghezza", 100) > 100 else 0.64
    return int(max(40, min(massimo * g, largo / (max(len(testo), 1) * lettera))))


def _y(r):
    return max(getattr(r, "y_sub", 300) - 70, 330 if r.stile.get("testo_fisso") else 240)   # sotto il testo fisso, se c'è   # al posto della riga dei sottotitoli (che si toglie): ben sopra la testa (Michael)


def forte(r, e, faccia):
    """La riga piccola con le parole dette prima ("io mi sono") e sotto il pezzo forte: la parola gigante che passa
    DIETRO la testa (ritaglio della persona) o la targa inclinata davanti."""
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    c1, c2 = _colori(r)
    col = c2 if e.get("colore") == 2 else c1
    riga = e.get("sopra", "")
    y = _y(r)
    if e.get("modo") == "targa":
        if riga:
            r.corpo.append(f'<div class="es-riga" id="ef{n}r" style="top:{y}px">{E(riga)}</div>')
        r.corpo.append(f'<div class="es-f es-t" id="ef{n}" style="top:{y + (66 if riga else 0)}px"><span style="background:{col};font-size:{_misura(e["testo"], 860, 74, r)}px">{E(e["testo"])}</span></div>')
        r.tl.append(f'tl.fromTo("#ef{n}",{{opacity:0,clipPath:"inset(0 100% 0 0)"}},{{opacity:1,clipPath:"inset(0 0% 0 0)",duration:.3,ease:"power3.out",immediateRender:false}},{da:.3f});')
        r.suono("pop", da, 0.25)
        r.tl.append(f'tl.to("#ef{n}",{{opacity:0,y:-20,duration:.2}},{a - 0.2:.3f});')
    else:
        dim = _misura(e["testo"], 920, 170, r)
        dietro = e.get("dietro", True) and not any(x <= da < z for x, z in getattr(r, "su_fondo", []))
        if dietro:   # la parola sta tra il video e la persona ritagliata: la testa la copre in basso
            sel = r.ritaglio(da - 0.1, a + 0.1)
            cima = r.cima_testa(r.ultimo_ritaglio, 0.2) or faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
            yp = int(max(cima - dim * 0.62, y + (60 if riga else 0)))
            r.camera.insert(0, f'<div class="es-f es-g" id="ef{n}" style="top:{yp}px;font-size:{dim}px;z-index:2">{E(e["testo"])}</div>')
            r.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});')
        else:
            yp = y + (60 if riga else 0)
            r.corpo.append(f'<div class="es-f es-g" id="ef{n}" style="top:{yp}px;font-size:{dim}px">{E(e["testo"])}</div>')
        if riga:
            r.corpo.append(f'<div class="es-riga" id="ef{n}r" style="top:{yp - 66}px">{E(riga)}</div>')
        r.tl.append(f'tl.fromTo("#ef{n}",{{opacity:0,scale:1.5}},{{opacity:1,scale:1,duration:.22,ease:"power4.out",immediateRender:false}},{da:.3f});'
                    f'tl.set("#ef{n}",{{opacity:0}},{a:.3f});')
        r.suono("impatto", da, 0.3)
    if riga:
        r.tl.append(f'tl.set("#ef{n}r",{{opacity:1}},{da - 0.05:.3f});tl.set("#ef{n}r",{{opacity:0}},{a:.3f});')
    r.nascondi.append((da, a))   # al posto dei sottotitoli: la riga piccola e il pezzo forte


def numeri(r, e, faccia):
    """Passi numerati in alto: numeri grandi a colori alternati, la frase e una piccola icona; restano fino ad "a"."""
    _css(r)
    n, a = len(r.corpo), e["a"]
    c1, c2 = _colori(r)
    righe = []
    for j, v in enumerate(e["voci"]):
        testo, t = v[0], v[1]
        ic = _emoji_png(r, v[2]) if len(v) > 2 and v[2] else None
        righe.append(f'<div class="r" id="en{n}v{j}"><b style="color:{c1 if j % 2 == 0 else c2}">{j + 1}</b><span>{E(testo)}</span>'
                     + (f'<img src="assets/{ic}">' if ic else "") + "</div>")
        r.tl.append(f'tl.fromTo("#en{n}v{j}",{{opacity:0,x:-60}},{{opacity:1,x:0,duration:.3,ease:"back.out(1.8)",immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.25)
    da = e["voci"][0][1]
    su_fondo = any(x <= da < z for x, z in getattr(r, "su_fondo", []))
    # come nel riferimento i passi stanno su uno sfondo nuovo (fondo), con la persona in basso; senza fondo, un velo scuro
    velo = "" if su_fondo else f'<div class="es-velo" id="en{n}velo" style="opacity:1"></div>'
    r.corpo.append(f'{velo}<div class="es-n" id="en{n}" style="top:{_y(r)}px">{"".join(righe)}</div>')
    if velo:
        r.tl.append(f'tl.fromTo("#en{n}velo",{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{da - 0.1:.3f});tl.set("#en{n}velo",{{opacity:0}},{a:.3f});')
    r.tl.append(f'tl.to("#en{n}",{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    r.nascondi.append((e["voci"][0][1], a))


def pila(r, e, faccia):
    _css(r)
    n = len(r.corpo)
    c1, c2 = _colori(r)
    voci = e["voci"]
    da = voci[0][1] - 0.1
    a = e["a"]
    righe = []
    y0 = max(getattr(r, "y_sub", 300) - 40, 330 if r.stile.get("testo_fisso") else 260)
    targa = c1
    if hasattr(r, "si_confonde"):   # un colore che sparisce sul vestito (arancio su felpa rossa) diventa crema
        c1 = "#FFE9C7" if r.si_confonde(c1, da, y0, 300) else c1
        c2 = "#FFE9C7" if r.si_confonde(c2, da, y0, 300) else c2
    for j, (testo, _) in enumerate(voci):
        col = "#fff" if j % 2 == 0 else (c1 if j % 4 == 1 else c2)
        righe.append(f'<div id="ep{n}v{j}" style="color:{col}">{E(testo)}</div>')
    if e.get("finale"):
        righe.append(f'<div class="es-t" id="ep{n}f"><span style="background:{targa};font-size:{_misura(e["finale"][0], 860, 74, r)}px">{E(e["finale"][0])}</span></div>')
    su_fondo = any(x <= da < z for x, z in getattr(r, "su_fondo", []))   # sul fondo nuovo il velo scuro non serve
    r.corpo.append(f'<div class="es-velo" id="ep{n}velo"{' style="display:none"' if su_fondo else ''}></div><div class="es-p" id="ep{n}" style="top:{max(getattr(r, "y_sub", 300) - 40, 330 if r.stile.get("testo_fisso") else 260)}px">{"".join(righe)}</div>')
    r.tl.append(f'tl.to("#ep{n}velo",{{opacity:1,duration:.25}},{da:.3f});')
    for j, (_, t) in enumerate(voci):
        r.tl.append(f'tl.fromTo("#ep{n}v{j}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.22,ease:"back.out(2)",immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.22)
    if e.get("finale"):
        t = e["finale"][1]
        r.tl.append(f'tl.fromTo("#ep{n}f",{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:.25,ease:"back.out(2)",immediateRender:false}},{t:.3f});')
        r.suono("impatto", t, 0.3)
    r.tl.append(f'tl.to(["#ep{n}","#ep{n}velo"],{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    r.nascondi.append((da, a))


def schermata(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    c1, c2 = _colori(r)
    col = c2 if e.get("colore") == 2 else c1
    r.corpo.append(f'<div class="es-s" id="es{n}" style="background:{col}">'
                   f'<b style="font-size:{_misura(e["testo"], 940, 260, r)}px">{E(e["testo"])}</b>' + (f'<i>{E(e["sotto"])}</i>' if e.get("sotto") else "") + '</div>')
    r.tl.append(f'tl.set("#es{n}",{{opacity:1}},{da:.3f});tl.fromTo("#es{n} b",{{scale:1.25}},{{scale:1,duration:.3,ease:"power3.out",immediateRender:false}},{da:.3f});'
                f'tl.set("#es{n}",{{opacity:0}},{a:.3f});')
    r.suono("impatto", da, 0.35)
    r.nascondi.append((da, a))


FONDI = {
    "blu": lambda c1, c2: f"linear-gradient(170deg,{c2} 0%,#5B3FB8 55%,#7A2E7E 100%)",
    "brand": lambda c1, c2: f"radial-gradient(ellipse 120% 80% at 50% 22%,{c1} 0%,{c1} 30%,#120A06 100%)",   # il colore che sfuma nel nero (Michael)
    "carta": lambda c1, c2: "radial-gradient(ellipse at 40% 30%,#FFFFFF 0%,#EFEDE8 60%,#E2DFD8 100%)",
    "scuro": lambda c1, c2: "radial-gradient(ellipse at 50% 30%,#3A1F33 0%,#1E1420 60%,#120C14 100%)",
}


def fondo(r, e, faccia):
    """Un fondo nuovo dietro la persona staccata, rimpicciolita in basso con il bordino bianco."""
    import ritaglio as rit
    import os
    import shutil
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    c1, c2 = _colori(r)
    p = rit.ritaglia(os.path.dirname(r.reel), da, a, f"fondo-{da:.2f}-{a:.2f}", duro=True)
    dest = os.path.join(r.assets, os.path.basename(p))
    if not os.path.exists(dest):
        shutil.copy2(p, dest)
    sf = FONDI.get(e.get("sfondo", "blu"), FONDI["blu"])(c1, c2)
    bordo = "".join(f"drop-shadow({x}px {y}px 0 #fff) " for x, y in ((5, 0), (-5, 0), (0, 5), (0, -5))) + "drop-shadow(0 18px 30px rgba(0,0,0,.35))"
    # rimpicciolita del 30% dal fondo dello schermo: la testa scende a metà, sopra c'è posto per le scritte
    r.corpo.append(f'<div class="es-fondo" id="eo{n}" style="position:absolute;inset:0;z-index:28;opacity:0;background:{sf}"></div>'
                   f'<video id="eo{n}v" src="assets/{os.path.basename(p)}" muted playsinline data-start="{da:.3f}" data-media-start="0" '
                   f'data-duration="{a - da:.3f}" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:28;opacity:0;'
                   f'transform-origin:50% 100%;filter:{bordo}"></video>')
    # tutto il movimento con GSAP (un transform nel CSS lo cancellerebbe): il taglio sotto il petto esce dallo schermo
    r.tl.append(f'tl.set(["#eo{n}","#eo{n}v"],{{opacity:1}},{da:.3f});'
                f'tl.fromTo("#eo{n}v",{{scale:.72,y:400}},{{scale:.72,y:280,duration:.35,ease:"power3.out",immediateRender:false}},{da:.3f});'
                f'tl.set(["#eo{n}","#eo{n}v"],{{opacity:0}},{a:.3f});')
    r.suono("pop", da, 0.25)
    r.su_fondo = getattr(r, "su_fondo", []) + [(da, a)]


def _noto3d(emoji, dest):
    """L'emoji Noto 3D di Google (licenza Apache 2.0, nessuna citazione): scaricata una volta in DATI/emoji/noto3d.
    True se c'è. Si usa dove non ci sono le emoji di Apple (Windows): così sono uguali per tutti, non quelle di Microsoft."""
    import os
    import shutil
    import urllib.request
    from comune import DATI
    codici = "_".join(f"{ord(c):x}" for c in emoji if ord(c) != 0xFE0F)
    cache = os.path.join(DATI, "emoji", "noto3d", f"emoji_u{codici}.png")
    if not os.path.exists(cache):
        try:
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            url = f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/3D/png/512/emoji_u{codici}.png"
            with urllib.request.urlopen(url, timeout=30) as risposta, open(cache + ".tmp", "wb") as f:
                shutil.copyfileobj(risposta, f)
            os.replace(cache + ".tmp", cache)
        except Exception:
            return False
    from PIL import Image
    im = Image.open(cache).convert("RGBA")
    im.crop(im.getbbox()).save(dest)
    return True


def _emoji_png(r, emoji):
    """L'emoji disegnata una volta come immagine (come lettera nella pagina rallenta il montaggio e blocca le foto).
    Mac: Apple Color Emoji (le più belle, scelta di Michael 25/11/2026); altrove: Noto 3D di Google; ultima riserva
    Segoe UI Emoji di Windows. None se non si riesce a disegnarla."""
    import os
    from PIL import Image, ImageDraw, ImageFont
    nome = "emoji-" + "-".join(f"{ord(c):x}" for c in emoji) + ".png"
    dest = os.path.join(r.assets, nome)
    if os.path.exists(dest):
        return nome
    if not os.path.exists("/System/Library/Fonts/Apple Color Emoji.ttc") and _noto3d(emoji, dest):
        return nome
    for font, misura in (("/System/Library/Fonts/Apple Color Emoji.ttc", 160), ("C:/Windows/Fonts/seguiemj.ttf", 160)):
        if not os.path.exists(font):
            continue
        try:
            f = ImageFont.truetype(font, misura)
            im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((110, 110), emoji, font=f, embedded_color=True, anchor="mm")
            if im.getbbox():
                im.crop(im.getbbox()).save(dest)
                return nome
        except Exception:
            continue
    return None


_TRATTO = 'fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"'


def icona(r, e, faccia):
    """Disegni animati fatti da noi: ogni icona ha il suo movimento e il suo suono."""
    n, da, a = len(r.corpo), e["da"], e["a"]
    c1, c2 = _colori(r)
    su_fondo = any(x <= da < z for x, z in getattr(r, "su_fondo", []))
    y = 640 if su_fondo else int(max(faccia["occhi"] - 120, 430))
    x = 50 if e.get("lato") == "sinistra" else 740
    if e.get("emoji"):   # la riserva: qualsiasi cosa si dica c'è un'emoji; salta fuori, rimbalza e oscilla piano
        nome = _emoji_png(r, e["emoji"])
        if not nome:
            print(f'NOTA: non riesco a disegnare l\'emoji {e["emoji"]} su questo computer, la salto')
            return
        r.corpo.append(f'<img id="ei{n}" src="assets/{nome}" style="position:absolute;left:{x}px;top:{y}px;width:290px;height:290px;'
                       f'z-index:32;opacity:0;object-fit:contain;filter:drop-shadow(0 10px 22px rgba(0,0,0,.45))">')
        r.tl.append(f'tl.fromTo("#ei{n}",{{opacity:0,scale:.2,rotation:-30,y:60}},{{opacity:1,scale:1,rotation:0,y:0,duration:.45,ease:"back.out(2.6)",immediateRender:false}},{da:.3f});'
                    f'tl.to("#ei{n}",{{rotation:8,duration:.35,repeat:{max(int((a - da - 0.6) / 0.35), 1)},yoyo:true,ease:"sine.inOut"}},{da + 0.45:.3f});'
                    f'tl.to("#ei{n}",{{opacity:0,scale:.5,duration:.2}},{a - 0.2:.3f});')
        r.suono("pop", da, 0.25)
        return
    k = e.get("icona", "spunta")
    ombra = "filter:drop-shadow(0 10px 22px rgba(0,0,0,.45))"
    if k == "orologio":
        svg = (f'<circle cx="100" cy="100" r="84" fill="{c2}" stroke="#fff" stroke-width="10"/>'
               + "".join(f'<path d="M100 26v14" stroke="#fff" stroke-width="7" stroke-linecap="round" transform="rotate({g} 100 100)"/>' for g in range(0, 360, 30))
               + f'<path id="ei{n}m" d="M100 100V44" stroke="#fff" stroke-width="9" stroke-linecap="round"/>'
               + f'<path id="ei{n}h" d="M100 100h34" stroke="#fff" stroke-width="11" stroke-linecap="round"/><circle cx="100" cy="100" r="9" fill="#fff"/>')
        mov = (f'tl.fromTo("#ei{n}m",{{rotation:0}},{{rotation:1080,svgOrigin:"100 100",duration:{a - da:.2f},ease:"power2.out",immediateRender:false}},{da:.3f});'
               f'tl.fromTo("#ei{n}h",{{rotation:0}},{{rotation:90,svgOrigin:"100 100",duration:{a - da:.2f},ease:"power2.out",immediateRender:false}},{da:.3f});')
        suono = ("click", 0.2)   # un clic breve: la tastiera copriva la voce (Michael)
    elif k == "x":
        svg = (f'<circle cx="100" cy="100" r="84" fill="#E5322D" stroke="#fff" stroke-width="10"/>'
               f'<path id="ei{n}a" d="M66 66L134 134" {_TRATTO} stroke-width="20" stroke-dasharray="100" stroke-dashoffset="100"/>'
               f'<path id="ei{n}b" d="M134 66L66 134" {_TRATTO} stroke-width="20" stroke-dasharray="100" stroke-dashoffset="100"/>')
        mov = (f'tl.to("#ei{n}a",{{strokeDashoffset:0,duration:.15}},{da + 0.15:.3f});tl.to("#ei{n}b",{{strokeDashoffset:0,duration:.15}},{da + 0.3:.3f});'
               f'tl.fromTo("#ei{n}",{{x:0}},{{keyframes:[{{x:-14,duration:.05}},{{x:14,duration:.05}},{{x:-8,duration:.05}},{{x:0,duration:.05}}],immediateRender:false}},{da + 0.45:.3f});')
        suono = ("glitch", 0.3)
    elif k == "soldi":
        svg = "".join(f'<g id="ei{n}s{j}"><rect x="{30 + j * 22}" y="40" width="96" height="54" rx="8" fill="#2E9E5B" stroke="#fff" stroke-width="6"/>'
                      f'<circle cx="{78 + j * 22}" cy="67" r="13" fill="none" stroke="#fff" stroke-width="5"/></g>' for j in range(3))
        mov = "".join(f'tl.fromTo("#ei{n}s{j}",{{y:-160,rotation:{-20 + j * 20},opacity:0}},{{y:{j * 30},rotation:{-8 + j * 8},opacity:1,duration:.4,ease:"bounce.out",immediateRender:false}},{da + j * 0.15:.3f});' for j in range(3))
        suono = ("ding", 0.25)
    elif k == "cuore":
        svg = f'<path id="ei{n}c" d="M100 170C40 125 20 95 20 65a40 40 0 0 1 80-8a40 40 0 0 1 80 8c0 30-20 60-80 105z" fill="#E5322D" stroke="#fff" stroke-width="9"/>'
        mov = f'tl.fromTo("#ei{n}c",{{scale:1}},{{scale:1.15,svgOrigin:"100 100",duration:.25,repeat:{max(int((a - da) / 0.25) - 2, 1)},yoyo:true,immediateRender:false}},{da + 0.3:.3f});'
        suono = ("pop", 0.25)
    elif k == "fulmine":
        svg = f'<path d="M118 14L44 112h48l-14 74 78-104h-50z" fill="#FFD23F" stroke="#fff" stroke-width="9" stroke-linejoin="round"/>'
        mov = f'tl.fromTo("#ei{n}",{{filter:"brightness(3)"}},{{filter:"brightness(1)",duration:.3,immediateRender:false}},{da + 0.1:.3f});'
        suono = ("impatto", 0.3)
    else:   # spunta
        svg = (f'<circle cx="100" cy="100" r="84" fill="#2E9E5B" stroke="#fff" stroke-width="10"/>'
               f'<path id="ei{n}a" d="M58 104l28 28 58-62" {_TRATTO} stroke-width="20" stroke-dasharray="140" stroke-dashoffset="140"/>')
        mov = f'tl.to("#ei{n}a",{{strokeDashoffset:0,duration:.3,ease:"power2.out"}},{da + 0.15:.3f});'
        suono = ("ding", 0.25)
    r.corpo.append(f'<svg id="ei{n}" viewBox="0 0 200 200" width="290" height="290" style="position:absolute;left:{x}px;top:{y}px;z-index:32;opacity:0;{ombra}">{svg}</svg>')
    r.tl.append(f'tl.fromTo("#ei{n}",{{opacity:0,scale:.3,rotation:-25}},{{opacity:1,scale:1,rotation:0,duration:.35,ease:"back.out(2.2)",immediateRender:false}},{da:.3f});'
                + mov + f'tl.to("#ei{n}",{{opacity:0,scale:.6,duration:.2}},{a - 0.2:.3f});')
    r.suono("pop", da, 0.2)
    r.suono(suono[0], da + 0.15, suono[1])


TIPI = {"forte": forte, "pila": pila, "schermata": schermata, "fondo": fondo, "icona": icona, "numeri": numeri}
