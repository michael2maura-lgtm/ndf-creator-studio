"""Effetti del modello Testimonianza (18/11/2026), rifatti da noi guardando un reel di esempio (mai copiato niente).
Motore grafica, tempi del video TAGLIATO. Colori: la carta prende il colore dello stile (accento), il fondo è
colori["fondo_carta"] (di serie verde petrolio scuro).

 {"tipo": "intervista", "da": 0, "a": 1.6, "titolo": "Da 0 clienti ad *agenda piena*|in soli 3 mesi",
  "sopra": "chiamata.mp4" (facoltativo), "sotto": "io" (facoltativo)}
     Apertura con la videointervista: su un fondo scuro due finestre arrotondate una sopra l'altra e, in mezzo, il
     titolo con il risultato (corsivo grassetto, *parola* = colore della carta, "|" = a capo).
     Di serie le finestre mostrano le due metà del pezzo di videochiamata messo in testa al video con
     `testa.py` (a sinistra la cliente sopra, a destra chi intervista sotto). Con "sopra": un file (clip di DATI/clip o
     del lavoro, senza audio) nella finestra di sopra e tu (il video) in quella di sotto.
 {"tipo": "carta", "da", "a", "etichetta": "Prima" | "Dopo", "foto": "cliente.jpg" (facoltativa),
  "voci": [["AGENDA VUOTA", t], ["NO PERCORSI", t], ["0€ DAI SOCIAL", t]]}
     Scheda Prima/Dopo: lo schermo passa su un fondo pieno con una carta del colore dello stile, la foto tonda della
     persona, l'etichetta e le voci che escono dallo sfocato quando le dici (2-4 voci, 1-3 parole). I sottotitoli
     scendono sotto la carta. Una "Prima" e una "Dopo" per video, 4-10 secondi ciascuna.
 {"tipo": "prove", "da", "a", "file": "profilo.png" (screenshot o video), "scorri": true}
     Prove dietro di te: lo sfondo della stanza diventa lo screenshot (il profilo, i messaggi, i risultati della
     cliente) che scorre piano verso l'alto; tu resti ritagliato davanti. Quando parli dei risultati.
 {"tipo": "prova", "da", "a", "file": "screenshot.png" o video}
     Prova sul telefono: un telefono sale dal basso (con il mosso) e mostra lo screenshot o il video; dietro, la
     stanza sfocata. Per "guarda", "ha fatto", un video pubblicato, un messaggio ricevuto.
 {"tipo": "miste", "da", "a", "parole": [["CHI MI", t, "forte"], ["comprerà", t, "corsivo"], ["MAI", t, "oro"]],
  "dove": "sopra" | "petto"}
     Parole miste sopra la testa: grassetto bianco maiuscolo, corsivo elegante e grassetto dorato, una alla volta,
     a scaletta. Per la frase-dubbio ("chi mi comprerà mai?") e la frase forte ("senza diventare VIRALE").
"""
import html
import os
import re
import shutil

E = html.escape


def _fondo(r):
    return r.stile["colori"].get("fondo_carta", "#0F3D3E")


def _schiari(hexa, k):
    rr, gg, bb = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(x + (255 - x) * k) for x in (rr, gg, bb))


def _scuri(hexa, k):
    rr, gg, bb = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(x * k) for x in (rr, gg, bb))


def _css(r):
    if getattr(r, "css_testim", False):
        return
    r.css_testim = True
    for f in ("Poppins-Bold.ttf", "PlayfairDisplay.ttf", "PlayfairDisplay-Italic.ttf", "PlusJakartaSans.ttf"):
        r.font_extra(f)
    acc = r.stile["colori"]["accento"]
    f = _fondo(r)
    luce = _schiari(f, 0.12)
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'TS Poppins';src:url('assets/Poppins-Bold.ttf');font-weight:700}"
        "@font-face{font-family:'TS Playfair';src:url('assets/PlayfairDisplay.ttf');font-weight:400 900}"
        "@font-face{font-family:'TS Playfair';src:url('assets/PlayfairDisplay-Italic.ttf');font-style:italic;font-weight:400 900}"
        "@font-face{font-family:'TS Jakarta';src:url('assets/PlusJakartaSans.ttf');font-weight:200 800}"
        f".ts-fondo{{position:absolute;inset:0;z-index:28;opacity:0;background:radial-gradient(ellipse 120% 80% at 70% 95%,{luce} 0%,{f} 60%),{f}}}"
        f".ts-carta{{position:absolute;left:150px;width:780px;top:220px;height:1040px;border-radius:46px;z-index:29;opacity:0;"
        f"background:linear-gradient(140deg,{_schiari(acc, .38)} 0%,{_schiari(acc, .12)} 45%,{acc} 75%,{_schiari(acc, .3)} 100%);"
        "box-shadow:0 30px 70px rgba(0,0,0,.45),inset 0 2px 0 rgba(255,255,255,.35)}"
        ".ts-foto{position:absolute;left:50%;top:48px;width:210px;height:210px;margin-left:-105px;border-radius:50%;object-fit:cover;"
        "border:4px solid rgba(255,255,255,.55);box-shadow:0 10px 26px rgba(0,0,0,.35)}"
        f".ts-et{{position:absolute;left:30px;top:286px;padding:8px 30px 14px;border-radius:16px;background:{f};"
        "border:2px solid rgba(160,240,230,.28);font-family:'TS Playfair';font-size:66px;line-height:1;color:#F6E9CF;"
        "text-shadow:0 0 14px rgba(255,236,200,.55);box-shadow:0 8px 20px rgba(0,0,0,.25)}"
        f".ts-voce{{position:absolute;left:30px;right:30px;height:132px;border-radius:30px;background:{f};opacity:0;"
        "border:2px solid rgba(160,240,230,.28);display:flex;align-items:center;justify-content:center;"
        "font-family:'TS Poppins';font-weight:700;font-size:62px;letter-spacing:.5px;color:#F6E9CF;white-space:nowrap;"
        "text-shadow:0 0 16px rgba(255,236,200,.65);box-shadow:0 10px 24px rgba(0,0,0,.3)}"
        ".ts-win{position:absolute;left:90px;width:900px;height:506px;border-radius:30px;overflow:hidden;z-index:29;opacity:0;"
        "box-shadow:0 18px 44px rgba(0,0,0,.45);border:2px solid rgba(255,255,255,.18)}"
        ".ts-win video,.ts-win img{position:absolute;object-fit:cover}"
        ".ts-tit{position:absolute;left:40px;right:40px;z-index:30;opacity:0;text-align:center;font-family:'TS Poppins';"
        "font-style:italic;font-weight:700;font-size:64px;line-height:1.08;letter-spacing:-1.5px;color:#F3DDB0;"
        "text-shadow:0 4px 16px rgba(0,0,0,.45)}"
        f".ts-tit em{{font-style:italic;color:{_schiari(acc, .1)}}}"
        ".ts-prove{position:absolute;left:0;top:0;width:1080px;z-index:0;opacity:0}"
        ".ts-tel{position:absolute;left:250px;top:330px;width:580px;height:1180px;border-radius:78px;background:#0B0B0D;z-index:30;opacity:0;"
        "box-shadow:0 40px 90px rgba(0,0,0,.55),inset 0 0 0 3px #2A2A2E;padding:22px;box-sizing:border-box}"
        ".ts-tel i{position:absolute;left:50%;top:38px;width:150px;height:40px;margin-left:-75px;border-radius:20px;background:#000;z-index:2}"
        ".ts-tel div{position:absolute;inset:22px;border-radius:58px;overflow:hidden;background:#111}"
        ".ts-tel div img,.ts-tel div video{width:100%;height:100%;object-fit:cover;object-position:50% 0}"
        ".ts-mx{position:absolute;z-index:31;opacity:0;white-space:nowrap;line-height:1}"
        ".ts-mx.forte{font-family:'TS Poppins';font-weight:700;color:#fff;letter-spacing:-1px;"
        "text-shadow:0 3px 0 rgba(0,0,0,.18),0 8px 24px rgba(0,0,0,.45)}"
        ".ts-mx.corsivo{font-family:'TS Playfair';font-style:italic;font-weight:400;color:#fff;text-shadow:0 4px 20px rgba(0,0,0,.5)}"
        ".ts-mx.oro{font-family:'TS Poppins';font-weight:700;letter-spacing:-1px;color:#E9C98B;"
        "background:linear-gradient(180deg,#F8E7BE 0%,#D9AE62 60%,#B98A44 100%);-webkit-background-clip:text;background-clip:text;"
        "-webkit-text-fill-color:transparent;filter:drop-shadow(0 6px 16px rgba(0,0,0,.45))}"
        "</style>")


def _file(r, nome):
    """Trova un file del cliente: percorso pieno, cartella del lavoro, DATI/clip, DATI/immagini."""
    cart = os.path.dirname(r.reel)
    dati = os.path.dirname(os.path.dirname(cart))
    for q in (nome, os.path.join(cart, nome), os.path.join(dati, "clip", nome), os.path.join(dati, "immagini", nome)):
        if q and os.path.isfile(q):
            return q
    return None


def _copia(r, p, n, pref):
    dest = f"{pref}-{n}{os.path.splitext(p)[1].lower()}"
    shutil.copy2(p, os.path.join(r.assets, dest))
    return dest


def _media(dest, da, a, stile, ident=""):
    if dest.endswith((".mp4", ".mov", ".webm", ".m4v")):
        return (f'<video{ident} src="assets/{dest}" muted playsinline data-start="{da:.3f}" data-media-start="0" '
                f'data-duration="{a - da:.3f}" style="{stile}"></video>')
    return f'<img{ident} src="assets/{dest}" style="{stile}">'


def _sott(r, da, a, y):
    """I sottotitoli scendono sotto la carta (o dove serve) e poi tornano al loro posto."""
    r.tl.append(f'tl.set(".st,.sub",{{top:{y}}},{da:.3f});tl.set(".st,.sub",{{top:{r.y_sub}}},{a:.3f});')


def intervista(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    y1, y2 = 350, 1070
    if e.get("sopra"):
        p = _file(r, e["sopra"])
        if not p:
            print(f'NOTA: non trovo {e["sopra"]} per l\'intervista, la salto')
            return
        dest = _copia(r, p, n, "intervista")
        w1 = _media(dest, da, a, "left:0;top:0;width:900px;height:506px;object-position:50% 26%")
        # sotto: tu, la parte del video con la faccia
        cy = faccia["occhi"] + 60
        w2 = _media("tagliato.mp4", da, a, f"left:0;top:{-(cy * 900 / 1080 - 253):.0f}px;width:900px;height:1600px").replace(
            'data-media-start="0"', f'data-media-start="{da:.3f}"')
    else:
        # il pezzo di videochiamata (16:9) messo in testa dal testa.py sta in mezzo al video: y 656-1264
        w1 = _media("tagliato.mp4", da, a, "left:0;top:-1346px;width:1800px;height:3200px").replace(
            'data-media-start="0"', f'data-media-start="{da:.3f}"')
        w2 = _media("tagliato.mp4", da, a, "left:-900px;top:-1346px;width:1800px;height:3200px").replace(
            'data-media-start="0"', f'data-media-start="{da:.3f}"')
    righe = [re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(t.strip())) for t in e.get("titolo", "").split("|") if t.strip()]
    tit = "<br>".join(righe)
    r.corpo.append(f'<div class="ts-fondo" id="ti{n}"></div>'
                   f'<div class="ts-win" id="ti{n}a" style="top:{y1}px">{w1}</div>'
                   f'<div class="ts-tit" id="ti{n}t" style="top:{y1 + 506 + 28}px">{tit}</div>'
                   f'<div class="ts-win" id="ti{n}b" style="top:{y2 + 60 * (len(righe) > 2)}px">{w2}</div>')
    r.tl.append(f'tl.set(["#ti{n}","#ti{n}a","#ti{n}b"],{{opacity:1}},{da:.3f});'
                f'tl.fromTo(["#ti{n}a","#ti{n}b"],{{scale:1.04}},{{scale:1,duration:{a - da:.3f},ease:"none",immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#ti{n}t",{{opacity:0,y:16,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.35,ease:"power3.out",immediateRender:false}},{da + 0.05:.3f});'
                f'tl.set(["#ti{n}","#ti{n}a","#ti{n}b","#ti{n}t"],{{opacity:0}},{a:.3f});')
    _sott(r, da, a, y1 - 70)


def carta(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    foto = ""
    if e.get("foto"):
        p = _file(r, e["foto"])
        if p:
            foto = f'<img class="ts-foto" src="assets/{_copia(r, p, n, "foto")}">'
        else:
            print(f'NOTA: non trovo la foto {e["foto"]}, la carta resta senza')
    voci = e.get("voci", [])[:4]
    y0 = 420 if foto else 300
    et_top = 286 if foto else 60
    righe = "".join(f'<div class="ts-voce" id="tc{n}v{j}" style="top:{y0 + 30 + j * 168}px;'
                    f'font-size:{min(62, int(1180 / max(len(t), 8)))}px">{E(t.upper())}</div>' for j, (t, _) in enumerate(voci))
    alta = y0 + 30 + len(voci) * 168 + 40   # la carta è alta quanto le sue voci
    r.corpo.append(f'<div class="ts-fondo" id="tc{n}"></div><div class="ts-carta" id="tc{n}c" style="height:{alta}px;top:{max(160, 900 - alta // 2 - 120)}px">{foto}'
                   f'<div class="ts-et" id="tc{n}e" style="top:{et_top}px">{E(e.get("etichetta", "Prima"))}</div>{righe}</div>')
    r.tl.append(f'tl.fromTo("#tc{n}",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#tc{n}c",{{opacity:0,scale:.94,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.45,ease:"power3.out",immediateRender:false}},{da + 0.05:.3f});'
                f'tl.fromTo("#tc{n}e",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.3,ease:"power2.out",immediateRender:false}},{da + 0.3:.3f});')
    for j, (_, t) in enumerate(voci):
        t = max(t, da + 0.35)
        r.tl.append(f'tl.fromTo("#tc{n}v{j}",{{opacity:0,scale:1.06,filter:"blur(14px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.35,ease:"power2.out",immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.25)
    # esce dissolvendo e lascia ricomparire la persona
    r.tl.append(f'tl.to(["#tc{n}","#tc{n}c"],{{opacity:0,duration:.35,ease:"power1.in"}},{a - 0.35:.3f});')
    r.suono("transizione", da, 0.2)
    _sott(r, da, a, max(160, 900 - alta // 2 - 120) + alta + 110)


def prove(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    p = _file(r, e.get("file", ""))
    if not p:
        print(f'NOTA: non trovo {e.get("file")} per le prove, le salto')
        return
    dest = _copia(r, p, n, "prove")
    sel = r.ritaglio(da - 0.1, a + 0.1)
    alta = 1920
    if not dest.endswith((".mp4", ".mov", ".webm", ".m4v")):
        try:
            from PIL import Image
            w, h = Image.open(p).size
            alta = max(1920, round(h * 1080 / w))
        except Exception:
            pass
    stile = f"position:absolute;left:0;top:0;width:1080px;height:{alta}px;object-fit:cover;z-index:0;opacity:0"
    r.camera.insert(0, _media(dest, da, a, stile, f' id="tp{n}"'))
    corsa = min(alta - 1920, 900) if e.get("scorri", True) else 0
    r.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
                f'tl.fromTo("#tp{n}",{{opacity:0,scale:1.05}},{{opacity:1,scale:1,duration:.3,ease:"power2.out",immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#tp{n}",{{y:0}},{{y:{-corsa - 60},duration:{a - da:.3f},ease:"sine.inOut",immediateRender:false}},{da:.3f});'
                f'tl.to("#tp{n}",{{opacity:0,duration:.3}},{a - 0.3:.3f});')
    r.suono("transizione", da, 0.2)


def prova(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    p = _file(r, e.get("file", ""))
    if not p:
        print(f'NOTA: non trovo {e.get("file")} per la prova sul telefono, la salto')
        return
    dest = _copia(r, p, n, "prova")
    r.corpo.append(f'<div class="ts-tel" id="tt{n}"><i></i><div>{_media(dest, da, a, "")}</div></div>')
    r.tl.append(f'tl.fromTo("#bg",{{filter:"blur(0px) brightness(1)"}},{{filter:"blur(18px) brightness(.8)",duration:.3,immediateRender:false}},{da:.3f});'
                f'tl.to("#bg",{{filter:"blur(0px) brightness(1)",duration:.3}},{a - 0.3:.3f});tl.set("#bg",{{filter:"none"}},{a:.3f});'
                f'tl.fromTo("#tt{n}",{{opacity:1,y:1300,rotation:8,filter:"blur(10px)"}},{{opacity:1,y:0,rotation:-3,filter:"blur(0px)",duration:.45,ease:"back.out(1.1)",immediateRender:false}},{da:.3f});'
                f'tl.to("#tt{n}",{{rotation:2,y:-14,duration:{max(a - da - 0.8, 0.3):.3f},ease:"sine.inOut"}},{da + 0.45:.3f});'
                f'tl.to("#tt{n}",{{y:1300,rotation:-6,filter:"blur(8px)",duration:.35,ease:"power3.in"}},{a - 0.35:.3f});'
                f'tl.set("#tt{n}",{{opacity:0}},{a:.3f});')
    r.suono("transizione", da, 0.25)
    r.nascondi.append((da, a)) if e.get("senza_sottotitoli") else _sott(r, da, a, 1640)


def miste(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    parole = e.get("parole", [])[:6]
    cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
    sopra = e.get("dove", "sopra") == "sopra"
    y = max(cima - 330, 150) if sopra else faccia["mento"] + 120
    # le parole in righe a scaletta: si riempie una riga finché c'è posto, poi la riga dopo rientra un po'
    righe, cur, x0 = [], [], 0
    for j, p in enumerate(parole):
        testo, t = p[0], p[1]
        tipo = p[2] if len(p) > 2 else ("forte" if j % 2 == 0 else "corsivo")
        testo = testo.lower() if tipo == "corsivo" else testo.upper()
        dim = {"corsivo": 100, "forte": 96, "oro": 116}.get(tipo, 96)
        largo = len(testo) * dim * (0.46 if tipo == "corsivo" else 0.72)
        if largo > 880:
            dim, largo = int(dim * 880 / largo), 880
        if cur and x0 + largo > 900:
            righe.append(cur)
            cur, x0 = [], 0
        cur.append((j, testo, t, tipo, dim, x0, largo))
        x0 += largo + 26
    if cur:
        righe.append(cur)
    alti = [max(w[4] for w in rg) * 1.02 for rg in righe]
    y = (max(cima - 40 - sum(alti), 120)) if sopra else faccia["mento"] + 120
    pezzi = []
    for k, rg in enumerate(righe):
        largo_riga = rg[-1][5] + rg[-1][6]
        sx = max(60, min(540 - largo_riga / 2 + (-70 if k % 2 == 0 else 70), 1020 - largo_riga))
        for (j, testo, t, tipo, dim, x, _) in rg:
            top = y + (alti[k] - dim) * 0.8
            pezzi.append(f'<div class="ts-mx {tipo}" id="tm{n}w{j}" style="left:{sx + x:.0f}px;top:{top:.0f}px;font-size:{dim}px">{E(testo)}</div>')
            r.tl.append(f'tl.fromTo("#tm{n}w{j}",{{opacity:0,y:24,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.3,ease:"power3.out",immediateRender:false}},{max(t, da):.3f});')
        y += alti[k]
    r.corpo.append("".join(pezzi))
    r.tl.append(f'tl.to("[id^=tm{n}w]",{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    r.suono("pop", da, 0.2)


TIPI = {"intervista": intervista, "carta": carta, "prove": prove, "prova": prova, "miste": miste}
