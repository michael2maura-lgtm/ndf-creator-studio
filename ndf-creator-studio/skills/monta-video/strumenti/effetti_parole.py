"""Effetti di parole, tasti e cartelli (18/11/2026), rifatti da noi guardando come si muovono gli effetti di
riferimento (mai copiato il codice). Motore grafica, tempi del video TAGLIATO. Mentre ci sono, i sottotitoli si nascondono.

 {"tipo": "colora", "da", "a", "testo": "la parte bella", "testo_da": t, "colora_da": t, "colori": "arcobaleno" (facoltativo)}
     Scritta che si colora: sopra la testa una frase in corsivo compare chiara, poi si accende lettera per lettera
     nei colori dello stile (o in un arcobaleno). Per la parte bella, la parola che piace.
 {"tipo": "carosello", "da", "a", "carte": [["il gancio", t], {"testo": "...", "t": t, "secondo": s}]}
     Carosello: davanti al petto una fila di carte scorre da destra a sinistra; ogni volta che nomini una cosa la sua
     carta va al centro e diventa la più grande. Carte con una scritta, un fotogramma del video ("secondo") o una foto
     di DATI/immagini ("immagine"). Da 2 a 6. Per i lavori, gli esempi, un elenco che si mostra.
 {"tipo": "tasti", "da", "a", "testo": "FIX", "testo_da": t}
     Tasti che piovono: cadono dall'alto tasti di una tastiera, qualcuno passa via, quelli della parola rimbalzano e
     si mettono in fila sul petto. Per una parola da commentare ("commenta FIX"), un codice. Max 8 lettere.
 {"tipo": "fumetto", "da", "a", "testo": "bla bla bla"}
     Fumetto: una nuvoletta bianca accanto alla testa, con la punta verso la bocca; le parole entrano una alla volta.
     Per una frase detta da altri, un pensiero, una battuta.
 {"tipo": "cartello", "da", "a", "sopra": "CON IL MIO METODO", "testo": "è tutto più semplice"}
     Cartello: la frase che chiude un ragionamento in un cartello scuro un po' storto, in maiuscolo, con una piccola
     etichetta colorata sopra. Per una conclusione, una regola, la frase da ricordare.
"""
import colorsys
import html

from effetti_carte import _cima, _cx, _foto

E = html.escape


def _css(r):
    if getattr(r, "css_parole", False):
        return
    r.css_parole = True
    for f in ("InterTight.ttf", "InstrumentSerif-Italic.ttf", "PlayfairDisplay-Italic.ttf"):
        r.font_extra(f)
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}"
        "@font-face{font-family:'ISerifI';src:url('assets/InstrumentSerif-Italic.ttf')}"
        "@font-face{font-family:'PlayI';src:url('assets/PlayfairDisplay-Italic.ttf');font-weight:400 900}"
        ".ep-riga{position:absolute;left:20px;right:20px;text-align:center;white-space:nowrap;z-index:31;line-height:1;"
        "text-shadow:0 0 26px rgba(0,0,0,.6),0 0 8px rgba(0,0,0,.45),0 4px 14px rgba(0,0,0,.55)}"
        ".ep-riga span{display:inline-block}"
        ".ep-fila{position:absolute;left:0;top:0;z-index:31}"
        ".ep-card{position:absolute;border-radius:24px;box-shadow:0 14px 30px rgba(0,0,0,.42);overflow:hidden;display:flex;"
        "align-items:center;justify-content:center;text-align:center;font-family:'Inter Tight';font-weight:800;line-height:1.05;"
        "padding:18px;box-sizing:border-box;border:5px solid #fff}"
        ".ep-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}"
        ".ep-tasto{position:absolute;border-radius:24px;background:linear-gradient(#FFFFFF,#ECE9E3);display:grid;place-items:center;"
        "font-family:'Inter Tight';font-weight:800;color:#26232A;z-index:31;opacity:0;"
        "box-shadow:inset 0 -6px 0 rgba(0,0,0,.06),0 9px 0 #BEB8AE,0 20px 30px rgba(0,0,0,.42)}"
        ".ep-fum{position:absolute;z-index:31;opacity:0;background:#fff;color:#1D1B20;border-radius:56px;"
        "padding:26px 40px 30px;font:700 54px/1.12 PlayI;box-shadow:0 14px 30px rgba(0,0,0,.35);max-width:440px;box-sizing:border-box}"
        ".ep-fum span{display:inline-block;opacity:0}"
        ".ep-cart{position:absolute;left:130px;width:820px;z-index:31;opacity:0;border-radius:30px;padding:40px 52px 48px;"
        "box-sizing:border-box;box-shadow:0 20px 44px rgba(0,0,0,.45);font-family:'Inter Tight'}"
        ".ep-cart .ep-et{font-weight:800;font-size:28px;letter-spacing:.16em;margin-bottom:16px}"
        ".ep-cart .ep-gr{font-weight:900;letter-spacing:-.01em;line-height:1.02}"
        ".ep-cart .ep-gr span{display:inline-block;opacity:0;margin-right:.24em}"
        "</style>")


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _misto(a, b, u):
    return "#" + "".join(f"{int(x + (y - x) * u):02X}" for x, y in zip(_hex(a), _hex(b)))


# ---------------------------------------------------------------- scritta che si colora
def colora(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    testo = e.get("testo", "")
    td = e.get("testo_da", da)
    lettere = list(testo)
    q = max(sum(1 for x in lettere if x != " "), 1)
    cd = max(e.get("colora_da", td + 0.6), td + 0.35)
    dim = max(min(150, int(1000 / (max(len(testo), 3) * 0.42))), 70)
    y = max(_cima(faccia) - dim * 1.05, 210)
    sposta = max(min(_cx(faccia) - 540, 120), -120)
    if e.get("colori") == "arcobaleno":
        tinta = lambda u: "#" + "".join(f"{int(v * 255):02X}" for v in colorsys.hls_to_rgb(0.98 - u * 0.8, 0.62, 0.95))
    else:
        a1, a2 = c.get("accento", "#E86530"), c.get("accento_luce", "#FFB27A")
        tinta = lambda u: _misto(a1, a2, u)
    spans, k = [], 0
    for i, ch in enumerate(lettere):
        if ch == " ":
            spans.append("&nbsp;")
            continue
        spans.append(f'<span id="eo{n}l{k}">{E(ch)}</span>')
        k += 1
    r.corpo.append(f'<div class="ep-riga" id="eo{n}" style="top:{y:.0f}px;transform:translateX({sposta:.0f}px);font-family:PlayI;'
                   f'font-weight:700;font-size:{dim}px;color:#FBF7F0;opacity:0">{"".join(spans)}</div>')
    T = r.tl.append
    T(f'tl.fromTo("#eo{n}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:.35,ease:"power2.out",immediateRender:false}},{td:.3f});')
    passo = min(0.07, 0.9 / q)
    for k in range(q):
        u = k / max(q - 1, 1)
        t = cd + k * passo
        T(f'tl.fromTo("#eo{n}l{k}",{{color:"#FBF7F0",scale:1}},{{color:"{tinta(u)}",scale:1.22,duration:.14,ease:"power2.out",immediateRender:false}},{t:.3f});'
          f'tl.to("#eo{n}l{k}",{{scale:1,duration:.2,ease:"power2.inOut"}},{t + 0.14:.3f});')
    T(f'tl.to("#eo{n}",{{opacity:0,y:-20,duration:.3}},{a - 0.3:.3f});')
    r.suono_libreria("hyperframes/sparkle.mp3", cd, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- carosello
def carosello(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    carte = [x if isinstance(x, dict) else {"testo": x[0], "t": x[1]} for x in e.get("carte", [])[:6]]
    if not carte:
        return
    W, H, P = 240, 320, 290
    y = min(faccia["mento"] + 230, 1330) - H / 2
    cx = 540 + max(min(_cx(faccia) - 540, 80), -80)
    tinte = [(c.get("accento", "#E86530"), "#fff"), ("#FBF8F2", c.get("scuro", "#141414")),
             (c.get("scuro", "#141414"), c.get("testo", "#fff")), (c.get("accento_luce", "#FFB27A"), c.get("scuro", "#141414"))]
    pezzi = []
    for k, ct in enumerate(carte):
        fondo, ink = tinte[k % len(tinte)]
        dentro = ""
        if ct.get("immagine") or ct.get("secondo") is not None:
            f = _foto(r, f"car-{n}-{k}.jpg", ct.get("secondo"), ct.get("immagine"), W, H, faccia)
            if f:
                dentro = f'<img src="assets/{f}">'
        testo = ct.get("testo", "")
        if testo and dentro:
            dentro += (f'<b style="position:absolute;left:10px;right:10px;bottom:12px;background:{fondo};color:{ink};border-radius:12px;'
                       f'padding:8px 4px;font-size:34px">{E(testo)}</b>')
        elif testo:
            dim = max(min(52, int(200 / (max(max(len(p) for p in testo.split()), 3) * 0.62))), 28)
            dentro = f'<span style="font-size:{dim}px">{E(testo)}</span>'
        pezzi.append(f'<div class="ep-card" id="ek{n}c{k}" style="left:{k * P}px;top:0;width:{W}px;height:{H}px;background:{fondo};color:{ink}">{dentro}</div>')
    r.corpo.append(f'<div class="ep-fila" id="ek{n}" style="top:{y:.0f}px;opacity:0">{"".join(pezzi)}</div>')
    T = r.tl.append
    centro = lambda k: cx - k * P - W / 2
    stato = lambda k, j: (1.15, 1) if k == j else ((0.86, 0.8) if abs(k - j) == 1 else (0.78, 0.62))   # luce, non trasparenza: la felpa non deve passare
    t0 = max(carte[0].get("t", da), da)
    T(f'tl.set("#ek{n}",{{opacity:1}},{da:.3f});'
      f'tl.fromTo("#ek{n}",{{x:{1100:.0f}}},{{x:{centro(0):.0f},duration:.6,ease:"power3.out",immediateRender:false}},{max(t0 - 0.35, da):.3f});')
    for k in range(len(carte)):
        s, o = stato(k, 0)
        T(f'tl.set("#ek{n}c{k}",{{scale:{s},filter:"brightness({o})",zIndex:{10 - abs(k)}}},{da:.3f});')
    r.suono_libreria("hyperframes/whoosh-short.mp3", max(t0 - 0.35, da), 0.25)
    for j in range(1, len(carte)):
        t = max(carte[j].get("t", da + j * 0.6), da + 0.5) - 0.2
        T(f'tl.to("#ek{n}",{{x:{centro(j):.0f},duration:.5,ease:"power3.inOut"}},{t:.3f});')
        for k in range(len(carte)):
            s, o = stato(k, j)
            T(f'tl.to("#ek{n}c{k}",{{scale:{s},filter:"brightness({o})",duration:.5,ease:"power3.inOut"}},{t:.3f});'
              f'tl.set("#ek{n}c{k}",{{zIndex:{10 - abs(k - j)}}},{t + 0.25:.3f});')
        r.suono_libreria("hyperframes/whoosh-short.mp3", t, 0.2)
    T(f'tl.to("#ek{n}",{{x:"-=700",opacity:0,duration:.4,ease:"power2.in"}},{a - 0.4:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- tasti che piovono
def _tasto(id_, ch, lato, x, y):
    return (f'<div class="ep-tasto" id="{id_}" style="left:{x - lato / 2:.0f}px;top:{y - lato / 2:.0f}px;width:{lato}px;height:{lato}px;'
            f'font-size:{lato * 0.42:.0f}px">{E(ch)}</div>')


def tasti(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    parola = [ch for ch in e.get("testo", "").upper() if ch.strip()][:8]
    if not parola:
        return
    td = max(e.get("testo_da", da + 0.4), da)
    q = len(parola)
    lato = min(130, int(880 / q) - 18)
    passo = lato + 16
    y = min(faccia["mento"] + 240, 1320)
    cx = 540 + max(min(_cx(faccia) - 540, 80), -80)
    pezzi = []
    giri = [-32, 26, -18, 34, -24, 20, -30, 16]
    for i, ch in enumerate(parola):
        pezzi.append(_tasto(f"et{n}k{i}", ch, lato, cx + (i - (q - 1) / 2) * passo, y))
    # tasti che passano e basta
    vie = [(170, "Q", -30), (930, "Z", 28), (380, "M", 16), (760, "K", -22)]
    for j, (x, ch, g) in enumerate(vie):
        pezzi.append(_tasto(f"et{n}v{j}", ch, 104, x, -120))
    r.corpo.append(f'<div id="et{n}">{"".join(pezzi)}</div>')
    T = r.tl.append
    for j, (x, ch, g) in enumerate(vie):
        t = da + j * 0.13
        T(f'tl.fromTo("#et{n}v{j}",{{opacity:1,y:0,rotation:{g}}},{{y:2300,rotation:{g + 200},duration:1.0,ease:"power1.in",immediateRender:false}},{t:.3f});')
    for i in range(q):
        t = td + i * 0.09
        T(f'tl.fromTo("#et{n}k{i}",{{opacity:1,y:-1500,rotation:{giri[i % 8]}}},{{y:0,rotation:{giri[i % 8] // 9},duration:.7,ease:"bounce.out",immediateRender:false}},{t:.3f});')
        r.suono_libreria("hyperframes/key-press.mp3", t + 0.35, 0.45)
    T(f'tl.to("[id^=et{n}k]",{{y:900,rotation:"+=40",duration:.45,ease:"power2.in",stagger:.04}},{a - 0.45:.3f});'
      f'tl.set("#et{n}",{{opacity:0}},{a:.3f});')
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- fumetto
def fumetto(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    parole = e.get("testo", "").split()
    destra = _cx(faccia) <= 540   # la nuvoletta va dal lato con più spazio
    stacco = 85                    # aria tra la testa e la nuvoletta (Michael, 18/11: era troppo vicina)
    spazio = (1080 - faccia["destra"] if destra else faccia["sinistra"]) - stacco - 36
    stile = ""
    if spazio >= 235:
        # accanto alla testa, all'altezza della tempia, con la punta verso il viso
        y = max(faccia["occhi"] - 270, 210)
        stile = f"max-width:{spazio:.0f}px;font-size:42px;padding:20px 26px 24px;"
        if destra:
            lato = f"left:{faccia['destra'] + stacco:.0f}px"
            punta = ('<svg width="70" height="60" viewBox="0 0 70 60" style="position:absolute;left:-44px;bottom:18px">'
                     '<path d="M70 0 L0 52 L70 34 Z" fill="#fff"/></svg>')
            origine = "0% 80%"
        else:
            lato = f"right:{1080 - faccia['sinistra'] + stacco:.0f}px"
            punta = ('<svg width="70" height="60" viewBox="0 0 70 60" style="position:absolute;right:-44px;bottom:18px">'
                     '<path d="M0 0 L70 52 L0 34 Z" fill="#fff"/></svg>')
            origine = "100% 80%"
    else:
        # niente spazio ai lati: sopra la testa, spostata dal lato libero, ben staccata dai capelli
        y = max(_cima(faccia) - 230, 200)
        if destra:
            lato = "right:60px"
            punta = ('<svg width="90" height="70" viewBox="0 0 90 70" style="position:absolute;left:38px;bottom:-52px">'
                     '<path d="M0 0 L8 66 L66 0 Z" fill="#fff"/></svg>')
            origine = "0% 100%"
        else:
            lato = "left:60px"
            punta = ('<svg width="90" height="70" viewBox="0 0 90 70" style="position:absolute;right:38px;bottom:-52px">'
                     '<path d="M90 0 L82 66 L24 0 Z" fill="#fff"/></svg>')
            origine = "100% 100%"
    spans = " ".join(f'<span id="ef{n}w{k}">{E(p)}</span>' for k, p in enumerate(parole))
    r.corpo.append(f'<div class="ep-fum" id="ef{n}" style="{lato};top:{y:.0f}px;{stile}transform-origin:{origine}">{spans}{punta}</div>')
    T = r.tl.append
    gira = 4 if destra else -4
    T(f'tl.fromTo("#ef{n}",{{opacity:0,scale:.2,rotation:{-gira * 2}}},{{opacity:1,scale:1,rotation:{gira},duration:.4,ease:"back.out(1.5)",immediateRender:false}},{da:.3f});')
    for k in range(len(parole)):
        T(f'tl.fromTo("#ef{n}w{k}",{{opacity:0,y:8}},{{opacity:1,y:0,duration:.16,immediateRender:false}},{da + 0.15 + k * 0.12:.3f});')
    T(f'tl.to("#ef{n}",{{opacity:0,scale:.6,duration:.25,ease:"power2.in"}},{a - 0.25:.3f});')
    r.suono("pop", da, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- cartello
def cartello(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    testo = e.get("testo", "").upper()
    parole = testo.split()
    dim = 84 if len(testo) <= 22 else (72 if len(testo) <= 40 else 60)
    righe = max(1, int(len(testo) * dim * 0.62 / 716) + 1)
    alto = 40 + 44 + righe * dim * 1.02 + 48
    y = min(faccia["mento"] + 150, 1560 - alto)
    sopra = f'<div class="ep-et" style="color:{c.get("accento_luce", "#FFB27A")}">{E(e["sopra"].upper())}</div>' if e.get("sopra") else ""
    spans = "".join(f'<span id="eg{n}w{k}">{E(p)}</span>' for k, p in enumerate(parole))
    r.corpo.append(f'<div class="ep-cart" id="eg{n}" style="top:{y:.0f}px;background:{c.get("scuro", "#141414")}F2;color:{c.get("testo", "#fff")}">'
                   f'{sopra}<div class="ep-gr" style="font-size:{dim}px">{spans}</div></div>')
    T = r.tl.append
    T(f'tl.fromTo("#eg{n}",{{opacity:0,scale:.85,rotation:-6,y:40}},{{opacity:1,scale:1,rotation:-2,y:0,duration:.4,ease:"back.out(1.8)",immediateRender:false}},{da:.3f});')
    for k in range(len(parole)):
        T(f'tl.fromTo("#eg{n}w{k}",{{opacity:0,y:24}},{{opacity:1,y:0,duration:.22,ease:"power2.out",immediateRender:false}},{da + 0.25 + k * 0.1:.3f});')
    T(f'tl.to("#eg{n}",{{opacity:0,y:30,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    r.suono("pop", da, 0.25)
    r.suono_libreria("hyperframes/whoosh-short.mp3", da, 0.15)
    r.nascondi.append((da, a))


TIPI = {"colora": colora, "carosello": carosello, "tasti": tasti, "fumetto": fumetto, "cartello": cartello}
