"""Grafiche del modello "Chiaro" (16/11/2026): il livello di mezzo tra Pulito (solo sottotitoli) ed Energia (una trovata
ogni 3 secondi). Idee generiche (titolo sul gancio, parole chiave in grande, schede sui concetti chiave), grafica nostra.

Nel piano (tempi del video TAGLIATO):
 {"tipo": "evidenza", "da", "a", "sopra": "un post", "testo": "noioso", "grande": true}
     sopra la testa due righe: quella piccola dritta (le parole dette prima) e sotto la parola chiave in corsivo
     elegante, grande, che sale e si mette a fuoco. "grande": true per il titolo sul gancio (primi 2 secondi).
 {"tipo": "scheda", "da", "a", "numero": 3, "testo": "Gli errori", "sotto": "che rallentano i tuoi reel"}
     in basso, sotto i sottotitoli (che salgono sopra di lei), una scheda scura arrotondata e grande: a sinistra il quadratino del colore del brand con il numero (o "icona":
     un'emoji al posto del numero), a destra il titolo e una riga sotto. Sui concetti chiave, una ogni 7-8 secondi.
"""
import html

E = html.escape


def _css(r):
    if getattr(r, "css_chiaro", False):
        return
    r.css_chiaro = True
    r.font_extra("PlusJakartaSans.ttf")
    c = r.stile["colori"]
    ft = r.stile["font"]["titoli"]
    # il corsivo è il font dei titoli dello stile (Instrument Serif corsivo); se nella pagina si sceglie un font per i titoli, vale quello (ritocchi.titoli)
    r.corpo.append(
        "<style>@font-face{font-family:'Plus Jakarta Sans';src:url('assets/PlusJakartaSans.ttf');font-weight:200 800}"
        ".ch-e{position:absolute;left:50px;right:50px;text-align:center;z-index:31;opacity:0}"
        ".ch-e .s{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;color:#fff;line-height:1.1;"
        "text-shadow:0 3px 16px rgba(0,0,0,.65)}"
        f".ch-e .k{{font-family:'{ft['famiglia']}';font-weight:{ft.get('peso', 400)};font-stretch:{ft.get('larghezza', 100)}%;color:{c['accento']};"
        "line-height:.95;white-space:nowrap;-webkit-text-stroke:2px rgba(20,10,6,.55);paint-order:stroke fill;text-shadow:0 3px 0 rgba(0,0,0,.35),0 6px 26px rgba(0,0,0,.9),0 0 50px rgba(0,0,0,.5)}"
        ".ch-c{position:absolute;left:50px;width:920px;bottom:450px;z-index:31;opacity:0;display:flex;align-items:center;gap:32px;"
        "box-sizing:border-box;padding:28px 36px;border-radius:38px;background:rgba(18,18,20,.92);"
        "border:2px solid rgba(255,255,255,.12);box-shadow:0 22px 50px rgba(0,0,0,.5)}"
        f".ch-c b{{flex:none;display:grid;place-items:center;width:128px;height:128px;border-radius:30px;background:{c['accento']};"
        "color:#fff;font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:80px;line-height:1}"
        ".ch-c b img{width:86px;height:86px;object-fit:contain}"
        ".ch-c div{min-width:0}"
        ".ch-c .t{font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:62px;color:#fff;line-height:1.08}"
        ".ch-c .u{font-family:'Plus Jakarta Sans',sans-serif;font-weight:500;font-size:40px;color:rgba(255,255,255,.75);"
        "line-height:1.2;margin-top:8px}"
        "</style>")


def _grandezza(r):
    return max(70, min(140, int((r.stile.get("ritocchi_titoli") or {}).get("grandezza") or 100))) / 100


def evidenza(r, e, faccia):
    """Riga piccola + parola chiave in corsivo grande, sopra la testa."""
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    g = _grandezza(r)
    grande = e.get("grande")
    testo, sopra = e["testo"], e.get("sopra", "")
    dim = int(min((155 if grande else 130) * g, 940 / (max(len(testo), 1) * 0.42)))
    dim_s = int((52 if grande else 46) * min(g, 1.2))
    testa = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95   # la cima della testa
    alto = 320 if r.stile.get("testo_fisso") else 175
    y = int(max(alto, min(testa - dim - (dim_s if sopra else 0) - 150, 460)))   # largo sopra i capelli, anche con lo zoom
    r.corpo.append(f'<div class="ch-e" id="ce{n}" style="top:{y}px">'
                   + (f'<div class="s" id="ce{n}s" style="font-size:{dim_s}px">{E(sopra)}</div>' if sopra else "")
                   + f'<div class="k" id="ce{n}k" style="font-size:{dim}px">{E(testo)}</div></div>')
    r.tl.append(f'tl.set("#ce{n}",{{opacity:1}},{da - 0.05:.3f});')
    if sopra:
        r.tl.append(f'tl.fromTo("#ce{n}s",{{opacity:0,y:18}},{{opacity:1,y:0,duration:.25,ease:"power2.out",immediateRender:false}},{da - 0.05:.3f});')
    r.tl.append(f'tl.fromTo("#ce{n}k",{{opacity:0,y:40,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.4,ease:"power3.out",immediateRender:false}},{da + (0.12 if sopra else 0):.3f});'
                f'tl.to("#ce{n}",{{opacity:0,y:-16,duration:.25}},{a - 0.25:.3f});')
    r.suono("pop", da, 0.2)
    r.nascondi.append((da, a))   # i sottotitoli direbbero le stesse parole: si tolgono mentre c'è la parola chiave


def scheda(r, e, faccia):
    """Scheda in basso con il numero (o l'icona), il titolo e una riga sotto."""
    _css(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    if e.get("icona"):
        import effetti_sopra
        dentro = f'<img src="assets/{effetti_sopra._emoji_png(r, e["icona"])}">'
    else:
        dentro = E(str(e.get("numero", "")))
    # in basso, appoggiata al bordo della zona sicura (1470 px): i sottotitoli salgono sopra la scheda per il suo tempo
    righe = (1 if len(e["testo"]) <= 18 else 2) * 67 + ((1 if len(e.get("sotto", "")) <= 30 else 2) * 48 + 8 if e.get("sotto") else 0)
    alta = max(128, righe) + 60
    y_sub = int(max(1470 - alta - 150, faccia["mento"] + 50))
    r.corpo.append(f'<div class="ch-c" id="cc{n}"><b id="cc{n}b">{dentro}</b><div>'
                   f'<div class="t">{E(e["testo"])}</div>' + (f'<div class="u">{E(e["sotto"])}</div>' if e.get("sotto") else "")
                   + "</div></div>")
    r.tl.append(f'tl.fromTo("#cc{n}",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.35,ease:"power3.out",immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#cc{n}b",{{scale:.4,rotation:-12}},{{scale:1,rotation:0,duration:.35,ease:"back.out(2.2)",immediateRender:false}},{da + 0.12:.3f});'
                f'tl.to("#cc{n}",{{opacity:0,y:30,duration:.25}},{a - 0.25:.3f});'
                f'tl.to(".st,.sub",{{top:{y_sub},duration:.3,ease:"power2.out"}},{da - 0.05:.3f});'
                f'tl.to(".st,.sub",{{top:{r.y_sub},duration:.3,ease:"power2.inOut"}},{a - 0.2:.3f});')
    r.suono("pop", da + 0.1, 0.22)
    r.sotto_scheda = getattr(r, "sotto_scheda", []) + [(da, a)]


TIPI = {"evidenza": evidenza, "scheda": scheda}
