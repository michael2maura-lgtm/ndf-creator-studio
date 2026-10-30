"""Sottotitoli a scelta: il catalogo e il pezzo di pagina HyperFrames che li disegna.

Ogni stile di sottotitoli dice: caratteri, quante parole alla volta, maiuscolo o no, come entra, come si vede la
parola chiave (quelle in piano "parole_chiave"). I colori "acc" (accento) e "luce" vengono dallo stile del video,
così gli stessi sottotitoli prendono i colori di chi li usa.

    import sottotitoli
    css, corpo, tl, font = sottotitoli.parti("pulito", parole, chiave, y, nascondi, colori)

Modi:
  gruppo    le parole del gruppo entrano insieme
  parola    una parola alla volta
  accumula  le parole del gruppo entrano una dopo l'altra, quando vengono dette, e restano fino alla fine del gruppo
  karaoke   tutto il gruppo è già lì, la parola detta si accende
  scrivi    le lettere si scrivono una alla volta mentre la parola viene detta
"""
import html
import json
import re

# caratteri gratuiti (licenze accanto ai file, in STUDIO/font)
FONT = {
    "jakarta": ("Plus Jakarta Sans", "PlusJakartaSans.ttf", "font-weight:200 800"),
    "archivo": ("Archivo", "Archivo.ttf", "font-weight:100 900;font-stretch:62% 125%"),
    "serif-corsivo": ("Instrument Serif Italic", "InstrumentSerif-Italic.ttf", ""),
    "serif": ("Instrument Serif", "InstrumentSerif-Regular.ttf", ""),
    "anton": ("Anton", "Anton-Regular.ttf", ""),
    "bebas": ("Bebas Neue", "BebasNeue-Regular.ttf", ""),
    "pennarello": ("Permanent Marker", "PermanentMarker-Regular.ttf", ""),
    "fumetto": ("Bangers", "Bangers-Regular.ttf", ""),
    "mono": ("JetBrains Mono", "JetBrainsMono.ttf", "font-weight:100 800"),
}

OMBRA = "text-shadow:0 4px 18px rgba(0,0,0,.65)"
ENTRA_MORBIDO = ('{opacity:0,y:16}', '{opacity:1,y:0,duration:0.18,ease:"power2.out"}')
ENTRA_SALTO = ('{scale:0.8,y:14}', '{scale:1,y:0,duration:0.14,ease:"back.out(2)"}')
# il sottotitolo è largo quanto il testo (serve a quelli con un fondo dietro)
PIASTRA = ".st{left:50%;right:auto;width:max-content;max-width:860px;transform:translate(-50%,-50%)}"
ENTRA_PUGNO = ('{scale:1.3,opacity:0}', '{scale:1,opacity:1,duration:0.12,ease:"power3.out"}')

# chiave -> descrizione. "css" usa %acc% %luce% %f-<font>%; .st è il sottotitolo, .w una parola, .k la parola chiave
CATALOGO = {
    "ndf-classico": {
        "nome": "NDF Classico", "per": "Video parlati, spiegazioni",
        "descrizione": "Una parola alla volta, maiuscola, bianca e grande.",
        "modo": "parola", "maiuscolo": True, "entra": ENTRA_SALTO, "font": ["jakarta"],
        "css": ".st{font-family:%f-jakarta%;font-weight:800;font-size:84px;line-height:1.1;color:#fff;" + OMBRA + "}"
               ".st .k{color:%acc%}",
    },
    "spaziato": {
        "nome": "Spaziato", "per": "Video semplici, tono calmo",
        "descrizione": "Poche parole piccole, bianche e distanziate; la parola chiave grande da sola.",
        "modo": "gruppo", "parole": 2, "lettere": 16, "maiuscolo": True, "entra": ENTRA_MORBIDO, "font": ["jakarta"],
        "css": ".st{font-family:%f-jakarta%;font-weight:700;font-size:34px;line-height:1.3;letter-spacing:.22em;color:#fff;"
               "text-shadow:0 2px 12px rgba(0,0,0,.55)}"
               ".st .k{display:block;font-weight:800;font-size:80px;letter-spacing:.2em;line-height:1.05}",
    },
    "ndf-targhetta": {
        "nome": "NDF Targhetta", "per": "Motion graphics, video dinamici",
        "descrizione": "Due o tre parole in maiuscolo, la parola importante su una targhetta arancione.",
        "modo": "gruppo", "parole": 3, "lettere": 13, "maiuscolo": True, "entra": ENTRA_SALTO, "font": ["archivo"],
        "css": ".st{font-family:%f-archivo%;font-weight:900;font-stretch:125%;font-size:62px;line-height:1.15;color:#fff;"
               + OMBRA + "}.st .k{background:%acc%;padding:2px 14px;border-radius:10px;text-shadow:none;"
               "box-decoration-break:clone;-webkit-box-decoration-break:clone}",
    },
    "pulito": {
        "nome": "Pulito", "per": "Tutti i giorni, va bene sempre",
        "descrizione": "Una riga semplice e leggibile, la parola importante colorata.",
        "modo": "gruppo", "parole": 4, "lettere": 22, "entra": ENTRA_MORBIDO, "font": ["jakarta"],
        "css": ".st{font-family:%f-jakarta%;font-weight:700;font-size:58px;line-height:1.2;color:#fff;" + OMBRA + "}"
               ".st .k{color:#FFD84D}",
    },
    "due-caratteri": {
        "nome": "Due caratteri", "per": "Personal brand, video curati",
        "descrizione": "Scritta bianca dritta, la parola importante in corsivo elegante dorato.",
        "modo": "gruppo", "parole": 4, "lettere": 20, "entra": ENTRA_MORBIDO, "font": ["jakarta", "serif-corsivo"],
        "css": ".st{font-family:%f-jakarta%;font-weight:600;font-size:54px;line-height:1.15;color:#fff;" + OMBRA + "}"
               ".st .k{font-family:%f-serif-corsivo%;font-weight:400;font-size:96px;color:#E9C46A;letter-spacing:-1px}",
    },
    "gigante": {
        "nome": "Gigante", "per": "Ganci, opinioni forti, energia",
        "descrizione": "Parole grosse sul petto, quella importante diventa enorme.",
        "modo": "gruppo", "parole": 2, "lettere": 12, "maiuscolo": True, "entra": ENTRA_PUGNO, "font": ["anton"],
        "su": 70,  # più in alto degli altri: sul petto
        "css": ".st{font-family:%f-anton%;font-size:112px;line-height:.95;color:#fff;" + OMBRA + "}"
               ".st .k{display:block;font-size:200px;color:%acc%}",
    },
    "karaoke": {
        "nome": "Karaoke", "per": "Chi parla veloce, sfondi pieni",
        "descrizione": "Tutta la frase su un fondo scuro, la parola che dici si accende.",
        "modo": "karaoke", "parole": 4, "lettere": 22, "maiuscolo": True, "entra": ENTRA_MORBIDO, "font": ["jakarta"],
        "css": PIASTRA + ".st{font-family:%f-jakarta%;font-weight:800;font-size:54px;line-height:1.25;padding:18px 30px;"
               "border-radius:22px;background:rgba(10,10,12,.62)}.st .w{color:rgba(255,255,255,.45)}"
               ".st .w[data-on]{color:#fff}.st .k[data-on]{color:%luce%}",
    },
    "macchina": {
        "nome": "Macchina da scrivere", "per": "AI, tecnologia, tutorial",
        "descrizione": "Le lettere si scrivono una per una, con un carattere da computer.",
        "modo": "scrivi", "parole": 4, "lettere": 24, "entra": ENTRA_MORBIDO, "font": ["mono"],
        "css": PIASTRA + ".st{font-family:%f-mono%;font-weight:600;font-size:46px;line-height:1.3;color:#fff;padding:14px 24px;"
               "border-radius:12px;background:rgba(10,10,12,.7);border-left:6px solid %acc%}.st .k{color:%luce%}",
    },
    "film": {
        "nome": "Film", "per": "Video emozionali, racconti, b-roll",
        "descrizione": "Sottotitoli piccoli in basso, in corsivo dorato, come al cinema.",
        "modo": "gruppo", "parole": 7, "lettere": 36, "entra": ('{opacity:0}', '{opacity:1,duration:0.3,ease:"none"}'),
        "font": ["serif-corsivo"], "giu": 230,
        "css": ".st{font-family:%f-serif-corsivo%;font-size:62px;line-height:1.2;color:#F2D27A;"
               "text-shadow:0 2px 10px rgba(0,0,0,.8)}.st .k{color:#FFE7A8}",
    },
    "pennarello": {
        "nome": "Pennarello", "per": "Coach, creator, toni personali",
        "descrizione": "Scritta pulita, la parola importante scritta a mano col pennarello.",
        "modo": "gruppo", "parole": 4, "lettere": 20, "entra": ENTRA_MORBIDO, "font": ["jakarta", "pennarello"],
        "k_entra": ('{scale:0.4,rotation:-12}', '{scale:1,rotation:-4,duration:0.22,ease:"back.out(2.5)"}'),
        "css": ".st{font-family:%f-jakarta%;font-weight:700;font-size:54px;line-height:1.2;color:#fff;" + OMBRA + "}"
               ".st .k{display:inline-block;font-family:%f-pennarello%;font-weight:400;font-size:84px;color:%luce%;"
               "transform:rotate(-4deg)}",
    },
    "contorno": {
        "nome": "Contorno", "per": "Sport, fitness, frasi forti",
        "descrizione": "Lettere alte e strette, la parola importante disegnata solo col bordo.",
        "modo": "gruppo", "parole": 2, "lettere": 14, "maiuscolo": True, "entra": ENTRA_PUGNO, "font": ["bebas"],
        "css": ".st{font-family:%f-bebas%;font-size:130px;line-height:.95;letter-spacing:2px;color:#fff;" + OMBRA + "}"
               ".st .k{color:transparent;-webkit-text-stroke:4px #fff;text-shadow:none}",
    },
    "pillole": {
        "nome": "Pillole", "per": "Spiegazioni, passi, liste",
        "descrizione": "Ogni parola su una pillola colorata, entrano una alla volta.",
        "modo": "accumula", "parole": 3, "lettere": 20, "entra": ENTRA_SALTO, "font": ["jakarta"],
        "css": ".st{font-family:%f-jakarta%;font-weight:700;font-size:44px;line-height:1.5}"
               ".st .w{display:inline-block;margin:6px 4px;padding:6px 22px 9px;border-radius:999px;background:%acc%;color:#fff;"
               "box-shadow:0 8px 24px rgba(0,0,0,.35)}.st .k{background:#fff;color:%acc%}",
    },
    "etichetta": {
        "nome": "Etichetta fissa", "per": "Video semplici, un argomento solo",
        "descrizione": "In alto un'etichetta con la parola importante, sotto sottotitoli piccoli.",
        "modo": "gruppo", "parole": 4, "lettere": 24, "entra": ENTRA_MORBIDO, "font": ["jakarta"], "etichetta": True,
        "css": ".st{font-family:%f-jakarta%;font-weight:600;font-size:46px;line-height:1.2;color:#fff;" + OMBRA + "}"
               ".et{position:absolute;left:50%;top:330px;transform:translateX(-50%);z-index:31;opacity:0;white-space:nowrap;"
               "font-family:%f-jakarta%;font-weight:800;font-size:44px;letter-spacing:3px;text-transform:uppercase;color:#fff;"
               "background:%acc%;padding:10px 28px;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.35)}",
    },
    "neon": {
        "nome": "Neon", "per": "Video serali, musica, atmosfera",
        "descrizione": "Le parole si accendono con un bagliore, come un'insegna.",
        "modo": "gruppo", "parole": 3, "lettere": 16, "maiuscolo": True, "font": ["jakarta"],
        "entra": ('{opacity:0}', '{opacity:1,duration:0.22,ease:"steps(4)"}'),
        "css": ".st{font-family:%f-jakarta%;font-weight:800;font-size:66px;line-height:1.15;color:#fff;"
               "text-shadow:0 0 6px #fff,0 0 18px %luce%,0 0 40px %acc%,0 0 70px %acc%}"
               ".st .k{color:%luce%;text-shadow:0 0 6px %luce%,0 0 20px %acc%,0 0 50px %acc%}",
    },
    "minuscolo": {
        "nome": "Minuscolo enorme", "per": "Ganci, storie, lifestyle",
        "descrizione": "Tutto minuscolo, gigante e stretto.",
        "modo": "gruppo", "parole": 2, "lettere": 12, "entra": ENTRA_PUGNO, "font": ["jakarta"], "su": 40,
        "css": ".st{font-family:%f-jakarta%;font-weight:800;font-size:124px;line-height:.92;letter-spacing:-5px;color:#fff;"
               + OMBRA + ";text-transform:lowercase}.st .k{color:%luce%}",
    },
    "elegante": {
        "nome": "Elegante", "per": "Lusso, benessere, toni calmi",
        "descrizione": "Carattere sottile e raffinato, entra piano.",
        "modo": "gruppo", "parole": 4, "lettere": 22, "font": ["serif", "serif-corsivo"],
        "entra": ('{opacity:0,y:10}', '{opacity:1,y:0,duration:0.4,ease:"power1.out"}'),
        "css": ".st{font-family:%f-serif%;font-size:74px;line-height:1.1;color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.6)}"
               ".st .k{font-family:%f-serif-corsivo%;color:#F3E3C3}",
    },
    "colorato": {
        "nome": "Colorato", "per": "Video divertenti, ragazzi, energia",
        "descrizione": "Ogni parola entra con un salto e un colore diverso.",
        "modo": "accumula", "parole": 3, "lettere": 18, "maiuscolo": True, "font": ["jakarta"],
        "entra": ('{scale:0.3,rotation:-8,opacity:0}', '{scale:1,rotation:0,opacity:1,duration:0.2,ease:"back.out(3)"}'),
        "css": ".st{font-family:%f-jakarta%;font-weight:800;font-size:72px;line-height:1.1;" + OMBRA + "}"
               ".st .w{display:inline-block}.st .w:nth-child(4n+1){color:#FFD84D}.st .w:nth-child(4n+2){color:#5FD3FF}"
               ".st .w:nth-child(4n+3){color:#FF7BC0}.st .w:nth-child(4n+4){color:#8CFF72}",
    },
    "evidenziatore": {
        "nome": "Evidenziatore", "per": "Spiegazioni, consigli, studio",
        "descrizione": "La parola importante con l'evidenziatore giallo che passa dietro.",
        "modo": "gruppo", "parole": 4, "lettere": 20, "entra": ENTRA_MORBIDO, "font": ["jakarta"],
        "k_entra": ('{backgroundSize:"0% 100%"}', '{backgroundSize:"100% 100%",duration:0.3,ease:"power2.out"}'),
        "css": ".st{font-family:%f-jakarta%;font-weight:800;font-size:60px;line-height:1.25;color:#fff;" + OMBRA + "}"
               ".st .k{color:#151515;text-shadow:none;padding:0 10px;background-repeat:no-repeat;background-size:100% 100%;"
               "background-image:linear-gradient(transparent 12%,#FFE14D 12%,#FFE14D 88%,transparent 88%)}",
    },
    "fumetto": {
        "nome": "Fumetto", "per": "Video comici, battute, reazioni",
        "descrizione": "Le parole dentro una nuvoletta, come nei fumetti.",
        "modo": "gruppo", "parole": 4, "lettere": 20, "maiuscolo": True, "entra": ENTRA_SALTO, "font": ["fumetto"], "su": 30,
        "css": PIASTRA + ".st{font-family:%f-fumetto%;font-size:66px;letter-spacing:2px;line-height:1.05;color:#141414;"
               "background:#fff;border:6px solid #141414;border-radius:44px;padding:20px 40px 18px;box-shadow:8px 10px 0 #141414}"
               ".st::after{content:'';position:absolute;left:50%;bottom:-38px;margin-left:-20px;border:20px solid transparent;"
               "border-top:26px solid #141414}.st .k{color:%acc%}",
    },
    "telegiornale": {
        "nome": "Telegiornale", "per": "Notizie, annunci, novità",
        "descrizione": "Una fascia in basso, come al TG.",
        "modo": "gruppo", "parole": 6, "lettere": 30, "maiuscolo": True, "font": ["jakarta"], "giu": 260,
        "entra": ('{x:-50,opacity:0}', '{x:0,opacity:1,duration:0.2,ease:"power2.out"}'),
        "css": ".st{left:0;right:0;text-align:left;font-family:%f-jakarta%;font-weight:800;font-size:46px;line-height:1.2;"
               "color:#fff;background:linear-gradient(90deg,%acc% 0 14px,rgba(12,12,14,.86) 14px);padding:20px 60px 22px 60px}"
               ".st .k{color:%luce%}",
    },
    "spessore": {
        "nome": "Spessore", "per": "Prodotti, tecnologia, video puliti",
        "descrizione": "Le parole normali sottili, quella importante nera e spessa.",
        "modo": "gruppo", "parole": 4, "lettere": 22, "entra": ENTRA_MORBIDO, "font": ["jakarta"],
        "css": ".st{font-family:%f-jakarta%;font-weight:250;font-size:66px;line-height:1.15;color:#fff;" + OMBRA + "}"
               ".st .k{font-weight:800}",
    },
}


def gruppi(parole, max_parole, max_lettere):
    """Divide le parole in gruppi: si va a capo alla punteggiatura, a max_parole o quando le lettere sono troppe."""
    out, g = [], []
    for w in parole:
        if g and sum(len(x["testo"]) for x in g) + len(w["testo"]) > max_lettere:
            out.append(g)
            g = []
        g.append(w)
        if re.search(r"[.,?!;:]$", w["testo"]) or len(g) >= max_parole:
            out.append(g)
            g = []
    if g:
        out.append(g)
    return out


def _font_css(chiavi):
    righe = []
    for k in chiavi:
        fam, file, extra = FONT[k]
        righe.append(f"@font-face{{font-family:'{fam}';src:url('assets/{file}');{extra}}}")
    return "".join(righe)


def parti(nome, parole, chiave, y, nascondi, colori):
    """css, [html], [righe di timeline], [file dei caratteri da copiare in assets] per i sottotitoli `nome`.
    y = dove sta il centro della riga; nascondi = [(da, a)] in cui i sottotitoli non si vedono (titoli, scene)."""
    s = CATALOGO[nome]
    css = s["css"].replace("%acc%", colori.get("accento", "#E86530")).replace("%luce%", colori.get("accento_luce", "#FF8A4C"))
    for k, (fam, _, _) in FONT.items():
        css = css.replace(f"%f-{k}%", f"'{fam}'")
    css = _font_css(s["font"]) + (".st{position:absolute;left:80px;right:110px;text-align:center;opacity:0;z-index:30;"
                                  "transform:translateY(-50%)}") + css
    y = y - s.get("su", 0) + s.get("giu", 0)
    modo = s["modo"]
    n_par, n_let = (1, 99) if modo == "parola" else (s.get("parole", 3), s.get("lettere", 16))
    corpo, tl = [], []
    gs = gruppi(parole, n_par, n_let)
    for i, g in enumerate(gs):
        da = g[0]["da"]
        if any(x <= da < z for x, z in nascondi):
            continue
        fine = gs[i + 1][0]["da"] if i + 1 < len(gs) else g[-1]["a"]
        fine = min([fine, g[-1]["a"] + 0.6] + [x for x, _ in nascondi if x > da])
        pezzi = []
        for j, w in enumerate(g):
            t = re.sub(r"[.,;:!?\"«»]", "", w["testo"])
            t = t.upper() if s.get("maiuscolo") else t
            cl = "w k" if re.sub(r"[^\w]", "", t.lower()) in chiave else "w"
            pezzi.append(f'<span class="{cl}" id="u{i}w{j}">{html.escape(t)}</span>')
        corpo.append(f'<div class="st" id="u{i}" style="top:{y}px">{" ".join(pezzi)}</div>')
        da_v, a_v = s["entra"]
        if modo in ("gruppo", "parola", "karaoke"):
            tl.append(f'tl.set("#u{i}",{{opacity:1}},{da:.3f});tl.fromTo("#u{i} .w",{da_v},{a_v},{da:.3f});')
            for j, w in enumerate(g):  # la parola chiave fa qualcosa in più quando viene detta (evidenziatore, pennarello)
                if s.get("k_entra") and 'class="w k"' in pezzi[j]:
                    tl.append(f'tl.fromTo("#u{i}w{j}",{s["k_entra"][0]},{s["k_entra"][1]},{w["da"]:.3f});')
        elif modo in ("accumula", "scrivi"):
            tl.append(f'tl.set("#u{i}",{{opacity:1}},{da:.3f});tl.set("#u{i} .w",{{opacity:0}},{da:.3f});')
            for j, w in enumerate(g):
                if modo == "accumula":
                    tl.append(f'tl.set("#u{i}w{j}",{{opacity:1}},{w["da"]:.3f});tl.fromTo("#u{i}w{j}",{da_v},{a_v},{w["da"]:.3f});')
                else:
                    tl.append(f'tl.set("#u{i}w{j}",{{opacity:1}},{w["da"]:.3f});'
                              f'scriviLettere("#u{i}w{j}",{w["da"]:.3f},{max(w["a"] - w["da"], 0.12):.3f});')
        if modo == "karaoke":
            for j, w in enumerate(g):
                tl.append(f'tl.set("#u{i}w{j}",{{attr:{{"data-on":1}}}},{w["da"]:.3f});')
        tl.append(f'tl.set("#u{i}",{{opacity:0}},{fine:.3f});')
    if s.get("etichetta"):  # etichetta in alto: l'ultima parola chiave detta, resta finché non ne arriva un'altra
        corpo.append('<div class="et" id="et"></div>')
        visti = [(w["da"], re.sub(r"[^\w]", "", w["testo"])) for w in parole
                 if re.sub(r"[^\w]", "", w["testo"].lower()) in chiave and not any(x <= w["da"] < z for x, z in nascondi)]
        for n, (t, testo) in enumerate(visti):
            if n == 0:
                tl.append(f'tl.set("#et",{{opacity:1}},{t:.3f});')
            tl.append(f'tl.set("#et",{{textContent:{json.dumps(testo.upper())}}},{t:.3f});'
                      f'tl.fromTo("#et",{{scale:0.85}},{{scale:1,duration:0.2,ease:"back.out(2)"}},{t:.3f});')
        if nascondi:
            for x, z in nascondi:
                tl.append(f'tl.set("#et",{{autoAlpha:0}},{x:.3f});tl.set("#et",{{autoAlpha:1}},{z:.3f});')
    font = [FONT[k][1] for k in s["font"]]
    return css, corpo, tl, font


# funzione JS che serve al modo "scrivi": lettere che compaiono una alla volta
JS = """function scriviLettere(sel, da, dur) {
  const el = document.querySelector(sel); const testo = el.textContent; const o = {p: 0};
  tl.set(el, {textContent: ""}, Math.max(0, da - 0.001));
  tl.to(o, {p: 1, duration: dur, ease: "none", onUpdate: () => { el.textContent = testo.slice(0, Math.ceil(o.p * testo.length)); }}, da);
}"""
