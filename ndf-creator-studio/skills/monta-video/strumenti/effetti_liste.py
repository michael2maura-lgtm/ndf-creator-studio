"""Effetti di elenchi, capitoli, muri e nastri (18/11/2026), rifatti da noi guardando come si muovono gli effetti
di riferimento (mai copiato il codice). Motore grafica, tempi del video TAGLIATO. Mentre ci sono, i sottotitoli si nascondono.

 {"tipo": "elenco", "da", "a", "titolo": "IN QUESTO VIDEO", "voci": [["Il gancio", t], ["Lo zoom", t]]}
     Elenco che si accende: ti sposti un po' di lato e accanto compare l'elenco numerato, come l'indice di un video;
     la voce di cui parli si accende, una dopo l'altra. Da 2 a 6 voci, corte.
 {"tipo": "scalata", "da", "a", "titolo": "Le 5 cose", "voci": [["La parola", t], ["Il finale", t], ...]}
     Le cose dal basso: ti sposti di lato e accanto sale la scala dei numeri, dall'ultimo in fondo fino all'1 in cima,
     con la corona. Le voci in ordine di come le dici (la prima detta è l'ultima della scala). Da 3 a 10.
 {"tipo": "mosaico", "da", "a", "etichetta": "+300 REEL" (facoltativa), "immagini": ["a.jpg", ...] (facoltative)}
     Muro di reel: dietro di te si accende un muro di riquadri con i fotogrammi del video (o le foto di DATI/immagini),
     dal centro verso i bordi; tu resti davanti. Per "centinaia di reel", "tutti i miei contenuti", tanti clienti.
 {"tipo": "capitolo", "da", "a", "numero": "01", "testo": "il gancio"}
     Capitolo: un numero grande con l'etichetta accanto, in alto. Per i reel a punti: uno per ogni punto.
 {"tipo": "nastro", "da", "a", "testo": "progressione", "secondo": "costanza" (facoltativo)}
     Nastro che scorre: un nastro inclinato attraversa lo schermo con la parola che scorre; con "secondo" ne passa un
     altro incrociato. Per la parola chiave di un discorso, un tema.
"""
import html
import os

from effetti_carte import _cima, _cx, _foto

E = html.escape


def _css(r):
    if getattr(r, "css_liste", False):
        return
    r.css_liste = True
    r.font_extra("InterTight.ttf")
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}"
        ".el-ombra{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:29;opacity:0;pointer-events:none}"
        ".el-box{position:absolute;z-index:31;opacity:0;font-family:'Inter Tight'}"
        ".el-riga{position:relative;white-space:nowrap}"
        ".el-riga b{position:absolute;font-weight:800}"
        ".el-riga span{display:inline-block;font-weight:700}"
        ".el-luce{position:absolute;border-radius:40px;box-shadow:0 6px 16px rgba(0,0,0,.28)}"
        ".el-muro{position:absolute;inset:0;opacity:0}"
        ".el-muro i{position:absolute;border-radius:14px;background-size:cover;background-position:center;opacity:0;"
        "box-shadow:0 6px 16px rgba(0,0,0,.35)}"
        ".el-pill{position:absolute;z-index:31;opacity:0;border-radius:40px;font:900 40px 'Inter Tight';padding:14px 30px;"
        "box-shadow:0 10px 24px rgba(0,0,0,.35);white-space:nowrap}"
        ".el-cap{position:absolute;z-index:31;display:flex;align-items:center;gap:22px;font-family:'Inter Tight'}"
        ".el-cap .el-fin{display:block;overflow:hidden;padding:0 6px}"
        ".el-cap .el-num{display:block;font-weight:900;line-height:.9;letter-spacing:-.04em;text-shadow:0 6px 24px rgba(0,0,0,.35)}"
        ".el-cap .el-filo{height:5px;border-radius:3px;width:0}"
        ".el-cap .el-et{font-weight:800;font-size:30px;letter-spacing:.14em;padding:12px 22px;border-radius:14px;opacity:0;white-space:nowrap}"
        ".el-nastro{position:absolute;left:-300px;width:1680px;z-index:31;overflow:hidden;opacity:0;box-shadow:0 12px 26px rgba(0,0,0,.35)}"
        ".el-nastro div{white-space:nowrap;font:900 50px/96px 'Inter Tight';letter-spacing:.02em}"
        "</style>")


def _sposta_persona(r, da, a, dx, zoom=1.0, faccia=None):
    """Ti sposta di lato (dx pixel) per fare posto. Senza zoom il lato vuoto lo copre la sfumatura scura; con lo zoom
    (ingrandito attorno al viso) lo spostamento resta dentro il video e non si vede nessun bordo."""
    T = r.tl.append
    if zoom > 1 and faccia:
        ox, oy = _cx(faccia), faccia["occhi"]
        dx = min(dx, ox * (zoom - 1))
        T(f'tl.set("#cam",{{transformOrigin:"{ox:.0f}px {oy:.0f}px"}},{da:.3f});'
          f'tl.fromTo("#cam",{{x:0,scale:1}},{{x:{dx:.0f},scale:{zoom},duration:.45,ease:"power3.inOut",immediateRender:false}},{da:.3f});'
          f'tl.to("#cam",{{x:0,scale:1,duration:.4,ease:"power3.inOut"}},{a - 0.4:.3f});tl.set("#cam",{{clearProps:"x,scale,transformOrigin"}},{a:.3f});')
        return
    T(f'tl.fromTo("#cam",{{x:0}},{{x:{dx},duration:.45,ease:"power3.inOut",immediateRender:false}},{da:.3f});'
      f'tl.to("#cam",{{x:0,duration:.4,ease:"power3.inOut"}},{a - 0.4:.3f});tl.set("#cam",{{clearProps:"x"}},{a:.3f});')


def _ombra_lato(r, n, da, a, colore, sinistra=True, fino=0.62, pieno=None):
    verso = "90deg" if sinistra else "270deg"
    pieno = fino * 0.62 if pieno is None else pieno
    r.corpo.append(f'<div class="el-ombra" id="eo{n}s" style="background:linear-gradient({verso},{colore} 0 {pieno:.1%},'
                   f'{colore}00 {fino:.1%})"></div>')
    r.tl.append(f'tl.fromTo("#eo{n}s",{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{da:.3f});'
                f'tl.to("#eo{n}s",{{opacity:0,duration:.4}},{a - 0.4:.3f});')


def _voci(e):
    return [x if isinstance(x, (list, tuple)) else [x, None] for x in e.get("voci", [])]


# ---------------------------------------------------------------- elenco che si accende
def elenco(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    voci = _voci(e)[:6]
    if not voci:
        return
    dim = 40 if max(len(v[0]) for v in voci) <= 13 else 33
    RH, W = 78, max(320, int(max(len(v[0]) for v in voci) * dim * 0.6) + 110)
    W = min(W, 480)
    x0, y0 = 40, max(_cima(faccia) - 60, 230)
    dx = max(0, x0 + W + 30 - faccia["sinistra"])
    righe = "".join(f'<div class="el-riga" style="height:{RH}px;line-height:{RH}px;padding:0 30px 0 74px">'
                    f'<b style="left:28px;font-size:26px;color:{c.get("accento_luce", "#FFB27A")}">{k + 1:02d}</b>'
                    f'<span id="el{n}v{k}" style="font-size:{dim}px;color:{c.get("testo", "#fff")};opacity:.55">{E(v[0])}</span></div>'
                    for k, v in enumerate(voci))
    titolo = e.get("titolo", "IN QUESTO VIDEO").upper()
    r.corpo.append(
        f'<div class="el-box" id="el{n}" style="left:{x0}px;top:{y0:.0f}px;width:{W}px;padding:74px 0 20px;border-radius:30px;'
        f'background:{c.get("scuro", "#141414")}E6;border:2px solid rgba(255,255,255,.12);box-shadow:0 16px 34px rgba(0,0,0,.4)">'
        f'<div style="position:absolute;left:28px;top:26px;font-weight:800;font-size:24px;letter-spacing:.16em;color:{c.get("accento_luce", "#FFB27A")}">{E(titolo)}</div>'
        f'<div style="position:absolute;left:26px;right:26px;top:66px;height:2px;background:rgba(255,255,255,.14)"></div>'
        f'<i class="el-luce" id="el{n}l" style="left:12px;right:12px;top:{74 + 7}px;height:{RH - 14}px;background:{c.get("testo", "#fff")};opacity:0"></i>'
        f'{righe}</div>')
    T = r.tl.append
    _sposta_persona(r, da, a, dx, 1.25, faccia)
    T(f'tl.fromTo("#el{n}",{{opacity:0,x:-200}},{{opacity:1,x:0,duration:.45,ease:"power3.out",immediateRender:false}},{da + 0.1:.3f});')
    prima = None
    for k, (testo, t) in enumerate(voci):
        t = max(t if t is not None else da + 0.6 + k * 0.7, da + 0.4)
        if prima is None:
            T(f'tl.set("#el{n}l",{{y:{k * RH}}},{t:.3f});tl.to("#el{n}l",{{opacity:1,duration:.2}},{t:.3f});')
        else:
            T(f'tl.to("#el{n}l",{{y:{k * RH},duration:.35,ease:"power3.inOut"}},{t:.3f});'
              f'tl.to("#el{n}v{prima}",{{color:"{c.get("testo", "#fff")}",opacity:.85,duration:.2}},{t:.3f});')
        T(f'tl.to("#el{n}v{k}",{{color:"{c.get("scuro", "#141414")}",opacity:1,duration:.2}},{t + 0.1:.3f});')
        r.suono_libreria("hyperframes/click-soft.mp3", t, 0.35)
        prima = k
    T(f'tl.to("#el{n}",{{opacity:0,x:-200,duration:.35,ease:"power2.in"}},{a - 0.4:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- le cose dal basso
def scalata(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    voci = _voci(e)[:10]
    q = len(voci)
    if q < 2:
        return
    # in pagina dall'1 (in alto) all'ultimo (in basso); la prima voce detta è l'ultima della scala
    alto_tot = 1420 - 380
    RH = min(110, alto_tot // q)
    RH = min(RH, 100)
    lunga = max(len(v[0]) for v in voci)
    dim = 38 if lunga <= 12 else (32 if lunga <= 16 else 28)
    W = min(max(380, int(lunga * dim * 0.58) + RH + 40), 520)
    x0, y0 = 40, 360
    dx = min(max(0, x0 + W + 50 - faccia["sinistra"]), 340)   # la fascia non deve mai coprire la faccia
    _ombra_lato(r, n, da, a, c.get("accento_luce", "#FFB27A"), True, (x0 + W + 60) / 1080, (x0 + W + 5) / 1080)   # fascia arancione chiaro (colore chiaro dello stile), scritte scure: il nero era brutto (Michael 18/11)
    ink = c.get("banda", "#4A2412")
    righe = []
    for p in range(q):            # p = posto - 1
        k = q - 1 - p             # indice nella lista detta
        righe.append(f'<div class="el-riga" style="height:{RH}px;line-height:{RH}px;padding:0 20px 0 {RH + 20}px">'
                     f'<b style="left:0;width:{RH}px;text-align:center;font-size:{int(RH * 0.62)}px;color:{ink}" id="es{n}n{k}">{p + 1}</b>'
                     f'<span id="es{n}v{k}" style="font-size:{dim}px;color:{ink};opacity:0">{E(voci[k][0])}</span></div>')
    corona = ('<svg width="56" height="40" viewBox="-1.05 -.85 2.1 1.4" style="position:absolute;opacity:0" id="es{n}c">'
              '<path d="M-1 .5 L-1 -.45 L-.5 .05 L0 -.8 L.5 .05 L1 -.45 L1 .5 Z" fill="#F6C945" stroke="INK" stroke-width=".09" stroke-linejoin="round"/></svg>').replace("{n}", str(n)).replace("INK", ink)
    titolo = e.get("titolo", f"Le {q} cose")
    r.corpo.append(
        f'<div class="el-box" id="es{n}" style="left:{x0}px;top:{y0}px;width:{W}px">'
        f'<div style="position:absolute;left:0;top:-110px;font-weight:900;font-size:72px;letter-spacing:-.02em;color:{ink};white-space:nowrap">{E(titolo)}</div>'
        f'<i class="el-luce" id="es{n}l" style="left:-14px;right:20px;top:{(q - 1) * RH + 6}px;height:{RH - 12}px;background:#fff;opacity:0"></i>'
        f'{"".join(righe)}<div style="position:absolute;left:{RH + 16}px;top:-8px">{corona}</div></div>')
    T = r.tl.append
    _sposta_persona(r, da, a, dx)
    T(f'tl.fromTo("#es{n}",{{opacity:0,x:-120}},{{opacity:1,x:0,duration:.45,ease:"power3.out",immediateRender:false}},{da + 0.1:.3f});')
    for k in range(q):
        T(f'tl.set("#es{n}n{k}",{{opacity:.35}},{da:.3f});')
    prima = None
    for k, (testo, t) in enumerate(voci):
        t = max(t if t is not None else da + 0.6 + k * 0.5, da + 0.35)
        p = q - 1 - k
        if prima is None:
            T(f'tl.to("#es{n}l",{{opacity:1,duration:.2}},{t:.3f});')
        else:
            T(f'tl.to("#es{n}l",{{y:{-(k) * RH},duration:.35,ease:"power3.inOut"}},{t:.3f});'
              f'tl.to("#es{n}v{prima}",{{color:"{ink}",duration:.2}},{t:.3f});'
              f'tl.to("#es{n}n{prima}",{{color:"{ink}",duration:.2}},{t:.3f});')
        T(f'tl.fromTo("#es{n}v{k}",{{opacity:0,x:-20}},{{opacity:1,x:0,color:"#111111",duration:.25,immediateRender:false}},{t + 0.1:.3f});'
          f'tl.to("#es{n}n{k}",{{opacity:1,color:"#111111",duration:.2}},{t + 0.1:.3f});')   # barra chiara, scritta nera
        r.suono_libreria("hyperframes/click-soft.mp3", t, 0.35)
        prima = k
        if p == 0:
            T(f'tl.fromTo("#es{n}c",{{opacity:0,y:-30,scale:.4}},{{opacity:1,y:0,scale:1,duration:.35,ease:"back.out(2.5)",immediateRender:false}},{t + 0.3:.3f});')
            r.suono_libreria("hyperframes/sparkle.mp3", t + 0.3, 0.3)
    T(f'tl.to("#es{n}",{{opacity:0,x:-120,duration:.35,ease:"power2.in"}},{a - 0.4:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- muro di reel
def mosaico(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.camera)
    c = r.stile["colori"]
    COL, RIG, G = 4, 6, 10
    tw, th = (1080 - G * (COL + 1)) / COL, (1920 - G * (RIG + 1)) / RIG
    foto = []
    imm = e.get("immagini") or []
    quante = max(len(imm), 9) if imm else 9
    for j in range(quante):
        if imm:
            f = _foto(r, f"muro-{n}-{j}.jpg", immagine=imm[j % len(imm)], w=264, h=310)
        else:
            f = _foto(r, f"muro-{n}-{j}.jpg", secondo=r.D * (j + 0.5) / quante, w=264, h=310, faccia=faccia)
        if f:
            foto.append(f)
    if not foto:
        return
    tess, tl = [], []
    cx, cy = 1080 / 2, 1920 * 0.45
    for i in range(RIG):
        for j in range(COL):
            x, y = G + j * (tw + G), G + i * (th + G)
            d = (((x + tw / 2 - cx) / 1080) ** 2 + ((y + th / 2 - cy) / 1920) ** 2) ** 0.5
            k = i * COL + j
            tess.append(f'<i id="em{n}t{k}" style="left:{x:.0f}px;top:{y:.0f}px;width:{tw:.0f}px;height:{th:.0f}px;'
                        f'background-image:url(assets/{foto[(k * 5 + i) % len(foto)]})"></i>')
            tl.append((k, d))
    giu = min(faccia["mento"] + 60, 1300)   # sotto le spalle torna il video vero: lì il ritaglio della persona è incerto
    maschera = f"linear-gradient(#000 0,#000 {giu}px,transparent {giu + 220}px)"
    r.camera.insert(0, f'<div class="el-muro" id="em{n}" style="background:{c.get("scuro", "#141414")};-webkit-mask-image:{maschera};mask-image:{maschera}">{"".join(tess)}</div>')
    sel = r.ritaglio(da - 0.1, a + 0.1)
    T = r.tl.append
    T(f'tl.set("#em{n}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:1}},{da:.3f});')
    for k, d in tl:
        t = da + d * 1.1
        T(f'tl.fromTo("#em{n}t{k}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(1.6)",immediateRender:false}},{t:.3f});')
    T(f'tl.to("[id^=em{n}t]",{{opacity:0,scale:.7,duration:.25,stagger:{{each:.01,from:"center"}}}},{a - 0.45:.3f});'
      f'tl.set("#em{n}",{{opacity:0}},{a:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});')
    r.suono_libreria("hyperframes/whoosh-short.mp3", da, 0.3)
    r.suono_libreria("hyperframes/sparkle.mp3", da + 0.3, 0.25)
    if e.get("etichetta"):
        m = len(r.corpo)
        y = max(_cima(faccia) - 120, 210)
        r.corpo.append(f'<div class="el-pill" id="em{m}p" style="left:50%;top:{y:.0f}px;transform:translateX(-50%);'
                       f'background:{c.get("accento", "#E86530")};color:#fff">{E(e["etichetta"])}</div>')
        tp = e.get("etichetta_da", da + 0.7)
        T(f'tl.fromTo("#em{m}p",{{opacity:0,scale:.4,xPercent:-50,x:0}},{{opacity:1,scale:1,xPercent:-50,duration:.35,ease:"back.out(2.5)",immediateRender:false}},{tp:.3f});'
          f'tl.to("#em{m}p",{{opacity:0,duration:.2}},{a - 0.45:.3f});')
        r.suono("pop", tp, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- capitolo
def capitolo(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    num = str(e.get("numero", "01"))
    y = max(_cima(faccia) - 220, 200)
    sinistra = _cx(faccia) >= 540 or True
    r.corpo.append(f'<div class="el-cap" id="ec{n}" style="left:70px;top:{y:.0f}px">'
                   f'<span class="el-fin"><span class="el-num" id="ec{n}n" style="font-size:190px;color:{c.get("accento_luce", "#FFB27A")}">{E(num)}</span></span>'
                   f'<i class="el-filo" id="ec{n}f" style="background:{c.get("testo", "#fff")}"></i>'
                   f'<span class="el-et" id="ec{n}e" style="background:{c.get("scuro", "#141414")};color:{c.get("testo", "#fff")}">{E(e.get("testo", "").upper())}</span></div>')
    T = r.tl.append
    T(f'tl.fromTo("#ec{n}n",{{yPercent:105}},{{yPercent:0,duration:.5,ease:"power3.out",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#ec{n}f",{{width:0}},{{width:60,duration:.3,ease:"power2.out",immediateRender:false}},{da + 0.3:.3f});'
      f'tl.fromTo("#ec{n}e",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.3,ease:"power2.out",immediateRender:false}},{da + 0.45:.3f});'
      f'tl.to("#ec{n}",{{opacity:0,y:-30,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    r.suono_libreria("hyperframes/whoosh-short.mp3", da, 0.25)
    r.suono("pop", da + 0.45, 0.2)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- nastro che scorre
def nastro(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    y = min(faccia["mento"] + 220, 1300)
    nastri = [(e.get("testo", ""), c.get("accento", "#E86530"), "#fff", -6, 1, 0)]
    if e.get("secondo"):
        nastri.append((e["secondo"], c.get("scuro", "#141414"), c.get("testo", "#fff"), 5, -1, 40))
    T = r.tl.append
    html_n = []
    for j, (testo, fondo, ink, gira, verso, dy) in enumerate(nastri):
        pezzo = f" {E(testo.upper())} &nbsp;•&nbsp;"
        riga = pezzo * 14
        html_n.append(f'<div class="el-nastro" id="en{n}r{j}" style="top:{y + dy:.0f}px;background:{fondo};color:{ink};'
                      f'transform:rotate({gira}deg)"><div id="en{n}t{j}">{riga}</div></div>')
        lungo = a - da
        T(f'tl.fromTo("#en{n}r{j}",{{opacity:0,x:{verso * 1400}}},{{opacity:1,x:0,duration:.45,ease:"power3.out",immediateRender:false}},{da + j * 0.12:.3f});'
          f'tl.fromTo("#en{n}t{j}",{{x:{-400 if verso > 0 else -1400}}},{{x:{-1400 if verso > 0 else -400},duration:{lungo:.2f},ease:"none",immediateRender:false}},{da:.3f});'
          f'tl.to("#en{n}r{j}",{{x:{-verso * 1400},duration:.4,ease:"power3.in"}},{a - 0.4:.3f});')
        r.suono_libreria("hyperframes/whoosh-short.mp3", da + j * 0.12, 0.25)
    # i nastri incrociati: il primo sopra
    r.corpo.append("".join(reversed(html_n)))
    r.nascondi.append((da, a))


TIPI = {"elenco": elenco, "scalata": scalata, "mosaico": mosaico, "capitolo": capitolo, "nastro": nastro}
