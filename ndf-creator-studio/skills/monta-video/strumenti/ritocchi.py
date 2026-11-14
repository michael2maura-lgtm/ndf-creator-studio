"""Le scelte della pagina "Scegli il tuo stile" applicate al reel: font e lettere dei titoli, font, lettere e colori
dei sottotitoli, testo fisso in alto. Le usano grafica.py e costruisci.py (titoli, testo fisso) e sottotitoli.parti
(sottotitoli). La pagina fa le stesse cose in JavaScript per il telefono di anteprima (pagina/scegli.html): se cambi
qui, cambia anche là.

In scelte.json:
  "titoli": {"font": chiave di FONT, "grandezza": 80-130, "grassetto": true/false/null, "corsivo": bool,
             "maiuscolo": "su"/"giu"/null, "ombra": "leggera"/"nera"/"bianca"/"colore"/"nessuna"/null}
  "sott":   {"font", "font_k", "maiuscolo": "su"/"giu"/"no"/null, "grassetto", "corsivo", "ombra",
             "testo": "#RRGGBB", "evidenza": "#RRGGBB", "riquadro": "#RRGGBB"}
  "testo_fisso": "...", "fisso": {"testo": "#RRGGBB" o null, "sfondo": "#RRGGBB"/"nessuno"/null}
null = come lo stile.
"""
import os
import re

STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# chiave: (nome, file in STUDIO/font, gruppo, peso di serie, pesi del file variabile o "")
FONT = {
    "instrument": ("Instrument Serif", "InstrumentSerif-Regular.ttf", "Eleganti", 400, ""),
    "playfair": ("Playfair Display", "PlayfairDisplay.ttf", "Eleganti", 700, "400 900"),
    "fraunces": ("Fraunces", "Fraunces.ttf", "Eleganti", 700, "100 900"),
    "bodoni": ("Bodoni Moda", "BodoniModa.ttf", "Eleganti", 700, "400 900"),
    "cormorant": ("Cormorant Garamond", "CormorantGaramond.ttf", "Eleganti", 600, "300 700"),
    "stix": ("STIX Two Text", "STIXTwoText.ttf", "Eleganti", 700, "400 700"),
    "anton": ("Anton", "Anton-Regular.ttf", "Forti", 400, ""),
    "bebas": ("Bebas Neue", "BebasNeue-Regular.ttf", "Forti", 400, ""),
    "archivo-black": ("Archivo Black", "ArchivoBlack-Regular.ttf", "Forti", 400, ""),
    "archivo": ("Archivo", "Archivo.ttf", "Forti", 900, "100 900"),
    "unbounded": ("Unbounded", "Unbounded.ttf", "Forti", 800, "200 900"),
    "bricolage": ("Bricolage Grotesque", "BricolageGrotesque.ttf", "Moderni", 800, "200 800"),
    "spartan": ("League Spartan", "LeagueSpartan.ttf", "Moderni", 800, "100 900"),
    "space": ("Space Grotesk", "SpaceGrotesk.ttf", "Moderni", 700, "300 700"),
    "outfit": ("Outfit", "Outfit.ttf", "Moderni", 700, "100 900"),
    "jakarta": ("Plus Jakarta Sans", "PlusJakartaSans.ttf", "Moderni", 800, "200 800"),
    "inter": ("Inter", "Inter.ttf", "Moderni", 800, "100 900"),
    "poppins": ("Poppins", "Poppins-SemiBold.ttf", "Moderni", 600, ""),
    "fredoka": ("Fredoka", "Fredoka.ttf", "Simpatici", 600, "300 700"),
    "shrikhand": ("Shrikhand", "Shrikhand-Regular.ttf", "Simpatici", 400, ""),
    "bangers": ("Bangers", "Bangers-Regular.ttf", "Simpatici", 400, ""),
    "caveat": ("Caveat", "Caveat.ttf", "A mano", 700, "400 700"),
    "pennarello": ("Permanent Marker", "PermanentMarker-Regular.ttf", "A mano", 400, ""),
    "kalam": ("Kalam", "Kalam-Bold.ttf", "A mano", 700, ""),
    "dancing": ("Dancing Script", "DancingScript.ttf", "A mano", 700, "400 700"),
    "pacifico": ("Pacifico", "Pacifico-Regular.ttf", "A mano", 400, ""),
    "vibes": ("Great Vibes", "GreatVibes-Regular.ttf", "A mano", 400, ""),
    # corsivi veri: per la riga sotto / le parole in evidenza dei sottotitoli
    "instrument-c": ("Instrument Serif Italic", "InstrumentSerif-Italic.ttf", "Corsivi", 400, ""),
    "playfair-c": ("Playfair Display Italic", "PlayfairDisplay-Italic.ttf", "Corsivi", 600, "400 900"),
    "fraunces-c": ("Fraunces Italic", "Fraunces-Italic.ttf", "Corsivi", 500, "100 900"),
    "cormorant-c": ("Cormorant Garamond Italic", "CormorantGaramond-Italic.ttf", "Corsivi", 600, "300 700"),
    "stix-c": ("STIX Two Text Italic", "STIXTwoText-Italic.ttf", "Corsivi", 600, "400 700"),
    "bodoni-c": ("Bodoni Moda Italic", "BodoniModa-Italic.ttf", "Corsivi", 500, "400 900"),
}
# i font per i titoli (nella pagina, in quest'ordine); per i sottotitoli tutti tranne quelli da insegna troppo larghi
TITOLI = [k for k in FONT if not k.endswith("-c")]
SOTT = [k for k in FONT if not k.endswith("-c") and k not in ("shrikhand", "vibes")]
SOTT_K = [k for k in FONT if k.endswith("-c")] + ["caveat", "kalam", "dancing", "pacifico", "vibes", "pennarello", "anton", "bebas",
                                                   "archivo-black", "bricolage", "jakarta", "fredoka", "shrikhand"]

OMBRE = {
    "leggera": "0 3px 12px rgba(0,0,0,.45)",
    "nera": "0 4px 16px rgba(0,0,0,.85),0 1px 3px rgba(0,0,0,.9)",
    "bianca": "0 0 16px rgba(255,255,255,.75),0 0 3px rgba(255,255,255,.9)",
    "colore": "0 0 22px %acc%,0 4px 14px rgba(0,0,0,.5)",
    "nessuna": "none",
}
COLORE = re.compile(r"#[0-9A-Fa-f]{6}")


def file_font(k):
    return os.path.join(STUDIO, "font", FONT[k][1])


def font_face(k):
    nome, file, _, _, pesi = FONT[k]
    stile = ";font-style:italic" if k.endswith("-c") else ""
    return f"@font-face{{font-family:'{nome}';src:url('assets/{file}');{'font-weight:' + pesi if pesi else ''}{stile}}}"


def font_titoli(stile, t):
    """Il font dei titoli scelto al posto di quello dello stile (stile["font"]["titoli"])."""
    k = (t or {}).get("font")
    if k not in FONT:
        return stile
    nome, _, _, peso, _ = FONT[k]
    if t.get("grassetto") is True:
        peso = 900 if FONT[k][4] else peso
    elif t.get("grassetto") is False:
        peso = 400
    font = dict(stile["font"], titoli={"file": file_font(k), "famiglia": nome, "peso": peso, "larghezza": 100})
    return dict(stile, font=font)


def _regole(pagina, famiglia):
    """Le regole CSS che usano il font dei titoli (non la @font-face)."""
    return re.compile(r"\{[^{}]*font-family:\s*'" + re.escape(famiglia) + r"'[^{}]*\}")


def titoli(pagina, famiglia, t, acc):
    """Grandezza, grassetto, corsivo, maiuscolo e ombra su tutte le scritte nel font dei titoli."""
    t = t or {}
    if not t:
        return pagina
    extra = ""
    if t.get("grassetto") is True:
        extra += ";font-weight:900"
    elif t.get("grassetto") is False:
        extra += ";font-weight:400"
    if t.get("corsivo"):
        extra += ";font-style:italic"
    if t.get("maiuscolo") == "su":
        extra += ";text-transform:uppercase"
    elif t.get("maiuscolo") == "giu":
        extra += ";text-transform:lowercase"
    if t.get("ombra") in OMBRE:
        extra += ";text-shadow:" + OMBRE[t["ombra"]].replace("%acc%", acc or "#E86530")
    g = t.get("grandezza") or 100
    g = max(70, min(140, int(g))) / 100

    def cambia(m):
        r = m.group(0)
        if "src:url" in r:   # la @font-face resta com'è
            return r
        if g != 1:
            r = re.sub(r"font-size:(\d+(?:\.\d+)?)px", lambda x: f"font-size:{float(x.group(1)) * g:.0f}px", r)
        return r[:-1] + extra + "}"
    return _regole(pagina, famiglia).sub(cambia, pagina)


def sottotitoli(s, css_stile, modo, acc):
    """(css in più, maiuscolo) per i sottotitoli: va in fondo al css dello stile di sottotitoli. maiuscolo: True/False/None."""
    s = s or {}
    css, font = [], []
    if s.get("font") in FONT:
        font.append(s["font"])
        css.append(f".st,.st .r2,.st .ra{{font-family:'{FONT[s['font']][0]}'}}")
    if s.get("font_k") in FONT:
        font.append(s["font_k"])
        css.append(f".st .k,.st .r1,.st .rb{{font-family:'{FONT[s['font_k']][0]}';font-style:normal}}")
    if s.get("grassetto") is True:
        css.append(".st,.st .w{font-weight:800}")
    elif s.get("grassetto") is False:
        css.append(".st,.st .w{font-weight:400}")
    if s.get("corsivo"):
        css.append(".st .w{font-style:italic}")
    if s.get("maiuscolo") == "giu":
        css.append(".st{text-transform:lowercase}")
    elif s.get("maiuscolo") in ("su", "no"):
        css.append(".st{text-transform:none}")
    if s.get("ombra") in OMBRE:
        css.append(".st,.st .w{text-shadow:" + OMBRE[s["ombra"]].replace("%acc%", acc or "#E86530") + "}")
    if COLORE.fullmatch(s.get("testo") or ""):
        css.append(f".st .w[data-on]{{color:{s['testo']}}}" if modo == "karaoke" else f".st{{color:{s['testo']}}}")
    if COLORE.fullmatch(s.get("evidenza") or ""):
        k_fondo = re.search(r"\.st \.k\{[^}]*background", css_stile)
        if k_fondo:
            css.append(f".st .k{{background:{s['evidenza']};background-image:none}}")
        else:
            css.append(f".st .k,.st .k[data-on],.st .rb{{color:{s['evidenza']}}}")
    if COLORE.fullmatch(s.get("riquadro") or "") and ("background:rgba(10,10,12" in css_stile or "/*riq*/" in css_stile):
        h = s["riquadro"]
        css.append(f".st{{background:rgba({int(h[1:3], 16)},{int(h[3:5], 16)},{int(h[5:7], 16)},.82)}}")
    maiusc = {"su": True, "giu": False, "no": False}.get(s.get("maiuscolo"))
    return "".join(font_face(k) for k in font) + "".join(css), maiusc, [FONT[k][1] for k in font]


def testo_fisso(pagina, testo, f, famiglia, acc):
    """Una scritta che resta in alto per tutto il reel, nella zona sicura."""
    if not testo:
        return pagina
    import html
    f = f or {}
    colore = f.get("testo") if COLORE.fullmatch(f.get("testo") or "") else "#FFFFFF"
    sfondo = f.get("sfondo")
    fondo = "transparent" if sfondo == "nessuno" else (sfondo if COLORE.fullmatch(sfondo or "") else "rgba(12,12,14,.72)")
    css = (f".fisso-top{{position:absolute;left:50%;top:235px;transform:translateX(-50%);z-index:45;white-space:nowrap;"
           f"font-family:'{famiglia}';font-weight:800;font-size:40px;letter-spacing:.5px;color:{colore};background:{fondo};"
           f"padding:12px 26px 14px;border-radius:14px;{'text-shadow:0 2px 10px rgba(0,0,0,.6);' if fondo == 'transparent' else ''}}}")
    div = f'<div class="fisso-top">{html.escape(testo)}</div>'
    pagina = pagina.replace("</style>", css + "</style>", 1)
    return re.sub(r'(<div id="root"[^>]*>)', lambda m: m.group(1) + "\n" + div, pagina, count=1)


def per_la_pagina():
    """L'elenco dei font per la pagina: [{chiave, nome, file, gruppo, peso, pesi}] e le liste per titoli e sottotitoli."""
    return {"font": [{"chiave": k, "nome": v[0], "file": v[1], "gruppo": v[2], "peso": v[3], "pesi": v[4]}
                     for k, v in FONT.items()],
            "titoli": TITOLI, "sott": SOTT, "sott_k": SOTT_K, "ombre": OMBRE}
