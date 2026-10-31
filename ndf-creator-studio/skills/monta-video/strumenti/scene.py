"""Le scene a tutto schermo che coprono il video per 1-3 secondi. Ogni tipo di scena è una funzione qui.

Nel piano.json:  "scene": [
  {"tipo": "testo", "da": 4.0, "a": 5.6, "grande": "IN PARTE", "sotto": "è vero"},
  {"tipo": "capitolo", "da": 15.1, "a": 16.6, "numero": "01", "grande": "LA PRIMA", "sotto": "mentalità"}]
"grande" in maiuscolo; "sotto" e "sopra" in corsivo (facoltativi). "colore": "accento" o "testo" per la riga grande.
Tipi nuovi (omini, clip vere, telefono...) si aggiungono come funzioni nuove, senza toccare quelle che ci sono.
"""
import html

CSS = """
.scena{position:absolute;inset:0;opacity:0;z-index:20;overflow:hidden;
 background:radial-gradient(120% 80% at 50% 45%, #2a1a12 0%, #140E0A 60%, #0b0806 100%)}
.scena .luce{position:absolute;left:-40%;top:-20%;width:180%;height:140%;
 background:linear-gradient(115deg, transparent 38%, rgba(232,101,48,.10) 46%, rgba(255,138,76,.18) 50%, rgba(232,101,48,.08) 54%, transparent 62%)}
.scena .blocco{position:absolute;left:110px;right:110px;top:0;bottom:0;display:flex;flex-direction:column;
 justify-content:center;align-items:center;text-align:center;text-wrap:balance}
.scena .clipv{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
.scena .ombra-alto{position:absolute;left:0;right:0;top:0;height:760px;background:linear-gradient(rgba(10,7,5,.75),rgba(10,7,5,0))}
.scena .blocco.alto{top:250px;bottom:auto;justify-content:flex-start}
.scena .xrossa{position:absolute;left:290px;top:900px;width:500px;height:34px;border-radius:17px;background:#D9342B;
 box-shadow:0 4px 16px rgba(0,0,0,.5);transform-origin:center}
.scena .soldo{position:absolute;top:0;width:150px;height:72px;border-radius:8px;border:4px solid;display:flex;
 align-items:center;justify-content:center;font-family:'Plus Jakarta Sans';font-weight:800;font-size:34px;
 box-shadow:0 0 18px #E86530}
.scena .numero{position:absolute;left:0;right:0;top:50%;transform:translateY(-58%);text-align:center;
 font-size:620px;line-height:1;opacity:.16}
"""


def _righe(s, colori, cls_grande, size):
    out = []
    if s.get("sopra"):
        out.append(f'<div class="cors">{html.escape(s["sopra"])}</div>')
    col = colori.get(s.get("colore") or "testo", colori["testo"])
    out.append(f'<div class="grande {cls_grande}" style="color:{col};font-size:{size}px">{html.escape(s["grande"])}</div>')
    if s.get("sotto"):
        out.append(f'<div class="cors acc" style="font-size:78px">{html.escape(s["sotto"])}</div>')
    return "".join(out)


def testo(s, n, colori, size):
    """Scritta su fondo scuro e caldo, con una striscia di luce che scorre."""
    corpo = (f'<div class="scena" id="sc{n}"><div class="luce" id="sc{n}l"></div>'
             f'<div class="blocco" id="sc{n}b">{_righe(s, colori, "", size)}</div></div>')
    return corpo, _animazione(s, n, numero=False)


def capitolo(s, n, colori, size):
    """Come testo, con il numero del capitolo grande e trasparente dietro (01, 02, 03)."""
    num = (f'<div class="numero cors" id="sc{n}n" style="color:{colori["accento"]}">{html.escape(s.get("numero", ""))}</div>')
    corpo = (f'<div class="scena" id="sc{n}"><div class="luce" id="sc{n}l"></div>{num}'
             f'<div class="blocco" id="sc{n}b">{_righe(s, colori, "", size)}</div></div>')
    return corpo, _animazione(s, n, numero=True)


def _animazione(s, n, numero):
    da, a = s["da"], s["a"]
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,y:60,scale:1.12}},{{opacity:1,y:0,scale:1,duration:0.32,ease:"power3.out"}},{da:.3f});',
          f'tl.fromTo("#sc{n}l",{{x:-260}},{{x:260,duration:{a - da:.3f},ease:"none"}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{scale:1}},{{scale:1.05,duration:{max(a - da - 0.32, 0.1):.3f},ease:"none"}},{da + 0.32:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    if numero:
        tl.append(f'tl.fromTo("#sc{n}n",{{opacity:0,scale:0.85}},{{opacity:0.16,scale:1,duration:0.5,ease:"power2.out"}},{da:.3f});')
    return "".join(tl)


def clip(s, n, colori, size):
    """Clip vera a tutto schermo (cartella clip/), titolo in alto, e se serve la X rossa ("x": true)."""
    nome = s["clip"]
    da, a = s["da"], s["a"]
    x = ""
    if s.get("x"):
        x = f'<div class="xrossa" id="sc{n}x1"></div><div class="xrossa" id="sc{n}x2"></div>'
    corpo = (f'<div class="scena" id="sc{n}"><video class="clipv" id="sc{n}v" src="assets/clip-{nome}.mp4" muted playsinline '
             f'data-start="{da:.3f}" data-media-start="0" data-duration="{a - da:.3f}"></video>'
             f'<div class="ombra-alto"></div>{x}'
             f'<div class="blocco alto" id="sc{n}b">{_righe(s, colori, "", min(size, 120))}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}v",{{scale:1.12}},{{scale:1.0,duration:{a - da:.3f},ease:"power1.out"}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,y:40,scale:1.1}},{{opacity:1,y:0,scale:1,duration:0.32,ease:"power3.out"}},{da + 0.05:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    if s.get("x"):
        tl.append(f'tl.set("#sc{n}x1",{{rotation:45,scaleX:0}},0);tl.set("#sc{n}x2",{{rotation:-45,scaleX:0}},0);'
                  f'tl.to("#sc{n}x1",{{scaleX:1,duration:0.18,ease:"power2.out"}},{da + 0.45:.3f});'
                  f'tl.to("#sc{n}x2",{{scaleX:1,duration:0.18,ease:"power2.out"}},{da + 0.6:.3f});')
    return "".join([corpo]), "".join(tl)


# ---------- omino in giacca (ripreso dal kit "Monta le tue Ads") ----------
# angoli dal basso (0 = braccio giù), positivi verso l'esterno: [spalla-gomito, gomito-mano]
POSE = {"in_piedi": ([12, 6], [12, 6]), "spallucce": ([58, 125], [58, 125]),
        "braccia_su": ([158, 172], [158, 172]), "scrivania": ([14, -35], [14, -35])}


def _braccio(lato, su, giu, corpo, bordo):
    import math
    sp = (200 + lato * 66, 206)
    go = (sp[0] + lato * math.sin(math.radians(su)) * 118, sp[1] + math.cos(math.radians(su)) * 118)
    ma = (go[0] + lato * math.sin(math.radians(giu)) * 104, go[1] + math.cos(math.radians(giu)) * 104)
    d = f"M{sp[0]:.0f} {sp[1]:.0f} L{go[0]:.0f} {go[1]:.0f} L{ma[0]:.0f} {ma[1]:.0f}"
    return (f'<path d="{d}" stroke="{bordo}" stroke-width="44" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" stroke="{corpo}" stroke-width="36" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{ma[0]:.0f}" cy="{ma[1]:.0f}" r="19" fill="{bordo}"/><circle cx="{ma[0]:.0f}" cy="{ma[1]:.0f}" r="15" fill="{corpo}"/>')


def _omino_svg(posa, chiaro, colori):
    acc, luce = colori["accento"], colori["accento_luce"]
    corpo = "#161210" if chiaro else colori["scuro"]
    interno = "#2A2420" if chiaro else "#24170F"
    bordo = "#161210" if chiaro else luce
    sx, dx = POSE.get(posa, POSE["in_piedi"])
    seduto = posa == "scrivania"
    gambe = "" if seduto else (
        f'<path d="M128 436 L197 436 L193 700 L146 700 Z" fill="{corpo}" stroke="{bordo}" stroke-width="5" stroke-linejoin="round"/>'
        f'<path d="M203 436 L272 436 L254 700 L207 700 Z" fill="{corpo}" stroke="{bordo}" stroke-width="5" stroke-linejoin="round"/>'
        f'<path d="M136 700 Q170 690 196 700 L196 716 L130 716 Z" fill="{corpo}" stroke="{bordo}" stroke-width="5"/>'
        f'<path d="M204 700 Q230 690 264 700 L270 716 L204 716 Z" fill="{corpo}" stroke="{bordo}" stroke-width="5"/>')
    scrivania = "" if not seduto else (
        f'<path d="M120 300 L280 300 L268 392 L132 392 Z" fill="{"#5A4F47" if chiaro else corpo}" stroke="{acc if chiaro else bordo}" stroke-width="5" stroke-linejoin="round"/>'
        f'<circle cx="200" cy="346" r="10" fill="{acc}"/>'
        f'<rect x="96" y="392" width="208" height="12" rx="4" fill="{corpo}" stroke="{bordo}" stroke-width="4"/>'
        f'<rect x="10" y="404" width="380" height="20" rx="4" fill="{corpo}" stroke="{bordo}" stroke-width="5"/>'
        f'<path d="M44 424 L44 716 M356 424 L356 716" stroke="{bordo}" stroke-width="9" stroke-linecap="round"/>')
    ombra = "rgba(0,0,0,0.18)" if chiaro else "rgba(232,101,48,0.25)"
    glow = ("drop-shadow(0 18px 24px rgba(0,0,0,0.25))" if chiaro
            else f"drop-shadow(0 0 8px {acc}) drop-shadow(0 0 26px {acc})")
    return (f'<svg viewBox="0 0 400 780" style="width:620px;height:1209px;filter:{glow};overflow:visible">'
            f'<ellipse cx="200" cy="742" rx="120" ry="16" fill="{ombra}"/>{gambe}'
            f'<path d="M130 196 Q200 172 270 196 Q292 262 288 332 L284 444 Q200 458 116 444 L112 332 Q108 262 130 196 Z" fill="{corpo}" stroke="{bordo}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M176 188 L200 262 L224 188 Z" fill="{interno}"/>'
            f'<path d="M176 188 L198 286 M224 188 L202 286" stroke="{bordo}" stroke-width="4" fill="none"/>'
            f'<path d="M194 192 L206 192 L212 300 L200 320 L188 300 Z" fill="{acc}"/>'
            f'<circle cx="200" cy="346" r="5" fill="{bordo}"/><circle cx="200" cy="384" r="5" fill="{bordo}"/>'
            f'{_braccio(-1, sx[0], sx[1], corpo, bordo)}{_braccio(1, dx[0], dx[1], corpo, bordo)}'
            f'<rect x="185" y="148" width="30" height="40" rx="8" fill="{corpo}" stroke="{bordo}" stroke-width="4"/>'
            f'<ellipse cx="152" cy="110" rx="9" ry="15" fill="{corpo}" stroke="{bordo}" stroke-width="4"/>'
            f'<ellipse cx="248" cy="110" rx="9" ry="15" fill="{corpo}" stroke="{bordo}" stroke-width="4"/>'
            f'<ellipse cx="200" cy="104" rx="48" ry="56" fill="{corpo}" stroke="{bordo}" stroke-width="5"/>'
            f'<path d="M152 96 Q150 44 200 42 Q252 44 250 96 Q240 66 206 64 Q170 66 152 96 Z" fill="{bordo}" opacity="{1 if chiaro else 0.85}"/>'
            f'{scrivania}</svg>')


def omino(s, n, colori, size):
    """Scena con l'omino in giacca: "posa" (in_piedi, spallucce, braccia_su, scrivania), "chiaro": true per il fondo
    chiaro, "croce": true per la X rossa sopra, "numero": "3" per il numero grande dietro con le banconote che cadono."""
    chiaro = s.get("chiaro", False)
    da, a = s["da"], s["a"]
    fondo = ("radial-gradient(ellipse at 50% 45%, #F9F7F4 35%, #CFC6BB 100%)" if chiaro
             else "radial-gradient(ellipse at 50% 42%, #3A2216 0%, #140E0A 60%, #050302 100%)")
    col_grande = "#141414" if chiaro else "white"
    ombra_t = "none" if chiaro else f"0 0 30px {colori['accento']}"
    extra, tl = "", []
    if s.get("numero"):
        extra += (f'<div class="numero cors" id="sc{n}n" style="top:470px;transform:none;font-size:900px;'
                  f'color:{colori["accento"]}">{html.escape(s["numero"])}</div>')
        for i, x in enumerate([80, 260, 430, 610, 790, 950, 170, 700, 520, 340]):
            extra += (f'<div class="soldo" id="sc{n}m{i}" style="left:{x}px;border-color:{colori["accento_luce"]};'
                      f'color:{colori["accento_luce"]};background:{"#FFF3EC" if chiaro else "rgba(232,101,48,0.18)"}">€</div>')
            tl.append(f'tl.fromTo("#sc{n}m{i}",{{y:{-150 + (i % 3) * 40 - i * 66},rotation:{i * 17}}},'
                      f'{{y:{-150 + (i % 3) * 40 - i * 66 + (a - da) * 660:.0f},rotation:{i * 17 + 120},duration:{a - da:.3f},ease:"none"}},{da:.3f});')
    croce = ""
    if s.get("croce"):
        croce = (f'<svg viewBox="0 0 100 100" style="position:absolute;left:290px;top:820px;width:500px;height:500px">'
                 f'<path id="sc{n}c1" d="M12 12 L88 88" stroke="#D93B2B" stroke-width="9" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                 f'<path id="sc{n}c2" d="M88 12 L12 88" stroke="#D93B2B" stroke-width="9" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
        tl.append(f'tl.to("#sc{n}c1",{{strokeDashoffset:0,duration:0.13,ease:"none"}},{da + 0.33:.3f});'
                  f'tl.to("#sc{n}c2",{{strokeDashoffset:0,duration:0.13,ease:"none"}},{da + 0.46:.3f});')
    sotto = (f'<div class="cors scia" id="sc{n}s" style="font-size:92px;color:{colori["accento"]};margin-top:6px">'
             f'{html.escape(s["sotto"])}</div>') if s.get("sotto") else ""
    corpo = (f'<div class="scena" id="sc{n}" style="background:{fondo}">'
             + ("" if chiaro else f'<div class="luce" id="sc{n}l"></div>') + extra
             + f'<div style="position:absolute;top:240px;left:0;right:0;text-align:center">'   # sotto la fascia alta di Instagram (220)
             f'<div class="grande scia" id="sc{n}g" style="font-size:{min(size, 150)}px;color:{col_grande};text-shadow:{ombra_t}">'
             f'{html.escape(s["grande"])}</div>{sotto}</div>'
             f'<div id="sc{n}o" style="position:absolute;top:600px;left:0;right:0;display:flex;justify-content:center">'
             f'{_omino_svg(s.get("posa", "in_piedi"), chiaro, colori)}</div>{croce}</div>')
    tl += [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
           # la scritta entra di lato con la scia, come nel vecchio kit
           f'tl.fromTo("#sc{n}g",{{opacity:0,x:-260,skewX:14,filter:"blur(14px)"}},{{opacity:1,x:0,skewX:0,filter:"blur(0px)",duration:0.24,ease:"power3.out"}},{da + 0.07:.3f});',
           f'tl.fromTo("#sc{n}o",{{opacity:0,y:260,scale:0.85}},{{opacity:1,y:0,scale:1,duration:0.45,ease:"back.out(1.4)"}},{da:.3f});',
           f'tl.to("#sc{n}o",{{scale:1.015,duration:0.6,yoyo:true,repeat:{max(int((a - da) / 0.6) - 1, 0)},ease:"sine.inOut"}},{da + 0.45:.3f});',
           f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    if sotto:
        tl.append(f'tl.fromTo("#sc{n}s",{{opacity:0,x:260,skewX:-14,filter:"blur(14px)"}},{{opacity:1,x:0,skewX:0,filter:"blur(0px)",duration:0.24,ease:"power3.out"}},{da + 0.27:.3f});')
    if not chiaro:
        tl.append(f'tl.fromTo("#sc{n}l",{{x:-600}},{{x:900,duration:2,ease:"none"}},{da:.3f});')
    if s.get("numero"):
        tl.append(f'tl.fromTo("#sc{n}n",{{opacity:0}},{{opacity:0.22,duration:0.4}},{da:.3f});')
    return corpo, "".join(tl)


# ---------- chat, telefono e schema (ripresi dal kit "Monta le tue Ads") ----------
FONDO_CALDO = "radial-gradient(ellipse at 50% 40%, #3A2216 0%, #140E0A 62%, #050302 100%)"


def chat(s, n, colori, size):
    """Riquadro tipo ChatGPT: "testo" si scrive lettera per lettera, poi il tasto invio e la "risposta" grande."""
    acc, luce = colori["accento"], colori["accento_luce"]
    da, a = s["da"], s["a"]
    testo_ = s["testo"]
    lettere = "".join(f'<span id="sc{n}c{i}" style="opacity:0">{html.escape(ch)}</span>' for i, ch in enumerate(testo_))
    risposta = ""
    if s.get("risposta"):
        righe = "".join(f'<div id="sc{n}r{i}" style="height:22px;border-radius:11px;margin-top:24px;background:rgba(249,247,244,.22);width:0"></div>'
                        for i in range(3))
        risposta = (f'<div id="sc{n}r" style="margin-top:40px;opacity:0"><div class="grande" style="font-size:92px;color:{acc};'
                    f'text-shadow:0 0 30px {acc}">{html.escape(s["risposta"])}</div>{righe}</div>')
    corpo = (f'<div class="scena" id="sc{n}" style="background:{FONDO_CALDO}">'
             f'<div class="cors" id="sc{n}e" style="position:absolute;top:330px;left:0;right:0;text-align:center;font-size:88px;color:{luce}">'
             f'{html.escape(s.get("etichetta", "apri ChatGPT"))}</div>'
             f'<div id="sc{n}k" style="position:absolute;top:520px;left:90px;right:90px">'
             f'<div id="sc{n}box" style="background:rgba(249,247,244,.07);border:3px solid rgba(249,247,244,.35);border-radius:44px;padding:44px 48px">'
             f'<div style="font-family:\'Plus Jakarta Sans\';font-weight:700;font-size:58px;line-height:1.25;color:white">{lettere}'
             f'<span style="color:{acc}">|</span></div></div>'
             f'<div style="display:flex;justify-content:flex-end;margin-top:26px"><div id="sc{n}inv" style="width:96px;height:96px;border-radius:48px;'
             f'background:{acc};display:flex;align-items:center;justify-content:center;font-family:\'Plus Jakarta Sans\';font-weight:800;'
             f'font-size:54px;color:white">↑</div></div>{risposta}</div></div>')
    fine = da + (a - da) * s.get("scrittura", 0.55)  # quanto della scena dura la scrittura (più basso = più veloce)
    passo = (fine - da - 0.2) / max(len(testo_), 1)
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}k",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{da:.3f});',
          f'tl.fromTo("#sc{n}e",{{opacity:0}},{{opacity:1,duration:0.3}},{da:.3f});']
    tl += [f'tl.set("#sc{n}c{i}",{{opacity:1}},{da + 0.2 + i * passo:.3f});' for i in range(len(testo_))]
    tl.append(f'tl.set("#sc{n}box",{{borderColor:"{acc}",boxShadow:"0 0 40px rgba(232,101,48,.45)"}},{fine:.3f});'
              f'tl.fromTo("#sc{n}inv",{{scale:1}},{{scale:1.15,duration:0.12,yoyo:true,repeat:1}},{fine + 0.13:.3f});')
    if s.get("risposta"):
        tl.append(f'tl.fromTo("#sc{n}r",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.35,ease:"power3.out"}},{fine + 0.45:.3f});')
        tl += [f'tl.to("#sc{n}r{i}",{{width:"{w}%",duration:0.4,ease:"power2.out"}},{fine + 0.45:.3f});' for i, w in enumerate((92, 78, 64))]
    tl.append(f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});')
    return corpo, "".join(tl)


def telefono(s, n, colori, size):
    """Telefono che entra inclinato e si raddrizza. "modo": "storia" (adesivo domande + "domande" che arrivano)
    oppure "reel" (dentro c'è il video tagliato della persona, con icone e "didascalia")."""
    acc, luce = colori["accento"], colori["accento_luce"]
    da, a = s["da"], s["a"]
    W, H = 560, 1060
    if s.get("modo") == "reel":
        dentro = (f'<video id="sc{n}v" src="assets/tagliato.mp4" muted playsinline data-start="{da:.3f}" data-media-start="{da:.3f}" '
                  f'data-duration="{a - da:.3f}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></video>'
                  f'<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,0) 60%,rgba(0,0,0,.6) 100%)"></div>'
                  + "".join(f'<div style="position:absolute;right:30px;bottom:{430 - i * 90}px;font-size:52px;color:white;'
                            f'text-shadow:0 4px 12px rgba(0,0,0,.6)">{c}</div>' for i, c in enumerate(["♥", "✉", "➤"]))
                  + f'<div style="position:absolute;left:36px;bottom:110px;font-family:\'Plus Jakarta Sans\';font-weight:800;font-size:40px;'
                  f'color:white;text-shadow:0 4px 12px rgba(0,0,0,.7)">{html.escape(s.get("didascalia", "1 domanda = 1 risposta"))}</div>'
                  f'<div style="position:absolute;left:36px;right:36px;bottom:60px;height:10px;border-radius:5px;background:rgba(255,255,255,.3)">'
                  f'<div id="sc{n}p" style="width:0;height:100%;border-radius:5px;background:{acc}"></div></div>')
    else:
        domande = s.get("domande", [])
        dentro = (f'<div style="position:absolute;inset:0;background:linear-gradient(160deg,#3A2216 0%,#24170F 55%,#140E0A 100%)"></div>'
                  f'<div style="position:absolute;top:30px;left:30px;right:30px;height:8px;border-radius:4px;background:rgba(255,255,255,.3)">'
                  f'<div id="sc{n}p" style="width:0;height:100%;border-radius:4px;background:white"></div></div>'
                  f'<div style="position:absolute;top:64px;left:30px;display:flex;align-items:center;gap:16px">'
                  f'<div style="width:62px;height:62px;border-radius:31px;border:4px solid {acc};background:#3A2216"></div>'
                  f'<div style="font-family:\'Plus Jakarta Sans\';font-weight:700;font-size:30px;color:white">il tuo profilo</div></div>'
                  f'<div id="sc{n}ad" style="position:absolute;top:250px;left:60px;right:60px;border-radius:34px;background:white;overflow:hidden;'
                  f'box-shadow:0 20px 50px rgba(0,0,0,.5)"><div style="background:linear-gradient(90deg,{acc},{luce});padding:30px 20px;'
                  f'text-align:center;font-family:\'Plus Jakarta Sans\';font-weight:800;font-size:38px;color:white">'
                  f'{html.escape(s.get("adesivo", "FAMMI UNA DOMANDA"))}</div><div style="padding:30px 20px;text-align:center;'
                  f'font-family:\'Plus Jakarta Sans\';font-weight:700;font-size:30px;color:#9A918A">Scrivi qualcosa…</div></div>'
                  + "".join(f'<div id="sc{n}d{i}" style="position:absolute;top:{560 + i * 120}px;left:{110 if i % 2 else 50}px;max-width:420px;'
                            f'padding:22px 30px;border-radius:30px;background:rgba(249,247,244,.95);font-family:\'Plus Jakarta Sans\';'
                            f'font-weight:700;font-size:32px;color:#1C1A18;opacity:0">{html.escape(d)}</div>' for i, d in enumerate(domande)))
    sotto = (f'<div class="cors scia" id="sc{n}s" style="font-size:72px;color:{luce}">{html.escape(s["sotto"])}</div>'
             if s.get("sotto") else "")
    corpo = (f'<div class="scena" id="sc{n}" style="background:{FONDO_CALDO.replace("50% 40%", "50% 55%")}">'
             f'<div style="position:absolute;top:290px;left:0;right:0;text-align:center">'
             f'<div class="grande scia" id="sc{n}g" style="font-size:104px;color:white;text-shadow:0 0 26px {acc}">'
             f'{html.escape(s["grande"])}</div>{sotto}</div>'
             f'<div id="sc{n}t" style="position:absolute;left:{(1080 - W) // 2}px;top:540px;width:{W}px;height:{H}px;border-radius:70px;'
             f'border:6px solid {acc};box-shadow:0 0 50px rgba(232,101,48,.5);overflow:hidden;background:#0B0807">{dentro}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}t",{{y:500,rotation:8}},{{y:0,rotation:0,duration:0.55,ease:"back.out(1.2)"}},{da + 0.07:.3f});',
          f'tl.fromTo("#sc{n}g",{{opacity:0,x:-260,skewX:14,filter:"blur(14px)"}},{{opacity:1,x:0,skewX:0,filter:"blur(0px)",duration:0.24,ease:"power3.out"}},{da + 0.03:.3f});',
          f'tl.fromTo("#sc{n}p",{{width:"0%"}},{{width:"100%",duration:{a - da:.3f},ease:"none"}},{da:.3f});']
    if sotto:
        tl.append(f'tl.fromTo("#sc{n}s",{{opacity:0,x:260,skewX:-14,filter:"blur(14px)"}},{{opacity:1,x:0,skewX:0,filter:"blur(0px)",duration:0.24,ease:"power3.out"}},{da + 0.2:.3f});')
    if s.get("modo") != "reel":
        tl.append(f'tl.fromTo("#sc{n}ad",{{scale:0}},{{scale:1,duration:0.4,ease:"back.out(1.6)"}},{da + 0.4:.3f});')
        tl += [f'tl.fromTo("#sc{n}d{i}",{{opacity:0,x:{300 if i % 2 else -300}}},{{opacity:1,x:0,duration:0.35,ease:"back.out(1.3)"}},{da + 1.33 + i * 0.87:.3f});'
               for i in range(len(s.get("domande", [])))]
    tl.append(f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});')
    return corpo, "".join(tl)


def schema(s, n, colori, size):
    """Riquadri collegati da frecce che si disegnano da soli. "passi": [["1", "domande", 44.0], ...] (numero, testo, secondo)."""
    acc = colori["accento"]
    chiaro = s.get("chiaro", False)
    linea, teal = ("#3A3632" if chiaro else "#E9E2D8"), "#2FA3C7"
    H, top0, da, a = 230, 470, s["da"], s["a"]
    passi = s["passi"]
    parti, tl = [], [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
                     f'tl.fromTo("#sc{n}ti",{{opacity:0}},{{opacity:1,duration:0.4}},{da:.3f});']
    for i, (num, testo_, t) in enumerate(passi):
        y = top0 + i * (H + 80)
        ultimo = i == len(passi) - 1
        parti.append(f'<rect id="sc{n}b{i}" x="190" y="{y}" width="700" height="{H - 40}" rx="34" fill="none" stroke="{acc if ultimo else linea}" '
                     f'stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" '
                     f'style="filter:{f"drop-shadow(0 0 10px {acc})" if ultimo else "none"}"/>'
                     f'<g id="sc{n}x{i}" opacity="0"><text x="300" y="{y + (H - 40) / 2 + 30:.0f}" text-anchor="middle" font-family="Instrument Serif" '
                     f'font-style="italic" font-size="110" fill="{acc}">{html.escape(num)}</text>'
                     f'<text x="400" y="{y + (H - 40) / 2 + 18:.0f}" font-family="Plus Jakarta Sans" font-weight="800" font-size="58" '
                     f'fill="{"#1C1A18" if chiaro else "white"}">{html.escape(testo_)}</text></g>')
        tl.append(f'tl.to("#sc{n}b{i}",{{strokeDashoffset:0,duration:0.6,ease:"none"}},{t:.3f});'
                  f'tl.fromTo("#sc{n}x{i}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,ease:"back.out(1.5)"}},{t + 0.27:.3f});')
        if not ultimo:
            parti.append(f'<path id="sc{n}f{i}" d="M540 {y + H - 40} L540 {y + H + 40} M515 {y + H + 15} L540 {y + H + 40} L565 {y + H + 15}" fill="none" '
                         f'stroke="{teal}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
            tl.append(f'tl.to("#sc{n}f{i}",{{strokeDashoffset:0,duration:0.4,ease:"none"}},{passi[i + 1][2] - 0.33:.3f});')
    fondo = "#F9F7F4" if chiaro else "radial-gradient(ellipse at 50% 40%, #1E1712 0%, #0B0807 72%)"
    corpo = (f'<div class="scena" id="sc{n}" style="background:{fondo}">'
             f'<div id="sc{n}ti" style="position:absolute;top:210px;left:0;right:0;text-align:center;font-family:\'Plus Jakarta Sans\';'
             f'font-weight:700;font-size:32px;letter-spacing:6px;color:{acc if chiaro else teal}">{html.escape(s.get("titolo", "IN 3 PASSAGGI"))}</div>'
             f'<svg viewBox="0 0 1080 1920" style="position:absolute;inset:0">{"".join(parti)}</svg></div>')
    tl.append(f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});')
    return corpo, "".join(tl)


def immagine(s, n, colori, size):
    """Foto a tutto schermo (DATI/immagini/<nome>.jpg) che si avvicina piano, con il titolo in alto."""
    da, a = s["da"], s["a"]
    corpo = (f'<div class="scena" id="sc{n}"><img class="clipv" id="sc{n}v" src="assets/img-{s["immagine"]}.jpg">'
             f'<div class="ombra-alto"></div>'
             f'<div class="blocco alto" id="sc{n}b">{_righe(s, colori, "", min(size, 120))}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}v",{{scale:1.0}},{{scale:1.14,duration:{a - da:.3f},ease:"none"}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,y:40,scale:1.1}},{{opacity:1,y:0,scale:1,duration:0.32,ease:"power3.out"}},{da + 0.05:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    return corpo, "".join(tl)


TIPI = {"testo": testo, "capitolo": capitolo, "clip": clip, "omino": omino, "chat": chat, "telefono": telefono,
        "schema": schema, "immagine": immagine}

# ---------- entrate delle scene (riprese dal kit "Monta le tue Ads") ----------
# "lampo": un flash bianco quando la scena entra e quando si torna alla persona
# "scorri": la scena nuova entra da destra spingendo via quella prima
# "carta": la scena compare sfocata e diventa nitida, morbida
LAMPO = '<div id="lampo" style="position:absolute;inset:0;background:white;opacity:0;z-index:45;pointer-events:none"></div>'



# ---------- stile delle ads (esempi/ads-g31): bagliore, scheda della persona, finale su carta ----------
CSS_ADS = """
.scena .alone{position:absolute;left:50%;top:44%;width:1500px;height:1500px;margin:-750px 0 0 -750px;border-radius:50%;opacity:.9}
.scena .raggi{position:absolute;left:50%;top:46%;width:3200px;height:3200px;margin:-1600px 0 0 -1600px;opacity:.75;
 -webkit-mask:radial-gradient(circle,rgba(0,0,0,0) 6%,#000 22%,rgba(0,0,0,.4) 60%);mask:radial-gradient(circle,rgba(0,0,0,0) 6%,#000 22%,rgba(0,0,0,.4) 60%)}
.scena .pillola{display:inline-block;margin-top:18px;padding:8px 26px;border-radius:30px;font-family:'Plus Jakarta Sans';font-weight:800;
 font-size:34px;letter-spacing:1px;text-transform:uppercase}
.scena .contatore{font-size:330px;line-height:.9;margin-top:10px}
.carta{background:radial-gradient(ellipse 60% 45% at 50% 45%,#F7F3EA 0%,#E8E0D2 70%,#CFC4B2 100%)}
.carta .storto{transform:skewX(-9deg);font-style:normal}
.carta .scheda-p{position:absolute;left:60px;right:60px;top:180px;bottom:220px;border-radius:40px;border:4px solid rgba(0,0,0,.18)}
.carta .pill2{display:inline-flex;align-items:center;gap:12px;margin-top:22px;padding:10px 26px;border-radius:12px;
 font-family:'Plus Jakarta Sans';font-weight:800;font-size:36px;text-transform:uppercase}
.carta .giu{font-size:70px;line-height:1;margin-top:14px}
"""


def luce(s, n, colori, size):
    """Scena "luce" (stile ads): fondo nero con un alone del colore d'accento e, se "raggi": true, raggi di luce che
    corrono verso di te; titolo stretto e alto con il bagliore; sotto una pillola ("etichetta"); oppure un numero che
    conta fino a quello detto ("numero": 184, con "grande" sopra come etichetta)."""
    da, a = s["da"], s["a"]
    acc = colori["accento"]
    raggi = (f'<div class="raggi" id="sc{n}r" style="background:repeating-conic-gradient(from 0deg,{acc}00 0deg 4deg,{acc}cc 4.5deg 5deg,{acc}00 5.5deg 9deg)"></div>'
             if s.get("raggi") else "")
    alone = f'<div class="alone" style="background:radial-gradient(circle,{acc}cc 0%,{acc}55 25%,rgba(0,0,0,0) 60%)"></div>'
    pill = (f'<div class="pillola" style="background:{acc};color:#140E0A">{html.escape(s["etichetta"])}</div>' if s.get("etichetta") else "")
    numero = (f'<div class="grande contatore" id="sc{n}c" style="color:#fff">0</div>' if s.get("numero") is not None else "")
    righe = "".join(f'<div class="grande" style="font-size:{size}px;color:#fff">{html.escape(r)}</div>' for r in s.get("grande", "").split(" / ") if r)
    corpo = (f'<div class="scena" id="sc{n}" style="background:#050302">{alone}{raggi}'
             f'<div class="blocco" id="sc{n}b">{righe}{numero}{pill}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,scale:1.25,filter:"blur(12px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.28,ease:"power3.out"}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{y:0}},{{y:-20,duration:{max(a - da - 0.3, 0.1):.3f},ease:"none",immediateRender:false}},{da + 0.3:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    if s.get("raggi"):
        tl.append(f'tl.fromTo("#sc{n}r",{{rotation:0,scale:0.8}},{{rotation:25,scale:1.25,duration:{a - da:.3f},ease:"none"}},{da:.3f});')
    if s.get("numero") is not None:
        tl.append(f'contaNumero("#sc{n}c",{int(s["numero"])},{s.get("conta", da + 0.15):.3f},0.8);')
    return corpo, "".join(tl)


def persona(s, n, colori, size):
    """Scheda di una persona su fondo carta: il nome grande e storto, sotto le pillole della sua storia unite da
    frecce (prima scura, ultima del colore d'accento). s = {"nome": "DAISY", "voci": ["20 anni dipendente",
    "vive di network"], "da", "a"}."""
    da, a = s["da"], s["a"]
    voci = s.get("voci", [])
    pill = []
    for k, v in enumerate(voci):
        ultimo = k == len(voci) - 1
        col = f'background:{colori["accento"]};color:#140E0A' if ultimo else 'background:#1A1410;color:#fff'
        pill.append(f'<div class="pill2" id="sc{n}p{k}" style="{col}">{html.escape(v)}</div>'
                    + ('' if ultimo else f'<div class="giu" style="color:{colori["accento"]}">↓</div>'))
    corpo = (f'<div class="scena carta" id="sc{n}"><div class="scheda-p"></div><div class="blocco" id="sc{n}b">'
             f'<div class="grande storto" style="font-size:{min(size + 40, 200)}px;color:#140E0A;'
             f'text-shadow:6px 6px 0 {colori["accento"]}">{html.escape(s["nome"])}</div>{"".join(pill)}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{da:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    for k in range(len(voci)):
        tl.append(f'tl.fromTo("#sc{n}p{k}",{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.22,ease:"back.out(2)"}},{da + 0.3 + 0.35 * k:.3f});')
    return corpo, "".join(tl)


def carta(s, n, colori, size):
    """Finale su carta (stile ads): fondo chiaro con l'ombra ai bordi, righe grandi e storte con l'ombra d'accento,
    una freccia che salta e una riga piccola sotto ("sotto"). s = {"grande": "CLICCA / QUI SOTTO", "sotto": "cambia tutto."}."""
    da, a = s["da"], s["a"]
    righe = [r for r in s["grande"].split(" / ") if r]
    blocco = "".join(f'<div class="grande storto" style="font-size:{size if k == 0 else int(size * 0.72)}px;color:#140E0A;'
                     f'text-shadow:5px 5px 0 {colori["accento"]}">{html.escape(r)}</div>' for k, r in enumerate(righe))
    sotto = f'<div class="cors" id="sc{n}s" style="color:#140E0A;text-shadow:none;font-size:52px">{html.escape(s.get("sotto", ""))}</div>' if s.get("sotto") else ""
    corpo = (f'<div class="scena carta" id="sc{n}"><div class="blocco" id="sc{n}b">{blocco}'
             f'<div class="giu" id="sc{n}f" style="color:#140E0A;font-size:110px;margin:20px 0 50px">↓</div>{sotto}</div></div>')
    tl = [f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});',
          f'tl.fromTo("#sc{n}b",{{opacity:0,scale:0.9,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.3,ease:"power3.out"}},{da:.3f});',
          f'tl.fromTo("#sc{n}f",{{y:0}},{{y:20,duration:0.4,repeat:{max(int((a - da) / 0.4), 1)},yoyo:true,ease:"sine.inOut"}},{da + 0.3:.3f});',
          f'tl.set("#sc{n}",{{opacity:0}},{a:.3f});']
    if s.get("sotto"):
        tl.append(f'tl.fromTo("#sc{n}s",{{opacity:0}},{{opacity:1,duration:0.25}},{s.get("sotto_da", da + 0.8):.3f});')
    return corpo, "".join(tl)


TIPI.update({"luce": luce, "persona": persona, "carta": carta})

def entrata(s, n):
    tipo, da, a = s.get("entrata"), s["da"], s["a"]
    if tipo == "lampo":
        return (f'tl.fromTo("#lampo",{{opacity:0.75}},{{opacity:0,duration:0.14,ease:"power2.out"}},{da:.3f});'
                f'tl.fromTo("#lampo",{{opacity:0.6}},{{opacity:0,duration:0.14,ease:"power2.out"}},{a:.3f});')
    if tipo == "scorri":
        return f'tl.fromTo("#sc{n}",{{x:1080}},{{x:0,duration:0.28,ease:"power3.out"}},{da:.3f});'
    if tipo == "carta":
        return f'tl.fromTo("#sc{n}",{{opacity:0,filter:"blur(14px)"}},{{opacity:1,filter:"blur(0px)",duration:0.35,ease:"power2.out"}},{da:.3f});'
    return ""


def costruisci_scena(s, n, colori, size):
    if s["tipo"] not in TIPI:
        raise SystemExit(f"Tipo di scena sconosciuto: {s['tipo']} (ci sono: {', '.join(TIPI)})")
    return TIPI[s["tipo"]](s, n, colori, size)
