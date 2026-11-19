"""Effetti che cambiano la scena attorno alla persona (18/11/2026), rifatti da noi guardando come si muovono gli
effetti di riferimento fotogramma per fotogramma (mai copiato il codice). Motore grafica, tempi del video TAGLIATO.
Mentre ci sono, i sottotitoli si nascondono.

 {"tipo": "dentro", "da", "a", "colore": "#5F8F8A" (facoltativo)}
     Sfondo che si apre: con un lampo la stanza dietro di te diventa un fondo di luci sfocate che si muove piano,
     tu resti vero con un filo bianco attorno. Per "cambia tutto", "un altro mondo", un prima e dopo. 2,5-5 s.
 {"tipo": "sfocato", "da", "a", "sopra": "TI SERVE", "testo": "Metodo", "testo_da": t}
     Sfondo sfocato con scritta: sul petto si accendono delle luci tonde, poi tutto va fuori fuoco e compare una parola
     grande in corsivo elegante con una riga piccola sopra; poi torna a fuoco. Per la parola chiave di una frase.
 {"tipo": "raggi", "da", "a", "sopra": "PER FARTI NOTARE", "testo": "basta un'idea chiara", "testo_da": t}
     Luce dietro la testa: dietro di te si aprono dei raggi di luce calda che girano piano, la stanza in basso si
     scurisce e sul petto compaiono una riga piccola e una frase in corsivo dorato. Per un'idea importante, una rivelazione.
 {"tipo": "collage", "da", "a", "righe": [["FATTI", t], ["NOTARE", t], ["COSÌ", t]], "cerchio": 1, "sottolinea": 2}
     Collage di carta: lo sfondo diventa un collage (carta strappata gialla e marrone, quaderno a quadretti,
     scarabocchi), tu diventi un adesivo con il bordo bianco e in alto le parole si compongono con lettere ritagliate
     dai giornali. "cerchio": la riga cerchiata in rosso, "sottolinea": la riga sottolineata. Per un gancio forte, 1 volta.
 {"tipo": "reel", "da", "a", "testo": "riga sotto il nome", "segui": t, "cuore": t, "adesivo": "EDIT" (facoltativo)}
     Il video in un reel: l'inquadratura si stacca e diventa piccola, dentro la cornice di un reel di Instagram con
     il tuo nome, il tasto Segui, il cuore e la barra che scorre; dietro, il video sfocato e scuro. "segui" e "cuore":
     i secondi in cui vengono toccati. Per "pubblichi", "il tuo reel", "i tuoi contenuti".
"""
import html
import json
import os
import random
import subprocess

from comune import DATI, FFMPEG

E = html.escape


def _css(r):
    if getattr(r, "css_scena", False):
        return
    r.css_scena = True
    for f in ("InterTight.ttf", "InstrumentSerif-Regular.ttf", "InstrumentSerif-Italic.ttf", "Anton-Regular.ttf",
              "ArchivoBlack-Regular.ttf", "BodoniModa.ttf", "BodoniModa-Italic.ttf", "PlayfairDisplay-Italic.ttf", "BebasNeue-Regular.ttf"):
        r.font_extra(f)
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}"
        "@font-face{font-family:'ISerif';src:url('assets/InstrumentSerif-Regular.ttf')}"
        "@font-face{font-family:'ISerifI';src:url('assets/InstrumentSerif-Italic.ttf')}"
        "@font-face{font-family:'Anton';src:url('assets/Anton-Regular.ttf')}"
        "@font-face{font-family:'ArchivoBlack';src:url('assets/ArchivoBlack-Regular.ttf')}"
        "@font-face{font-family:'BodoniS';src:url('assets/BodoniModa.ttf');font-weight:400 900}"
        "@font-face{font-family:'BodoniSI';src:url('assets/BodoniModa-Italic.ttf');font-weight:400 900}"
        "@font-face{font-family:'PlayI';src:url('assets/PlayfairDisplay-Italic.ttf');font-weight:400 900}"
        "@font-face{font-family:'Bebas';src:url('assets/BebasNeue-Regular.ttf')}"
        # scritte: riga piccola spaziata + frase grande
        ".sc-pic{position:absolute;left:0;right:0;text-align:center;font:700 30px 'Inter Tight';letter-spacing:.42em;"
        "color:#fff;opacity:0;z-index:31;text-shadow:0 2px 12px rgba(0,0,0,.6);padding-left:.42em}"
        ".sc-gr{position:absolute;left:30px;right:30px;text-align:center;opacity:0;z-index:31;line-height:1;white-space:nowrap;"
        "text-shadow:0 6px 30px rgba(0,0,0,.45)}"
        # luci tonde
        ".sc-bk{position:absolute;border-radius:50%;opacity:0;z-index:30;"
        "background:radial-gradient(circle,rgba(255,244,214,.9) 0%,rgba(255,240,205,.75) 62%,rgba(255,250,235,.95) 70%,rgba(255,240,205,0) 76%);"
        "filter:blur(1.5px)}"
        ".sc-velo{position:absolute;inset:0;z-index:29;opacity:0;pointer-events:none}"
        # raggi
        ".sc-raggi{position:absolute;width:2400px;height:2400px;opacity:0;pointer-events:none;mix-blend-mode:screen}"
        ".sc-raggi i{position:absolute;inset:0;border-radius:50%}"
        # collage
        ".sc-col{position:absolute;inset:0;opacity:0}"
        ".sc-rg{position:absolute;left:30px;right:30px;display:flex;justify-content:center;align-items:center;gap:6px;z-index:31;opacity:1}"
        ".sc-l{display:inline-block;padding:6px 10px 4px;line-height:1;opacity:0;box-shadow:0 4px 8px rgba(0,0,0,.25)}"
        ".sc-segno{position:absolute;inset:0;z-index:32;pointer-events:none}"
        ".sc-segno path{fill:none;stroke:#D6262E;stroke-width:7;stroke-linecap:round}"
        # reel
        ".sc-dietro{position:absolute;inset:-80px;width:1240px;height:2080px;object-fit:cover;z-index:4;opacity:0;"
        "filter:blur(34px) brightness(.38) saturate(.7)}"
        ".sc-ui{position:absolute;z-index:31;opacity:0;font-family:'Inter Tight';color:#fff;pointer-events:none}"
        ".sc-ic{position:absolute;right:26px;display:flex;flex-direction:column;align-items:center;gap:30px}"
        ".sc-ic svg{width:54px;height:54px;filter:drop-shadow(0 2px 4px rgba(0,0,0,.4))}"
        ".sc-chi{position:absolute;left:24px;bottom:58px;right:110px}"
        ".sc-chi .r1{display:flex;align-items:center;gap:12px;font-weight:700;font-size:28px;text-shadow:0 1px 4px rgba(0,0,0,.5)}"
        ".sc-chi img{width:54px;height:54px;border-radius:50%;object-fit:cover;border:2px solid #fff}"
        ".sc-chi .sg{border:2px solid rgba(255,255,255,.8);border-radius:9px;padding:4px 12px;font-size:20px;font-weight:700}"
        ".sc-chi .r2{font-size:25px;margin-top:10px;opacity:.95;text-shadow:0 1px 4px rgba(0,0,0,.5)}"
        ".sc-bar{position:absolute;left:0;right:0;bottom:0;height:5px;background:rgba(255,255,255,.3)}"
        ".sc-bar i{display:block;height:100%;width:100%;background:#fff;transform-origin:0 50%;transform:scaleX(0)}"
        ".sc-dito{position:absolute;width:56px;height:56px;border-radius:50%;background:rgba(255,255,255,.85);"
        "box-shadow:0 0 0 8px rgba(255,255,255,.3);opacity:0}"
        ".sc-ade{position:absolute;display:flex;align-items:center;gap:10px;background:#fff;color:#111;border-radius:30px;"
        "padding:8px 18px 8px 8px;font-weight:900;font-size:26px;box-shadow:0 8px 20px rgba(0,0,0,.35)}"
        ".sc-ade i{width:34px;height:34px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#9DB3FF,#4C6CF0)}"
        "</style>")


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _bokeh(r, colore="#5F8F8A"):
    """Immagine di luci sfocate (fatta qui, sempre uguale per lo stesso colore): fondo sfumato + cerchi morbidi."""
    from PIL import Image, ImageDraw, ImageFilter
    nome = f"bokeh-{colore.lstrip('#')}.png"
    dest = os.path.join(r.assets, nome)
    if os.path.exists(dest):
        return nome
    W, H = 540, 960
    base = _hex(colore)
    scuro = tuple(int(v * 0.42) for v in base)
    chiaro = tuple(min(255, int(v * 1.25 + 20)) for v in base)
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            k = min(1, ((x - W * 0.35) ** 2 / (W * 0.9) ** 2 + (y - H * 0.3) ** 2 / (H * 0.85) ** 2) ** 0.5)
            px[x, y] = tuple(int(c * (1 - k) + s * k) for c, s in zip(chiaro, scuro))
    luci = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(11)
    for _ in range(34):
        rr = rnd.randint(28, 95)
        cx, cy = rnd.randint(-20, W + 20), rnd.randint(-20, int(H * 0.8))
        a = rnd.randint(50, 140)
        tinta = rnd.choice([(255, 255, 255), (220, 240, 245), (190, 215, 255), chiaro])
        d = ImageDraw.Draw(luci)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tinta + (a,))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255, min(255, a + 60)), width=2)
    luci = luci.filter(ImageFilter.GaussianBlur(2.2))
    im = Image.alpha_composite(im.convert("RGBA"), luci).convert("RGB").resize((1080, 1920), Image.LANCZOS)
    im.save(dest)
    return nome


def _contorno(spessore=3, colore="#fff"):
    """Filo attorno al ritaglio, come proprietà GSAP: filter:"drop-shadow(...) ..." """
    s = spessore
    ombre = " ".join(f"drop-shadow({x}px {y}px 0 {colore})" for x, y in ((s, 0), (-s, 0), (0, s), (0, -s)))
    return f'filter:"{ombre} drop-shadow(0 10px 18px rgba(0,0,0,.35))"'


# ---------------------------------------------------------------- dentro (sfondo che si apre)
def dentro(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    col = e.get("colore", "#5F8F8A")
    img = _bokeh(r, col)
    n = len(r.camera)
    # le luci come sfondo (dietro il ritaglio, sopra il video)
    r.camera.insert(0, f'<div id="sd{n}f" style="position:absolute;inset:0;opacity:0;background:url(assets/{img}) center/cover"></div>')
    vero = r.ritaglio(da - 0.1, a + 0.1)
    T = r.tl.append
    T(f'tl.set("{vero}",{{opacity:1,{_contorno(3)}}},{da:.3f});'
      f'tl.fromTo("{vero}",{{scale:1.03}},{{scale:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sd{n}f",{{opacity:0,scale:1.12}},{{opacity:1,scale:1,duration:.35,ease:"power2.out",immediateRender:false}},{da:.3f});'
      f'tl.to("#sd{n}f",{{scale:1.06,x:-20,duration:{max(a - da - 0.6, 0.3):.2f},ease:"none"}},{da + 0.35:.3f});'
      f'tl.to("#sd{n}f",{{opacity:0,duration:.25}},{a - 0.25:.3f});'
      f'tl.set("{vero}",{{opacity:0,filter:"none"}},{a:.3f});')
    r.flash(da, 0.35)
    r.suono_libreria("hyperframes/sparkle.mp3", da, 0.3)
    r.suono("transizione", da, 0.32)
    r.suono("transizione", a - 0.25, 0.25)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- sfocato (fuori fuoco + parola)
def _luci_tonde(r, n, cx, cy, quante=7):
    rnd = random.Random(n)
    pezzi = []
    for j in range(quante):
        rr = rnd.randint(46, 62)
        x = cx + rnd.randint(-170, 170) - rr
        y = cy + rnd.randint(-70, 70) - rr
        pezzi.append(f'<i class="sc-bk" id="sb{n}k{j}" style="left:{x}px;top:{y}px;width:{rr * 2}px;height:{rr * 2}px"></i>')
    return "".join(pezzi)


def sfocato(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    td = e.get("testo_da", da + 0.7)
    testo = e.get("testo", "")
    dim = max(min(210, int(950 / (max(len(testo), 3) * 0.42))), 90)
    y = min(faccia["mento"] + 120, 1280)
    cx = (faccia["sinistra"] + faccia["destra"]) / 2
    luci = _luci_tonde(r, n, cx, y + 60)
    r.corpo.append(f'<div>{luci}</div>'
                   f'<div class="sc-pic" id="sb{n}p" style="top:{y:.0f}px">{E(e.get("sopra", "").upper())}</div>'
                   f'<div class="sc-gr" id="sb{n}g" style="top:{y + 48:.0f}px;font-family:ISerifI;font-size:{dim}px;color:#F6EFE2">{E(testo)}</div>')
    T = r.tl.append
    fuori = max(td - 0.15, da + 0.3)
    T(f'tl.fromTo("#sb{n}k0,#sb{n}k1,#sb{n}k2,#sb{n}k3,#sb{n}k4,#sb{n}k5,#sb{n}k6",{{opacity:0,scale:.3}},{{opacity:1,scale:1,duration:.3,stagger:.04,ease:"back.out(2)",immediateRender:false}},{da:.3f});'
      f'tl.to("[id^=sb{n}k]",{{opacity:0,scale:1.4,duration:.3,stagger:.02}},{fuori:.3f});'
      f'tl.fromTo("#bg",{{filter:"blur(0px)"}},{{filter:"blur(16px) brightness(.88)",duration:.35,ease:"power2.out",immediateRender:false}},{fuori:.3f});'
      f'tl.fromTo("#sb{n}p",{{opacity:0,y:10}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{td - 0.1:.3f});'
      f'tl.fromTo("#sb{n}g",{{opacity:0,scale:1.15,filter:"blur(12px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.45,ease:"power3.out",immediateRender:false}},{td:.3f});'
      f'tl.to(["#sb{n}p","#sb{n}g"],{{opacity:0,filter:"blur(10px)",duration:.3}},{a - 0.55:.3f});'
      f'tl.to("#bg",{{filter:"blur(0px) brightness(1)",duration:.35}},{a - 0.5:.3f});tl.set("#bg",{{filter:"none"}},{a:.3f});')
    r.suono("pop", da, 0.2)
    r.suono_libreria("hyperframes/whoosh-short.mp3", fuori, 0.25)
    r.suono_libreria("hyperframes/sparkle.mp3", td, 0.25)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- raggi (luce dietro la testa)
def raggi(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    td = e.get("testo_da", da + 0.6)
    sel = r.ritaglio(da - 0.1, a + 0.1)
    cima = r.cima_testa(r.ultimo_ritaglio, 0.2) or faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
    cx = (faccia["sinistra"] + faccia["destra"]) / 2
    cy = cima + (faccia["occhi"] - cima) * 0.35
    n = len(r.camera)
    luce = "255,247,226"
    r.camera.insert(0,
        f'<div class="sc-raggi" id="sr{n}" style="left:{cx - 1200:.0f}px;top:{cy - 1200:.0f}px">'
        f'<i id="sr{n}a" style="background:repeating-conic-gradient(from 0deg,rgba({luce},.55) 0deg 2.2deg,rgba({luce},0) 4deg 13deg);'
        f'-webkit-mask-image:radial-gradient(circle,#000 4%,rgba(0,0,0,.55) 22%,transparent 48%);filter:blur(9px)"></i>'
        f'<i id="sr{n}b" style="background:repeating-conic-gradient(from 6deg,rgba({luce},.35) 0deg 4deg,rgba({luce},0) 6deg 23deg);'
        f'-webkit-mask-image:radial-gradient(circle,#000 6%,rgba(0,0,0,.4) 26%,transparent 46%);filter:blur(16px)"></i>'
        f'<i style="background:radial-gradient(circle,rgba(255,253,244,1) 0%,rgba({luce},.85) 5%,rgba({luce},.35) 13%,rgba({luce},0) 30%)"></i></div>')
    m = len(r.corpo)
    y = min(faccia["mento"] + 150, 1300)
    testo = e.get("testo", "")
    dim = max(min(104, int(1000 / (max(len(testo), 3) * 0.4))), 54)
    r.corpo.append(f'<div class="sc-velo" id="sr{m}v" style="background:linear-gradient(rgba(0,0,0,0) 45%,rgba(0,0,0,.62) 100%)"></div>'
                   f'<div class="sc-pic" id="sr{m}p" style="top:{y:.0f}px;font-size:32px">{E(e.get("sopra", "").upper())}</div>'
                   f'<div class="sc-gr" id="sr{m}g" style="top:{y + 52:.0f}px;font-family:ISerifI;font-size:{dim}px;color:#F1DB8E;white-space:normal">{E(testo)}</div>')
    T = r.tl.append
    T(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
      f'tl.fromTo("#sr{n}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.7,ease:"power2.out",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sr{n}a",{{rotation:0}},{{rotation:14,duration:{a - da:.2f},ease:"none",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sr{n}b",{{rotation:0}},{{rotation:-10,duration:{a - da:.2f},ease:"none",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sr{m}v",{{opacity:0}},{{opacity:1,duration:.5,immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#bg",{{filter:"brightness(1)"}},{{filter:"brightness(.82)",duration:.5,immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sr{m}p",{{opacity:0,letterSpacing:".2em"}},{{opacity:1,letterSpacing:".42em",duration:.5,immediateRender:false}},{td - 0.25:.3f});'
      f'tl.fromTo("#sr{m}g",{{opacity:0,y:16,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.5,ease:"power2.out",immediateRender:false}},{td:.3f});'
      f'tl.to(["#sr{n}","#sr{m}v","#sr{m}p","#sr{m}g"],{{opacity:0,duration:.4}},{a - 0.4:.3f});'
      f'tl.to("#bg",{{filter:"brightness(1)",duration:.4}},{a - 0.4:.3f});tl.set("#bg",{{filter:"none"}},{a:.3f});')
    r.suono_libreria("hyperframes/riser.mp3", max(da - 0.4, 0), 0.18)
    r.suono_libreria("hyperframes/sparkle.mp3", da + 0.1, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- collage di carta
_CARTE = [("#1D4FB5", "#fff", "'Inter Tight'", 900), ("#fff", "#111", "PlayI", 900), ("#111", "#F4D23C", "Anton", 400),
          ("#E9DFC8", "#111", "ArchivoBlack", 400), ("#D6262E", "#fff", "'Inter Tight'", 900), ("#F4D23C", "#111", "Bebas", 400),
          ("#fff", "#D6262E", "Anton", 400), ("#C9A06A", "#111", "PlayI", 900), ("#111", "#fff", "ArchivoBlack", 400),
          ("#F2EEE4", "#1D4FB5", "Bebas", 400)]   # solo caratteri pieni: quelli sottili facevano sembrare la H due I


def _strappo(punti, rnd, ampiezza=14):
    """Un bordo strappato: tra un punto e l'altro tanti dentini a caso."""
    out = []
    for (x1, y1), (x2, y2) in zip(punti, punti[1:] + punti[:1]):
        passi = max(int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 26), 1)
        for k in range(passi):
            t = k / passi
            out.append(f"{x1 + (x2 - x1) * t + rnd.uniform(-ampiezza, ampiezza) * (y1 == y2 and 0 or 1):.0f},"
                       f"{y1 + (y2 - y1) * t + rnd.uniform(-ampiezza, ampiezza) * (x1 == x2 and 0 or 1):.0f}")
    return " ".join(out)


def _scarabocchio(x, y, w, h, righe, rnd):
    d = f"M{x},{y}"
    for k in range(righe):
        d += f" L{x + w + rnd.uniform(-20, 20):.0f},{y + h * (k + 0.5) / righe:.0f} L{x + rnd.uniform(-20, 20):.0f},{y + h * (k + 1) / righe:.0f}"
    return d


def collage(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    rnd = random.Random(5)
    n = len(r.camera)
    # il fondo di carta (dietro di te, sopra il video)
    giallo = _strappo([(-40, 1060), (760, 1010), (720, 1380), (-40, 1420)], rnd, 16)
    marrone = _strappo([(520, 1180), (1120, 1150), (1120, 1960), (470, 1960)], rnd, 14)
    quaderno = _strappo([(-40, 1390), (640, 1420), (600, 1960), (-40, 1960)], rnd, 12)
    blu = _scarabocchio(70, 120, 900, 330, 9, rnd)
    blu2 = _scarabocchio(60, 1110, 330, 170, 7, rnd)
    rosso = _scarabocchio(70, 1500, 200, 130, 6, rnd)
    r.camera.insert(0,
        f'<div class="sc-col" id="sc{n}"><svg viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;inset:0">'
        f'<defs><filter id="sc{n}t"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/>'
        f'<feColorMatrix values="0 0 0 0 .45 0 0 0 0 .4 0 0 0 0 .33 0 0 0 .09 0"/></filter>'
        f'<pattern id="sc{n}q" width="44" height="44" patternUnits="userSpaceOnUse"><rect width="44" height="44" fill="#FBFBF8"/>'
        f'<path d="M44 0V44M0 44H44" stroke="#A9C3E6" stroke-width="2"/></pattern></defs>'
        f'<rect width="1080" height="1920" fill="#F3EEE2"/>'
        f'<path d="{blu}" stroke="#8D9DDA" stroke-width="22" fill="none" stroke-linejoin="round" opacity=".75"/>'
        f'<polygon points="{quaderno}" fill="url(#sc{n}q)" style="filter:drop-shadow(0 -4px 6px rgba(0,0,0,.18))"/>'
        f'<polygon points="{marrone}" fill="#CFA56C" style="filter:drop-shadow(-4px 0 6px rgba(0,0,0,.2))"/>'
        f'<polygon points="{giallo}" fill="#F7DC4A" style="filter:drop-shadow(0 6px 8px rgba(0,0,0,.2))"/>'
        f'<path d="{blu2}" stroke="#3E57B8" stroke-width="12" fill="none" opacity=".85"/>'
        f'<path d="{rosso}" stroke="#E0434B" stroke-width="9" fill="none" opacity=".85"/>'
        f'<path d="M70 1700 q20 -40 40 0 q20 -40 40 0 q20 -40 40 0 q20 -40 40 0" stroke="#222" stroke-width="5" fill="none"/>'
        f'<path d="M80 1300 l30 30 M110 1300 l-30 30 M130 1330 l24 24 M154 1330 l-24 24" stroke="#222" stroke-width="5"/>'
        f'<path d="M930 1010 l26 26 M956 1010 l-26 26" stroke="#D6262E" stroke-width="6"/>'
        f'<path d="M880 1040 v30 M865 1055 h30 M869 1044 l22 22 M891 1044 l-22 22" stroke="#222" stroke-width="4"/>'
        f'<rect width="1080" height="1920" filter="url(#sc{n}t)"/></svg></div>')
    sel = r.ritaglio(da - 0.1, a + 0.1)
    # le righe di lettere ritagliate
    m = len(r.corpo)
    righe = e.get("righe", [])[:3]
    html_r, tl_l = [], []
    k = 0
    for j, (riga, t) in enumerate(righe):
        lett = [c for c in riga.upper()]
        dim = max(min(132, int(960 / max(len(lett), 1) / 0.78)), 70)
        spans = []
        for q, c in enumerate(lett):
            if c == " ":
                spans.append(f'<span style="width:{dim * 0.3:.0f}px"></span>')
                continue
            fondo, colore, fam, peso = _CARTE[(k * 7 + j * 3) % len(_CARTE)]
            gira = rnd.uniform(-7, 7)
            sz = dim * rnd.uniform(0.86, 1.05)
            spans.append(f'<span class="sc-l" id="sl{m}l{k}" style="background:{fondo};color:{colore};font-family:{fam};font-weight:{peso};'
                         f'font-size:{sz:.0f}px;transform:rotate({gira:.1f}deg)">{E(c)}</span>')
            tl_l.append((k, t + q * 0.045))
            k += 1
        y = 150 + j * 185
        html_r.append(f'<div class="sc-rg" id="sl{m}r{j}" style="top:{y}px">{"".join(spans)}</div>')
    segni = ""
    if e.get("cerchio") is not None and e["cerchio"] < len(righe):
        y = 150 + e["cerchio"] * 185 + 70
        segni += f'<path id="sl{m}c" d="M120 {y} C 120 {y - 160}, 960 {y - 160}, 965 {y} C 970 {y + 155}, 130 {y + 155}, 100 {y - 25}" stroke-dasharray="2600" stroke-dashoffset="2600"/>'
    if e.get("sottolinea") is not None and e["sottolinea"] < len(righe):
        y = 150 + e["sottolinea"] * 185 + 158
        segni += f'<path id="sl{m}s" d="M380 {y} C 520 {y - 12}, 700 {y + 8}, 860 {y - 6}" stroke-dasharray="520" stroke-dashoffset="520"/>'
    r.corpo.append("".join(html_r) + f'<svg class="sc-segno" viewBox="0 0 1080 1920" width="1080" height="1920">{segni}</svg>')
    T = r.tl.append
    # tu diventi un adesivo più piccolo, appoggiato in basso
    T(f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});tl.set("#sc{n}",{{opacity:0}},{a:.3f});'
      f'tl.set("{sel}",{{opacity:1,transformOrigin:"540px 1920px",{_contorno(9)}}},{da:.3f});'
      f'tl.fromTo("{sel}",{{scale:.86,rotation:-2}},{{scale:.74,rotation:0,duration:.35,ease:"back.out(1.6)",immediateRender:false}},{da:.3f});'
      f'tl.set("{sel}",{{opacity:0,filter:"none",scale:1}},{a:.3f});'
      f'tl.set("[id^=sl{m}r]",{{opacity:0}},{a:.3f});')
    for kk, t in tl_l:
        T(f'tl.fromTo("#sl{m}l{kk}",{{opacity:0,scale:1.7}},{{opacity:1,scale:1,duration:.14,ease:"back.out(2.5)",immediateRender:false}},{t:.3f});')
    for j, (_, t) in enumerate(righe):
        r.suono("pop", t, 0.22)
    fine_riga = lambda j: min(righe[j][1] + len(righe[j][0]) * 0.045 + 0.12, a - 0.6)
    if f'id="sl{m}c"' in segni:
        tc = fine_riga(e["cerchio"])
        T(f'tl.fromTo("#sl{m}c",{{strokeDashoffset:2600}},{{strokeDashoffset:0,duration:.45,ease:"power2.out",immediateRender:false}},{tc:.3f});')
        r.suono("click", tc, 0.2)
    if f'id="sl{m}s"' in segni:
        T(f'tl.fromTo("#sl{m}s",{{strokeDashoffset:520}},{{strokeDashoffset:0,duration:.3,ease:"power2.out",immediateRender:false}},{fine_riga(e["sottolinea"]) + 0.2:.3f});')
    T(f'tl.set(".sc-segno path",{{opacity:0}},{a:.3f});')
    r.suono("transizione", da, 0.35)
    r.suono("transizione", a, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- il video in un reel
_ICONE = {
    "cuore": '<path d="M24 41C10 31 4 24 4 16a10 10 0 0 1 20-4a10 10 0 0 1 20 4c0 8-6 15-20 25z" fill="none" stroke="#fff" stroke-width="3.5"/>',
    "commento": '<path d="M24 6a18 17 0 1 0 9 31l9 3-3-8A18 17 0 0 0 24 6z" fill="none" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>',
    "invia": '<path d="M44 5L4 20l16 6 6 16z M20 26L44 5" fill="none" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>',
    "altro": '<circle cx="10" cy="24" r="3.5" fill="#fff"/><circle cx="24" cy="24" r="3.5" fill="#fff"/><circle cx="38" cy="24" r="3.5" fill="#fff"/>',
}


def reel(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    k = 0.56
    L, Tp, W, H = 540 - 540 * k, 960 - 960 * k, 1080 * k, 1920 * k
    pp = os.path.join(DATI, "profilo.json")
    pf = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else {}
    nome = e.get("nome", pf.get("nome", "il_tuo_profilo"))
    n = len(r.corpo)
    foto = f"reel-{n}.jpg"
    vera = os.path.join(DATI, pf["foto"]) if pf.get("foto") else ""
    if vera and os.path.exists(vera):
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", vera, "-vf", "scale=120:120:force_original_aspect_ratio=increase,crop=120:120",
                        "-q:v", "3", os.path.join(r.assets, foto)], capture_output=True)
    else:
        lato = int((faccia["destra"] - faccia["sinistra"]) * 1.5)
        cx, cy = (faccia["sinistra"] + faccia["destra"]) / 2, (faccia["occhi"] + faccia["mento"]) / 2
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(da, 0):.2f}", "-i", os.path.join(r.assets, "tagliato.mp4"), "-frames:v", "1",
                        "-vf", f"crop={lato}:{lato}:{max(cx - lato / 2, 0):.0f}:{max(cy - lato / 2, 0):.0f},scale=120:120", "-q:v", "3",
                        os.path.join(r.assets, foto)], capture_output=True)
    icone = "".join(f'<svg viewBox="0 0 48 48" id="sv{n}{nomeic}">{_ICONE[nomeic]}</svg>' for nomeic in ("cuore", "commento", "invia", "altro"))
    ade = (f'<div class="sc-ade" id="sv{n}a" style="right:90px;bottom:250px;opacity:0"><i></i>{E(e["adesivo"])}</div>' if e.get("adesivo") else "")
    r.corpo.append(f'<video class="sc-dietro" id="sv{n}d" src="assets/tagliato.mp4" muted playsinline data-start="{da:.3f}" '
                   f'data-media-start="{da:.3f}" data-duration="{a - da:.3f}"></video>'
                   f'<div class="sc-ui" id="sv{n}" style="left:{L:.0f}px;top:{Tp:.0f}px;width:{W:.0f}px;height:{H:.0f}px;border-radius:40px;overflow:hidden">'
                   f'<div class="sc-ic" style="bottom:120px">{icone}</div>'
                   f'<div class="sc-chi"><div class="r1"><img src="assets/{foto}"><span>{E(nome)}</span>'
                   f'<span class="sg" id="sv{n}s">Segui</span><span class="sg" id="sv{n}z" style="display:none;background:rgba(255,255,255,.22)">Seguito</span></div><div class="r2">{E(e.get("testo", ""))}</div></div>'
                   f'{ade}<div class="sc-bar"><i id="sv{n}b"></i></div><i class="sc-dito" id="sv{n}t"></i></div>')
    T = r.tl.append
    entra = 0.55
    T(f'tl.set("#cam",{{transformOrigin:"540px 960px"}},{da:.3f});'
      f'tl.fromTo("#cam",{{scale:1,borderRadius:0}},{{scale:{k},borderRadius:72,duration:{entra},ease:"power3.inOut",immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sv{n}d",{{opacity:0}},{{opacity:1,duration:{entra},immediateRender:false}},{da:.3f});'
      f'tl.fromTo("#sv{n}",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{da + entra - 0.1:.3f});'
      f'tl.fromTo("#sv{n}b",{{scaleX:0}},{{scaleX:1,duration:{a - da - entra:.2f},ease:"none",immediateRender:false}},{da + entra:.3f});'
      f'tl.to("#sv{n}",{{opacity:0,duration:.2}},{a - 0.45:.3f});'
      f'tl.to("#cam",{{scale:1,borderRadius:0,duration:.45,ease:"power3.inOut"}},{a - 0.45:.3f});'
      f'tl.to("#sv{n}d",{{opacity:0,duration:.45}},{a - 0.45:.3f});tl.set("#cam",{{clearProps:"borderRadius"}},{a:.3f});')
    seg = e.get("segui")
    if seg:
        # il dito tocca "Segui": il tasto diventa "Seguito"
        T(f'tl.set("#sv{n}t",{{left:{min(24 + 58 + len(nome) * 13.5 + 30, W - 160):.0f},bottom:85,top:"auto"}},{seg - 0.3:.3f});'
          f'tl.fromTo("#sv{n}t",{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:.2,immediateRender:false}},{seg - 0.25:.3f});'
          f'tl.to("#sv{n}t",{{opacity:0,scale:.7,duration:.25}},{seg + 0.1:.3f});'
          f'tl.set("#sv{n}s",{{display:"none"}},{seg:.3f});tl.set("#sv{n}z",{{display:"inline-block"}},{seg:.3f});')
        r.suono("click", seg, 0.3)
    if e.get("adesivo"):
        t_a = e.get("adesivo_da", da + entra + 0.6)
        T(f'tl.fromTo("#sv{n}a",{{opacity:0,scale:.4}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2.5)",immediateRender:false}},{t_a:.3f});')
        r.suono("pop", t_a, 0.25)
    cu = e.get("cuore")
    if cu:
        T(f'tl.set("#sv{n}cuore path",{{fill:"#FF3040",stroke:"#FF3040"}},{cu:.3f});'
          f'tl.set("#sv{n}cuore path",{{fill:"none",stroke:"#fff"}},{max(cu - 0.05, da):.3f});'
          f'tl.fromTo("#sv{n}cuore",{{scale:1.6}},{{scale:1,duration:.35,ease:"back.out(3)",immediateRender:false}},{cu:.3f});')
        r.suono("pop", cu, 0.3)
    r.suono("transizione", da, 0.3)
    r.suono("transizione", a - 0.45, 0.25)
    r.nascondi.append((da, a))


TIPI = {"dentro": dentro, "sfocato": sfocato, "raggi": raggi, "collage": collage, "reel": reel}
