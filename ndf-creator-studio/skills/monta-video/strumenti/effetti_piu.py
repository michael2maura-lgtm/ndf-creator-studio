"""Effetti aggiunti il 17/11/2026, rifatti da noi guardando come si muovono gli effetti di riferimento (mai copiato il codice).
Tutti nel motore grafica, tempi del video TAGLIATO. Mentre ci sono, i sottotitoli si nascondono (tranne "pallini").

 {"tipo": "sparse", "da", "a", "parole": [["Claude", t], ["monta", t], ["i miei", t], ["video", t]]}
     Parole sparse: le prime parole cadono una alla volta sul petto, di misure diverse; quelle prima si sfocano.
     Per il gancio (primi 3 secondi), 3-6 parole dette.
 {"tipo": "pallini", "da", "a", "quanti": 3, "riempi": [t1, t2, t3]}
     Pallini: dici "3 cose" e sotto il mento compaiono 3 pallini vuoti; si riempiono mentre le dici.
 {"tipo": "rivista", "da", "a", "testata": "EDIT", "sinistra": "IL NUMERO 1", "destra": "NOVEMBRE",
  "etichetta": "IN COPERTINA", "titolo": "I montatori sono *finiti*", "titolo_da": t}
     Copertina di rivista: la testata enorme dietro la testa, un filo sottile attorno, le scritte piccole e una riga
     in corsivo in basso (*parola* = colore dello stile). Per una frase forte, una volta per video.
 {"tipo": "schede", "da", "a", "titolo": "La verità sull'AI",
  "schede": [{"titolo": "La strada del corso", "da": t, "righe": [["Imparare a montare", 40], ["Comprare programmi", 25]]}, ...]}
     Schede con le barre: tu scendi in una finestra in basso, sopra una scheda bianca con le barre che corrono;
     la seconda scheda prende il posto della prima. Per un confronto con dei numeri (1-2 schede, 2-5 righe).
 {"tipo": "cartellini", "da", "a", "voci": [{"testo": "Immagini", "sotto": "per le ads", "punto": "testa", "quando": t}, ...]}
     Cartellini legati con un filo: scuri, con il quadratino giallo, legati con una linea sottile a un punto di te
     (punto: "testa", "testa_dx", "spalla", "petto") che ti segue quando ti muovi. 1-3 voci.
 {"tipo": "scritte", "da", "a", "frasi": [["TUTTI NE PARLANO", t], ["CLAUDE MONTA I VIDEO", t]]}
     Muro di parole giganti: la stanza si scurisce, dietro di te righe di parole enormi che scorrono; sulla frase
     dopo cambiano (l'ultima nel colore dello stile). "Tutti dicono", "ovunque", un tema che torna.
 {"tipo": "broll", "da", "a", "file": "soldi.mp4" (clip o foto in DATI/clip, DATI/immagini o nel lavoro),
  "testo": "facoltativo, una riga in alto", "lampo": true}
     B-roll: per 1-3 secondi il video stacca su una clip o una foto vera a tutto schermo (la foto si avvicina piano),
     poi torna su di te. I sottotitoli continuano sopra. Solo quando la frase nomina una cosa che si può far vedere
     (soldi, ufficio, sveglia, una persona al computer). Clip da Pexels con strumenti/clip.py, foto con lo stesso.
     Al massimo uno ogni 6-8 secondi.
 {"tipo": "spunte", "da", "a", "voci": [["Insegnanti preparati", t], ["Anni di esperienza", t]]}
     Spunte: sul petto un quadratino con la spunta (colore del brand) e sotto, grande e bianca, la cosa detta; ogni voce prende
     il posto della prima. Per i punti di forza, i vantaggi, "cosa trovi da noi" (2-4 voci).
 {"tipo": "frase", "da", "a", "parole": [["e il tuo", t, "piccola"], ["collega", t, "grande"], ["straordinari", t, "corsivo"]],
  "fondo": "scuro" | "colore"}
     Frase a tutto schermo (testo animato): lo schermo stacca su un fondo pieno (il colore del brand scurito, o pieno
     con "colore") e le parole si compongono una alla volta, piccole, grandi in grassetto o grandi in corsivo.
     Sulla frase più importante (gancio, domanda, frase finale), 1-2 volte in un video, 1,5-3 s, parole dette.
 {"tipo": "colpiti", "da", "a", "voci": [["Programma uno", t, "riga piccola"], ...]}
     Nomi colpiti: ogni nome sbatte su una targa scura sopra la testa; quando arriva il dopo, il prima viene
     barrato in rosso e vola via. Per "senza questo, senza quello", strumenti o abitudini da lasciare (2-4).
"""
import html
import re

E = html.escape


def _css(r):
    if getattr(r, "css_piu", False):
        return
    r.css_piu = True
    for f in ("InterTight.ttf", "BodoniModa.ttf", "BodoniModa-Italic.ttf", "JetBrainsMono.ttf"):
        r.font_extra(f)
    acc = r.stile["colori"]["accento"]
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Bodoni Moda';src:url('assets/BodoniModa.ttf');font-weight:400 900}"
        "@font-face{font-family:'Bodoni Moda';src:url('assets/BodoniModa-Italic.ttf');font-style:italic;font-weight:400 900}"
        "@font-face{font-family:'JetBrains Mono';src:url('assets/JetBrainsMono.ttf');font-weight:100 800}"
        ".px-sp{position:absolute;z-index:31;opacity:0;font-family:'Inter Tight';font-weight:800;color:#fff;letter-spacing:-.03em;"
        "white-space:nowrap;line-height:1;text-shadow:0 4px 22px rgba(0,0,0,.55)}"
        ".px-dots{position:absolute;left:0;right:0;z-index:31;display:flex;justify-content:center;gap:20px}"
        ".px-dot{width:40px;height:40px;border-radius:50%;border:5px solid #fff;box-sizing:border-box;opacity:0;"
        "box-shadow:0 3px 14px rgba(0,0,0,.35)}"
        ".px-tes{position:absolute;left:0;right:0;text-align:center;z-index:2;opacity:0;font-family:'Bodoni Moda';font-weight:600;"
        "color:#F6F1E6;line-height:.85;letter-spacing:.06em;white-space:nowrap}"
        ".px-cor{position:absolute;inset:34px;z-index:30;border:2px solid rgba(255,255,255,.75);opacity:0;pointer-events:none}"
        ".px-pic{position:absolute;z-index:30;opacity:0;font-family:'Inter Tight';font-weight:700;font-size:22px;letter-spacing:4px;"
        "color:#fff;line-height:1.35;text-shadow:0 2px 8px rgba(0,0,0,.5)}"
        ".px-ombra{position:absolute;left:0;right:0;bottom:0;height:900px;z-index:29;opacity:0;"
        "background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.72))}"
        ".px-cl{position:absolute;left:80px;right:80px;bottom:360px;z-index:31;opacity:0}"
        ".px-cl small{display:block;font-family:'Inter Tight';font-weight:700;font-size:24px;letter-spacing:5px;color:#fff;margin-bottom:14px}"
        ".px-cl div{font-family:'Bodoni Moda';font-style:italic;font-weight:500;font-size:100px;line-height:1;color:#fff}"
        f".px-cl em{{font-style:italic;color:{acc}}}"
        ".px-cl span{display:inline-block;opacity:0}"
        ".px-st{position:absolute;inset:0;z-index:28;opacity:0;background:#EEEDEA}"
        ".px-st h3{position:absolute;left:0;right:0;top:90px;margin:0;text-align:center;font-family:'Inter Tight';font-weight:800;"
        "font-size:56px;color:#151515!important;letter-spacing:-1px;opacity:1!important}"
        ".px-win{position:absolute;left:60px;top:760px;width:960px;height:1100px;object-fit:cover;border-radius:36px;z-index:29;opacity:0;"
        "box-shadow:0 20px 50px rgba(0,0,0,.25)}"
        ".px-sc{position:absolute;left:60px;right:60px;top:180px;z-index:30;opacity:0;background:#fff;border-radius:30px;padding:30px 36px;"
        "box-shadow:0 14px 40px rgba(0,0,0,.12);font-family:'Inter Tight'}"
        ".px-sc h4{margin:0 0 20px;text-align:center;font-weight:800;font-size:46px;color:#151515!important;opacity:1!important}"
        ".px-rg{display:flex;align-items:center;gap:18px;height:86px}"
        ".px-rg span{flex:none;width:300px;font-weight:700;font-size:36px;color:#333!important;opacity:1!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".px-rg i{flex:1;height:30px;border-radius:15px;background:#E6E5E1;overflow:hidden}"
        f".px-rg i b{{display:block;height:100%;width:100%;border-radius:15px;background:{acc};transform:scaleX(0);transform-origin:0 50%}}"
        ".px-rg em{flex:none;width:110px;text-align:right;font-style:normal;font-weight:800;font-size:36px;color:#151515!important;opacity:1!important}"
        ".px-ct{position:absolute;z-index:32;opacity:0;display:flex;align-items:center;gap:16px;padding:14px 26px 14px 14px;border-radius:20px;"
        "background:rgba(20,20,22,.92);border:2px solid rgba(255,255,255,.1);box-shadow:0 12px 30px rgba(0,0,0,.4);font-family:'Inter Tight';white-space:nowrap}"
        ".px-ct b{flex:none;width:58px;height:58px;border-radius:14px;background:#F4E06D;color:#141414;display:grid;place-items:center;"
        "font-weight:900;font-size:32px}"
        ".px-ct strong{display:block;font-weight:800;font-size:38px;color:#fff;letter-spacing:-.5px}"
        ".px-ct small{display:block;font-weight:600;font-size:22px;color:rgba(255,255,255,.6);margin-top:2px}"
        ".px-fili{position:absolute;inset:0;z-index:31;pointer-events:none}"
        ".px-fili line{stroke:#F4E06D;stroke-width:3}.px-fili circle{fill:#F4E06D;stroke:#141414;stroke-width:3}"
        ".px-mw{position:absolute;inset:0;z-index:2;opacity:0;overflow:hidden}"
        ".px-mr{position:absolute;left:-400px;white-space:nowrap;font-family:'Inter Tight';font-weight:900;font-size:150px;line-height:1;"
        "letter-spacing:-.02em;text-transform:uppercase}"
        ".px-mr.pieno{color:#F2EEE6}"
        ".px-mr.vuoto{color:transparent;-webkit-text-stroke:2.5px rgba(242,238,230,.32)}"
        ".px-tg{position:absolute;z-index:31;opacity:0;padding:18px 34px 16px;border-radius:22px;background:#141416;color:#fff;"
        "box-shadow:0 14px 34px rgba(0,0,0,.45);font-family:'Inter Tight';text-align:center;white-space:nowrap}"
        ".px-tg strong{display:block;font-weight:900;font-size:68px;letter-spacing:-2px;line-height:1}"
        ".px-tg small{display:block;font-family:'JetBrains Mono';font-weight:500;font-size:22px;color:#F4E06D;margin-top:6px}"
        ".px-tg i{position:absolute;left:18px;right:18px;top:44%;height:9px;border-radius:5px;background:#E5484D;transform:scaleX(0);"
        "transform-origin:0 50%}"
        ".px-bt{position:absolute;left:60px;right:60px;top:260px;z-index:28;opacity:0;text-align:center;font-family:'Inter Tight';"
        "font-weight:900;font-size:110px;line-height:1.02;letter-spacing:-.03em;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.6)}"
        ".px-sp2{position:absolute;left:40px;right:40px;z-index:31;opacity:0;text-align:center;font-family:'Inter Tight'}"
        f".px-sp2 i{{display:inline-grid;place-items:center;width:84px;height:84px;border-radius:22px;background:{acc};color:#fff;font-style:normal;"
        "font-weight:900;font-size:56px;box-shadow:0 6px 20px rgba(0,0,0,.35)}"
        ".px-sp2 b{position:absolute;left:0;right:0;top:100px;opacity:0;font-weight:900;font-size:86px;line-height:1;letter-spacing:-.03em;"
        "color:#fff;text-shadow:0 4px 18px rgba(0,0,0,.7),0 0 4px rgba(0,0,0,.4)}"
        "@font-face{font-family:'Instrument Serif';src:url('assets/InstrumentSerif-Italic.ttf');font-style:italic}"
        ".px-fr{position:absolute;inset:0;z-index:30;opacity:0;display:flex;align-items:center;justify-content:center}"
        ".px-fr-in{width:960px;text-align:center;color:#fff;transform-origin:50% 50%}"
        ".px-fr-r{line-height:.98;opacity:0;white-space:nowrap;text-shadow:0 6px 30px rgba(0,0,0,.35)}"
        "</style>")


def _via(r, sel, a, dur=0.25):
    r.tl.append(f'tl.to({sel},{{opacity:0,duration:{dur},ease:"power2.in"}},{a - dur:.3f});')


def sparse(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    parole = e["parole"][:6]
    y0 = min(faccia["mento"] + 30, 1250)
    posti = [(0.24, 0), (0.6, 12), (0.84, -6), (0.36, 130), (0.7, 140), (0.5, 260)]
    taglie = [70, 96, 58, 120, 76, 104]
    pezzi = []
    for j, (t, _) in enumerate(parole):
        x, dy = posti[j]
        dim = min(taglie[j], int(560 / max(len(t) * 0.55, 1)))
        pezzi.append(f'<div class="px-sp" id="ps{n}w{j}" style="left:{x * 1080:.0f}px;top:{y0 + dy:.0f}px;font-size:{dim}px">{E(t)}</div>')
    r.corpo.append("".join(pezzi))
    for j, (_, t) in enumerate(parole):
        r.tl.append(f'tl.set("#ps{n}w{j}",{{xPercent:-50}},0);'
                    f'tl.fromTo("#ps{n}w{j}",{{opacity:0,scale:1.45,filter:"blur(14px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.28,ease:"power3.out",immediateRender:false}},{t:.3f});')
        if j:
            prima = ",".join(f'"#ps{n}w{k}"' for k in range(j))
            r.tl.append(f'tl.to([{prima}],{{opacity:.42,filter:"blur(4px)",duration:.25}},{t:.3f});')
        r.suono("pop", t, 0.22)
    _via(r, "[" + ",".join(f'"#ps{n}w{k}"' for k in range(len(parole))) + "]", a)
    r.nascondi.append((da, a))


def pallini(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    q = max(1, min(int(e.get("quanti", 3)), 6))
    y = min(faccia["mento"] + 40, 1240)
    r.corpo.append(f'<div class="px-dots" id="pd{n}" style="top:{y}px">' + "".join(f'<i class="px-dot" id="pd{n}d{j}"></i>' for j in range(q)) + '</div>')
    r.tl.append(f'tl.fromTo("#pd{n} .px-dot",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.3,stagger:.09,ease:"back.out(3)",immediateRender:false}},{da:.3f});')
    for j, t in enumerate(e.get("riempi", [])[:q]):
        r.tl.append(f'tl.set("#pd{n}d{j}",{{backgroundColor:"#fff"}},{t:.3f});'
                    f'tl.fromTo("#pd{n}d{j}",{{scale:1.35}},{{scale:1,duration:.3,ease:"back.out(3)",immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.25)
    r.suono("pop", da, 0.25)
    _via(r, f'"#pd{n} .px-dot"', a)


def rivista(r, e, faccia):
    _css(r)
    c = r.stile["colori"]
    n, da, a = len(r.corpo), e["da"], e["a"]
    sel = r.ritaglio(da - 0.1, a + 0.1)
    testata = e.get("testata", "EDIT").upper()
    dim = min(330, int(1000 / (max(len(testata), 3) * 0.86)))
    top = 90
    r.camera.insert(0, f'<div class="px-tes" id="pv{n}t" style="top:{top}px;font-size:{dim}px">{E(testata)}</div>')
    ys = top + dim * 0.9 + 18
    tit = re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(e.get("titolo", "")))
    parole = re.split(r"(\s+)", tit)
    # le parole del titolo una alla volta (le <em> restano intere)
    pz, buf = [], ""
    for p in re.findall(r"<em>.*?</em>|\S+", tit):
        pz.append(f'<span>{p}</span>')
    r.corpo.append(f'<div class="px-ombra" id="pv{n}o"></div><div class="px-cor" id="pv{n}c"></div>'
                   f'<div class="px-pic" id="pv{n}s" style="left:80px;top:{ys:.0f}px">{E(e.get("sinistra", "IL NUMERO 1")).replace(" ", "<br>", 1)}</div>'
                   f'<div class="px-pic" id="pv{n}d" style="right:80px;top:{ys:.0f}px;text-align:right">{E(e.get("destra", "")).replace(" ", "<br>", 1)}</div>'
                   f'<div class="px-cl" id="pv{n}l"><small>{E(e.get("etichetta", "IN COPERTINA").upper())}</small><div>{" ".join(pz)}</div></div>')
    td = e.get("titolo_da", da + 0.9)
    r.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
                f'tl.fromTo("#pv{n}t",{{opacity:0,y:80,filter:"blur(16px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.55,ease:"power3.out",immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#pv{n}c",{{opacity:0,scale:1.04}},{{opacity:1,scale:1,duration:.5,ease:"power2.out",immediateRender:false}},{da + 0.15:.3f});'
                f'tl.fromTo(["#pv{n}s","#pv{n}d"],{{opacity:0,y:10}},{{opacity:1,y:0,duration:.35,stagger:.1,immediateRender:false}},{da + 0.45:.3f});'
                f'tl.fromTo("#pv{n}o",{{opacity:0}},{{opacity:1,duration:.4,immediateRender:false}},{td - 0.2:.3f});'
                f'tl.set("#pv{n}l",{{opacity:1}},{td:.3f});'
                f'tl.fromTo("#pv{n}l small",{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{td - 0.15:.3f});'
                f'tl.fromTo("#pv{n}l span",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.35,stagger:.12,ease:"power3.out",immediateRender:false}},{td:.3f});'
                f'tl.to("#bg",{{filter:"brightness(.82) contrast(1.06)",duration:.4}},{da:.3f});tl.set("#bg",{{filter:"none"}},{a:.3f});')
    _via(r, f'["#pv{n}t","#pv{n}c","#pv{n}s","#pv{n}d","#pv{n}o","#pv{n}l"]', a, 0.3)
    r.suono("transizione", da, 0.3)
    r.suono("pop", td, 0.25)
    r.nascondi.append((da, a))


def schede(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    sc = e.get("schede", [])[:2]
    carte = []
    for k, s in enumerate(sc):
        righe = "".join(f'<div class="px-rg"><span>{E(t)}</span><i><b id="pk{n}c{k}b{j}"></b></i><em id="pk{n}c{k}p{j}">0%</em></div>'
                        for j, (t, _) in enumerate(s.get("righe", [])[:5]))
        carte.append(f'<div class="px-sc" id="pk{n}c{k}"><h4>{E(s.get("titolo", ""))}</h4>{righe}</div>')
    r.corpo.append(f'<div class="px-st" id="pk{n}"><h3>{E(e.get("titolo", ""))}</h3></div>{"".join(carte)}'
                   f'<video class="px-win" id="pk{n}v" src="assets/tagliato.mp4" muted playsinline data-start="{da:.3f}" '
                   f'data-media-start="{da:.3f}" data-duration="{a - da:.3f}"></video>')
    r.tl.append(f'tl.set(["#pk{n}","#pk{n}v"],{{opacity:1}},{da:.3f});'
                f'tl.fromTo("#pk{n}v",{{scale:1.12,y:-300,borderRadius:0}},{{scale:1,y:0,borderRadius:36,duration:.5,ease:"power3.inOut",immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#pk{n} h3",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{da + 0.25:.3f});')
    for k, s in enumerate(sc):
        t = s.get("da", da + 0.4 + k * 2)
        fine = sc[k + 1].get("da", t + 2) if k + 1 < len(sc) else a
        r.tl.append(f'tl.fromTo("#pk{n}c{k}",{{opacity:0,y:40,scale:.96}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.4)",immediateRender:false}},{t:.3f});')
        if k + 1 < len(sc):
            r.tl.append(f'tl.to("#pk{n}c{k}",{{opacity:0,y:-30,scale:.94,duration:.25}},{fine - 0.2:.3f});')
        for j, (_, v) in enumerate(s.get("righe", [])[:5]):
            v = max(0, min(100, int(v)))
            q = t + 0.3 + j * 0.12
            r.tl.append(f'tl.fromTo("#pk{n}c{k}b{j}",{{scaleX:0}},{{scaleX:{v / 100:.3f},duration:.9,ease:"power2.out",immediateRender:false}},{q:.3f});'
                        f'(()=>{{const o={{v:0}};tl.to(o,{{v:{v},duration:.9,ease:"power2.out",onUpdate:()=>{{document.querySelector("#pk{n}c{k}p{j}").textContent=Math.round(o.v)+"%";}}}},{q:.3f});}})();')
        r.suono("pop", t, 0.25)
    r.tl.append(f'tl.to(["#pk{n}","#pk{n}c{len(sc) - 1}"],{{opacity:0,duration:.25}},{a - 0.25:.3f});'
                f'tl.to("#pk{n}v",{{scale:1.12,y:-300,borderRadius:0,duration:.25,ease:"power2.in"}},{a - 0.25:.3f});tl.set("#pk{n}v",{{opacity:0}},{a:.3f});')
    r.suono("transizione", da, 0.3)
    r.nascondi.append((da, a))


def _punto(c, quale):
    """Il punto di te a cui è legato un cartellino, da un campione della faccia (x, y, l, h)."""
    x, y, l, h = c["x"], c["y"], c["l"], c["h"]
    return {"testa": (x + l * 0.3, y + h * 0.02), "testa_dx": (x + l * 0.72, y + h * 0.02),
            "spalla": (x + l * 1.15, y + h * 1.45), "petto": (x + l * 0.3, y + h * 1.6)}.get(quale, (x + l * 0.5, y))


def cartellini(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    voci = e.get("voci", [])[:3]
    cs = [c for c in (faccia.get("campioni") or []) if da - 0.5 <= c["t"] <= a + 0.5] or \
        [{"t": da, "x": faccia["sinistra"], "y": faccia["occhi"] - 120, "l": faccia["destra"] - faccia["sinistra"],
          "h": faccia["mento"] - faccia["occhi"] + 120}]
    c0 = min(cs, key=lambda c: abs(c["t"] - da))
    cima = c0["y"] - c0["h"] * 0.25
    posti = {"testa": (70, max(cima - 300, 140)), "testa_dx": (600, max(cima - 360, 120)),
             "spalla": (690, c0["y"] + c0["h"] * 1.0), "petto": (60, c0["y"] + c0["h"] * 1.9)}
    linee, carte = [], []
    for j, v in enumerate(voci):
        quale = v.get("punto", ["testa", "testa_dx", "spalla"][j])
        lx, ly = posti.get(quale, posti["testa"])
        ax, ay = lx + 150, ly + 86 if ly < c0["y"] else ly
        px, py = _punto(c0, quale)
        carte.append(f'<div class="px-ct" id="pc{n}k{j}" style="left:{lx:.0f}px;top:{ly:.0f}px"><b>{E(v["testo"][:1].upper())}</b>'
                     f'<div><strong>{E(v["testo"])}</strong>' + (f'<small>{E(v["sotto"])}</small>' if v.get("sotto") else "") + '</div></div>')
        linee.append(f'<line id="pc{n}l{j}" x1="{ax:.0f}" y1="{ay:.0f}" x2="{px:.0f}" y2="{py:.0f}" opacity="0"/>'
                     f'<circle id="pc{n}o{j}" cx="{px:.0f}" cy="{py:.0f}" r="10" opacity="0"/>')
        t = v.get("quando", da + j * 0.8)
        r.tl.append(f'tl.fromTo("#pc{n}k{j}",{{opacity:0,scale:.6,y:10}},{{opacity:1,scale:1,y:0,duration:.3,ease:"back.out(2.2)",immediateRender:false}},{t:.3f});'
                    f'tl.fromTo("#pc{n}l{j}",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{t + 0.1:.3f});'
                    f'tl.fromTo("#pc{n}o{j}",{{opacity:0,scale:0,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:.25,ease:"back.out(3)",immediateRender:false}},{t + 0.2:.3f});')
        # il punto (e la fine del filo) segue la faccia campione per campione
        prima = c0["t"]
        for c in sorted(cs, key=lambda c: c["t"]):
            if c["t"] <= prima:
                continue
            qx, qy = _punto(c, quale)
            dur = c["t"] - prima
            r.tl.append(f'tl.to("#pc{n}l{j}",{{attr:{{x2:{qx:.0f},y2:{qy:.0f}}},duration:{dur:.2f},ease:"sine.inOut"}},{prima:.3f});'
                        f'tl.to("#pc{n}o{j}",{{attr:{{cx:{qx:.0f},cy:{qy:.0f}}},duration:{dur:.2f},ease:"sine.inOut"}},{prima:.3f});')
            prima = c["t"]
        r.suono("pop", t, 0.3)
    r.corpo.append(f'<svg class="px-fili" id="pc{n}" width="1080" height="1920">{"".join(linee)}</svg>{"".join(carte)}')
    tutti = [f'"#pc{n}k{j}"' for j in range(len(voci))] + [f'"#pc{n}l{j}"' for j in range(len(voci))] + [f'"#pc{n}o{j}"' for j in range(len(voci))]
    _via(r, "[" + ",".join(tutti) + "]", a)


def scritte(r, e, faccia):
    _css(r)
    c = r.stile["colori"]
    n, da, a = len(r.corpo), e["da"], e["a"]
    frasi = e.get("frasi", [])[:4]
    sel = r.ritaglio(da - 0.1, a + 0.1)
    cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
    righe = 5
    ys = [max(cima - 330, 40) + k * 150 for k in range(righe)]
    testo0 = (frasi[0][0] + "  ") * 6 if frasi else ""
    r.camera.insert(0, f'<div class="px-mw" id="pm{n}">' + "".join(
        f'<div class="px-mr {"pieno" if k == 0 else "vuoto"}" id="pm{n}r{k}" style="top:{y:.0f}px">{E(testo0)}</div>'
        for k, y in enumerate(ys)) + '</div>')
    r.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
                f'tl.fromTo("#bg",{{filter:"brightness(1)"}},{{filter:"brightness(.42) saturate(.7)",duration:.4,immediateRender:false}},{da:.3f});'
                f'tl.set("#bg",{{filter:"none"}},{a:.3f});'
                f'tl.fromTo("#pm{n}",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{da:.3f});')
    for k in range(righe):
        verso = -1 if k % 2 == 0 else 1
        r.tl.append(f'tl.fromTo("#pm{n}r{k}",{{x:{0 if verso < 0 else -500}}},{{x:{-500 if verso < 0 else 0},duration:{a - da:.3f},ease:"none",immediateRender:false}},{da:.3f});')
    for j, (frase, t) in enumerate(frasi):
        ultimo = j == len(frasi) - 1 and len(frasi) > 1
        testo = json_str((frase + "  ") * 6)
        if j:
            r.tl.append(f'tl.set(["#pm{n}r0","#pm{n}r1","#pm{n}r2","#pm{n}r3","#pm{n}r4"],{{textContent:{testo}}},{t:.3f});'
                        f'tl.fromTo("#pm{n}",{{scale:1.06}},{{scale:1,duration:.25,ease:"power3.out",immediateRender:false}},{t:.3f});')
            r.suono("impatto", t, 0.3)
        if ultimo:
            r.tl.append(f'tl.set("#pm{n}r0",{{color:"{c["accento"]}"}},{t:.3f});')
    r.tl.append(f'tl.to("#pm{n}",{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    r.suono("transizione", da, 0.3)
    r.nascondi.append((da, a))


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def colpiti(r, e, faccia):
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    voci = e.get("voci", [])[:4]
    cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
    y = max(cima - 230, 130)
    posti = [(90, y + 40, -6), (560, y - 30, 5), (260, y - 90, -3), (600, y + 60, 4)]
    pezzi = []
    for j, v in enumerate(voci):
        testo, t = v[0], v[1]
        sotto = v[2] if len(v) > 2 else ""
        lx, ly, rot = posti[j]
        pezzi.append(f'<div class="px-tg" id="pt{n}k{j}" style="left:{lx}px;top:{ly:.0f}px"><strong>{E(testo)}</strong>'
                     + (f'<small>{E(sotto)}</small>' if sotto else "") + f'<i id="pt{n}x{j}"></i></div>')
        r.tl.append(f'tl.fromTo("#pt{n}k{j}",{{opacity:0,scale:1.8,rotation:{rot * 3}}},{{opacity:1,scale:1,rotation:{rot},duration:.22,ease:"power4.in",immediateRender:false}},{t:.3f});'
                    f'tl.fromTo("#cam",{{x:0,y:0}},{{keyframes:[{{x:-7,y:5,duration:.035}},{{x:6,y:-4,duration:.035}},{{x:0,y:0,duration:.035}}],immediateRender:false}},{t + 0.22:.3f});')
        r.suono("impatto", t + 0.2, 0.35)
        colpo = voci[j + 1][1] - 0.35 if j + 1 < len(voci) else max(t + 0.45, a - 0.75)
        r.tl.append(f'tl.fromTo("#pt{n}x{j}",{{scaleX:0,rotation:-4}},{{scaleX:1,rotation:-4,duration:.18,ease:"power2.out",immediateRender:false}},{colpo:.3f});'
                    f'tl.to("#pt{n}k{j}",{{x:{-700 if lx < 400 else 700},y:-120,rotation:{-40 if lx < 400 else 40},opacity:0,duration:.35,ease:"power3.in"}},{colpo + 0.22:.3f});')
        r.suono("click", colpo, 0.35)
    r.corpo.append("".join(pezzi))
    r.nascondi.append((da, a))


def broll(r, e, faccia):
    """B-roll a tutto schermo: clip o foto vera al posto tuo, poi si torna su di te."""
    import os
    import shutil
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    cart = os.path.dirname(r.reel)
    dati = os.path.dirname(os.path.dirname(cart))
    p = next((q for q in (e["file"], os.path.join(cart, e["file"]), os.path.join(dati, "clip", e["file"]),
                          os.path.join(dati, "immagini", e["file"])) if os.path.isfile(q)), None)
    if not p:
        print(f'NOTA: non trovo {e["file"]} per il B-roll, lo salto')
        return
    dest = f"broll-{n}{os.path.splitext(p)[1].lower()}"
    shutil.copy2(p, os.path.join(r.assets, dest))
    finestra = e.get("finestra", r.stile.get("broll_finestra", False))
    stile = "position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:27;opacity:0"
    fondo = ""
    if finestra:   # la clip in una finestra arrotondata, sopra un fondo sfumato scuro con la luce del colore dello stile
        acc = r.stile["colori"]["accento"]
        stile = ("position:absolute;left:44px;top:70px;width:992px;height:1700px;object-fit:cover;border-radius:84px;z-index:27;opacity:0;"
                 "box-shadow:0 30px 80px rgba(0,0,0,.55)")
        fondo = (f'<div id="pb{n}f" style="position:absolute;inset:0;z-index:26;opacity:0;background:'
                 f'radial-gradient(ellipse 90% 45% at 30% 0%,{acc}cc 0%,rgba(0,0,0,0) 70%),'
                 f'radial-gradient(ellipse 90% 50% at 90% 100%,#6D4BD8aa 0%,rgba(0,0,0,0) 70%),linear-gradient(170deg,#2A2160,#120E2A 55%,#1B1238)"></div>')
    if dest.endswith((".mp4", ".mov", ".webm")):
        dentro = (f'<video id="pb{n}" src="assets/{dest}" muted playsinline data-start="{da:.3f}" data-media-start="0" '
                  f'data-duration="{a - da:.3f}" style="{stile}"></video>')
    else:
        dentro = f'<img id="pb{n}" src="assets/{dest}" style="{stile}">'
    alto = 400 if r.stile.get("testo_fisso") else 260   # con il testo fisso in alto la scritta scende sotto di lui
    testo = (f'<div class="px-bt" id="pb{n}t" style="top:{alto}px">{E(e["testo"])}</div>') if e.get("testo") else ""
    r.corpo.append(fondo + dentro + testo)
    r.tl.append(f'tl.set("#pb{n}",{{opacity:1}},{da:.3f});tl.set("#pb{n}",{{opacity:0}},{a:.3f});'
                f'tl.fromTo("#pb{n}",{{scale:1.08}},{{scale:1,duration:{a - da:.3f},ease:"none",immediateRender:false}},{da:.3f});')
    if fondo:
        r.tl.append(f'tl.set("#pb{n}f",{{opacity:1}},{da:.3f});tl.set("#pb{n}f",{{opacity:0}},{a:.3f});')
    if testo:
        r.tl.append(f'tl.fromTo("#pb{n}t",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.3,ease:"power3.out",immediateRender:false}},{da + 0.1:.3f});'
                    f'tl.set("#pb{n}t",{{opacity:0}},{a:.3f});')
    if e.get("lampo", not finestra):
        r.flash(da, 0.5, "#FFFFFF")
        r.flash(a, 0.35, "#FFFFFF")
    r.suono("transizione", da, 0.25)


def spunte(r, e, faccia):
    """Spunte: sul petto un quadratino del colore del brand con la spunta e sotto la frase in grassetto; ogni voce prende il posto della prima."""
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    voci = e.get("voci", [])[:5]
    y = min(faccia["mento"] + 40, 1240)
    r.corpo.append(f'<div class="px-sp2" id="pq{n}" style="top:{y}px"><i>✓</i>'
                   + "".join(f'<b id="pq{n}v{j}">{E(t)}</b>' for j, (t, _) in enumerate(voci)) + '</div>')
    r.tl.append(f'tl.fromTo("#pq{n}",{{opacity:0}},{{opacity:1,duration:.15,immediateRender:false}},{voci[0][1] if voci else da:.3f});'
                f'tl.fromTo("#pq{n} i",{{scale:0}},{{scale:1,duration:.3,ease:"back.out(3)",immediateRender:false}},{voci[0][1] if voci else da:.3f});')
    for j, (_, t) in enumerate(voci):
        fine = voci[j + 1][1] if j + 1 < len(voci) else a
        r.tl.append(f'tl.fromTo("#pq{n}v{j}",{{opacity:0,y:24,scale:.9}},{{opacity:1,y:0,scale:1,duration:.25,ease:"back.out(2)",immediateRender:false}},{t:.3f});'
                    f'tl.set("#pq{n}v{j}",{{opacity:0}},{fine:.3f});')
        r.suono("pop", t, 0.3)
    _via(r, f'"#pq{n}"', a, 0.2)
    r.nascondi.append((voci[0][1] if voci else da, a))


def frase(r, e, faccia):
    """Frase a tutto schermo (testo animato): lo schermo stacca su un fondo pieno e le parole si compongono una alla
    volta, ognuna con la sua misura: piccola, grande in grassetto o grande in corsivo. Poi si torna sulla persona."""
    _css(r)
    r.font_extra("InstrumentSerif-Italic.ttf")
    n, da, a = len(r.corpo), e["da"], e["a"]
    acc = r.stile["colori"]["accento"]
    rr, gg, bb = (int(acc[i:i + 2], 16) for i in (1, 3, 5))
    scuro = "#%02X%02X%02X" % tuple(round(x * .22 + 8) for x in (rr, gg, bb))
    medio = "#%02X%02X%02X" % tuple(round(x * .45 + 10) for x in (rr, gg, bb))
    fondo = (acc if e.get("fondo") == "colore" else
             f"radial-gradient(ellipse 80% 55% at 50% 45%,{medio} 0%,{scuro} 70%,#070708 100%)")
    righe = []
    for j, p in enumerate(e.get("parole", [])[:6]):
        testo, t = p[0], p[1]
        peso = p[2] if len(p) > 2 else ("grande" if j % 3 == 1 else "corsivo" if j % 3 == 2 else "piccola")
        lung = max(len(testo), 3)
        if peso == "grande":
            stile = f"font-family:'Inter Tight';font-weight:900;letter-spacing:-.04em;font-size:{min(190, int(1500 / lung))}px"
        elif peso == "corsivo":
            stile = f"font-family:'Instrument Serif';font-style:italic;font-weight:400;font-size:{min(180, int(1700 / lung))}px;color:{'#fff' if e.get('fondo') == 'colore' else r.stile['colori'].get('accento_luce', acc)}"
        else:
            stile = f"font-family:'Inter Tight';font-weight:600;font-size:{min(64, int(900 / lung))}px;opacity:.9"
        righe.append(f'<div class="px-fr-r" id="pf{n}w{j}" style="{stile}">{E(testo)}</div>')
        r.tl.append(f'tl.fromTo("#pf{n}w{j}",{{opacity:0,y:26,scale:.92,filter:"blur(14px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:.32,ease:"power3.out",immediateRender:false}},{max(t, da):.3f});')
    r.corpo.append(f'<div class="px-fr" id="pf{n}" style="background:{fondo}"><div class="px-fr-in">{"".join(righe)}</div></div>')
    r.tl.append(f'tl.set("#pf{n}",{{opacity:1}},{da:.3f});tl.set("#pf{n}",{{opacity:0}},{a:.3f});'
                f'tl.fromTo("#pf{n} .px-fr-in",{{scale:1}},{{scale:1.05,duration:{a - da:.3f},ease:"none",immediateRender:false}},{da:.3f});')
    r.suono("transizione", da, 0.25)
    r.nascondi.append((da, a))


TIPI = {"sparse": sparse, "pallini": pallini, "rivista": rivista, "schede": schede, "cartellini": cartellini,
        "scritte": scritte, "colpiti": colpiti, "broll": broll, "spunte": spunte, "frase": frase}
