"""Il brand del cliente, fatto in chat (niente pagina). Claude raccoglie logo, link della landing o di Instagram, un
brand già fatto (anche con Claude) o le risposte alle domande, poi usa questo strumento per salvarlo e mostrarlo.

    PY brand.py colori FILE [FILE...]   i colori vivi più presenti in un logo o in uno screenshot (dal più usato)
    PY brand.py font                    i font dello studio, per scegliere il più simile a quello del brand
    PY brand.py salva DATI.json         salva il brand (vedi sotto) e stampa BRAND SALVATO
    PY brand.py prova                   fa DATI/brand-prova.jpg: un fotogramma con colori, font, sottotitolo,
                                        bottone e scheda Segui del brand (senza logo), da far approvare al cliente

DATI.json (tutto facoltativo tranne "colore"; quello che manca resta com'era):
  {"colore": "#RRGGBB" (l'unico che accende titoli, parole in evidenza, effetti), "nome": nome Instagram,
   "sotto": riga sotto il nome, "parole": [nomi che il computer scrive male],
   "logo": percorso di un'immagine, "foto": percorso della foto profilo,
   "font_titoli": chiave di `font`, "font_testo": chiave di `font` (vanno nei titoli e nei sottotitoli di ogni stile)}
Scrive DATI/profilo.json (lo leggono già tutti gli strumenti) e i font in DATI/scelte.json ("titoli"/"sott" "font").
La scheda scritta del brand (chi è, tono, frasi sì e no, colori, cosa evitare) la scrive Claude in DATI/brand.md.
"""
import json
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, SCELTE, STUDIO, leggi, scrivi  # noqa: E402
import ritocchi  # noqa: E402

PROFILO = os.path.join(DATI, "profilo.json")
SCHEDA = os.path.join(DATI, "brand.md")
PROVA = os.path.join(DATI, "brand-prova.jpg")


def _leggi(p):
    try:
        return leggi(p)
    except (OSError, ValueError):
        return {}


def colori(file):
    """I colori vivi più presenti (niente bianco, nero, grigi, trasparente), raggruppati se quasi uguali."""
    from PIL import Image
    import colorsys
    im = Image.open(file).convert("RGBA")
    im.thumbnail((200, 200))
    conta = {}
    px = im.tobytes()
    for i in range(0, len(px), 4):
        r, g, b, a = px[i], px[i + 1], px[i + 2], px[i + 3]
        if a < 128:
            continue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if s < 0.25 or l < 0.12 or l > 0.92:
            continue
        k = (r // 24, g // 24, b // 24)
        c = conta.setdefault(k, [0, 0, 0, 0, 0])
        c[0] += s * min(l, 1 - l) * 2   # i colori accesi contano più di quelli scuri o slavati
        c[1] += r; c[2] += g; c[3] += b; c[4] += 1
    tot = sum(c[0] for c in conta.values()) or 1
    out = []
    for peso, r, g, b, n in sorted(conta.values(), reverse=True):
        rgb = (r // n, g // n, b // n)
        if any(sum(abs(x - y) for x, y in zip(rgb, o)) < 60 for o, _ in out):
            continue
        out.append((rgb, peso / tot))
        if len(out) == 5:
            break
    return [("#%02X%02X%02X" % rgb, quota) for rgb, quota in out]


def _copia(src, nome):
    if not src or not os.path.isfile(os.path.expanduser(src)):
        return None
    src = os.path.expanduser(src)
    est = os.path.splitext(src)[1].lower() if os.path.splitext(src)[1].lower() in (".png", ".jpg", ".jpeg") else ".png"
    dest = os.path.join(DATI, nome + (".jpg" if est == ".jpeg" else est))
    if os.path.abspath(src) == os.path.abspath(dest):
        return os.path.basename(dest)
    if os.path.exists(dest):
        os.replace(dest, dest[:-4] + "-prima" + dest[-4:])
    if est in (".png", ".jpg"):
        shutil.copyfile(src, dest)
    else:
        from PIL import Image
        Image.open(src).save(dest)
    return os.path.basename(dest)


def salva(d):
    acc = str(d.get("colore") or "").strip().upper()
    if not re.fullmatch(r"#[0-9A-F]{6}", acc):
        sys.exit('Manca "colore" (#RRGGBB).')
    os.makedirs(DATI, exist_ok=True)
    pr = _leggi(PROFILO)
    pr["colore"] = acc
    if "nome" in d:
        pr["nome"] = re.sub(r"[^A-Za-z0-9._]", "", str(d["nome"]).lstrip("@"))[:40]
    if "sotto" in d:
        pr["sotto"] = str(d["sotto"]).strip()[:50]
    if "parole" in d:
        pr["parole"] = [x.strip()[:40] for x in d["parole"] if str(x).strip()][:30]
    for chiave, nome in (("logo", "logo"), ("foto", "profilo")):
        f = _copia(d.get(chiave), nome)
        if f:
            pr[chiave] = f
    scrivi(PROFILO, pr)
    sc = _leggi(SCELTE)
    for chiave, dove in (("font_titoli", "titoli"), ("font_testo", "sott")):
        if d.get(chiave) in ritocchi.FONT:
            sc[dove] = dict(sc.get(dove) or {}, font=d[chiave])
    if any(d.get(k) in ritocchi.FONT for k in ("font_titoli", "font_testo")):
        scrivi(SCELTE, sc)
    print(f"BRAND SALVATO colore={acc} nome={pr.get('nome') or '-'} "
          f"titoli={(sc.get('titoli') or {}).get('font') or 'dello stile'} testo={(sc.get('sott') or {}).get('font') or 'dello stile'} "
          f"logo={'si' if pr.get('logo') else 'no'} foto={'si' if pr.get('foto') else 'no'} "
          f"scheda={'si' if os.path.exists(SCHEDA) else 'MANCA (scrivila in DATI/brand.md)'}", flush=True)


def prova():
    """Un fotogramma 1080x1920 con il brand: titolo, sottotitolo con la parola in evidenza, scheda Segui, bottone."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
    pr, sc = _leggi(PROFILO), _leggi(SCELTE)
    acc = pr.get("colore") or "#FF6B00"
    W, H = 1080, 1920

    def font(k, dim, ripiego):
        k = k if k in ritocchi.FONT else ripiego
        f = ImageFont.truetype(ritocchi.file_font(k), dim)
        peso = ritocchi.FONT[k][3]
        if ritocchi.FONT[k][4]:
            try:
                f.set_variation_by_axes([peso])
            except Exception:  # noqa: BLE001
                pass
        return f

    ft = lambda dim: font((sc.get("titoli") or {}).get("font"), dim, "archivo-black")
    fs = lambda dim: font((sc.get("sott") or {}).get("font"), dim, "jakarta")
    sfondo = next((p for p in (os.path.join(DATI, "telefono.jpg"), os.path.join(STUDIO, "pagina", "telefono.jpg")) if os.path.exists(p)), None)
    im = ImageOps.fit(Image.open(sfondo).convert("RGB"), (W, H)) if sfondo else Image.new("RGB", (W, H), "#2A2420")
    ombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ombra)

    def centrato(dr, y, testo, f, colore):
        w = dr.textlength(testo, font=f)
        dr.text(((W - w) / 2, y), testo, font=f, fill=colore)

    # titolo in alto (zona sicura: sotto y 240), la seconda riga nel colore del brand
    centrato(d, 214, "ECCO IL TUO", ft(76), (0, 0, 0, 200))
    centrato(d, 296, "TITOLO", ft(124), (0, 0, 0, 200))
    im = Image.alpha_composite(im.convert("RGBA"), ombra.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    centrato(d, 210, "ECCO IL TUO", ft(76), "white")
    centrato(d, 292, "TITOLO", ft(124), acc)
    # sottotitolo con una parola in evidenza
    f = fs(76)
    parti = [("così si vedono ", "white"), ("le parole", acc)]
    larg = sum(d.textlength(t, font=f) for t, _ in parti)
    x, y = (W - larg) / 2, 1330
    for t, c in parti:
        d.text((x + 3, y + 4), t, font=f, fill=(0, 0, 0, 170))
        d.text((x, y), t, font=f, fill=c)
        x += d.textlength(t, font=f)
    # scheda Segui
    nome = "@" + (pr.get("nome") or "il_tuo_nome")
    sotto = pr.get("sotto") or ""
    d.rounded_rectangle((150, 1480, 930, 1600), 30, fill=(255, 255, 255, 240))
    foto = os.path.join(DATI, pr.get("foto") or "-")
    if os.path.isfile(foto):
        fi = ImageOps.fit(Image.open(foto).convert("RGB"), (90, 90))
        m = Image.new("L", (90, 90), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 90, 90), fill=255)
        im.paste(fi, (170, 1495), m)
    else:
        d.ellipse((170, 1495, 260, 1585), fill=acc)
    d.text((280, 1500 if sotto else 1518), nome[:22], font=fs(38), fill="#111111")
    if sotto:
        d.text((280, 1548), sotto[:30], font=fs(28), fill="#666666")
    d.rounded_rectangle((760, 1510, 910, 1570), 14, fill="#0095F6")
    centro = d.textlength("Segui", font=fs(30))
    d.text((835 - centro / 2, 1520), "Segui", font=fs(30), fill="white")
    # bottone del finale (la parola vera cambia a ogni video: qui un esempio)
    t = "COMMENTA INFO"
    f = ft(52)
    w = d.textlength(t, font=f)
    d.rounded_rectangle(((W - w) / 2 - 40, 1630, (W + w) / 2 + 40, 1720), 45, fill=(19, 13, 9, 210), outline=acc, width=5)
    centrato(d, 1645, t, f, "white")
    im.convert("RGB").save(PROVA, quality=90)
    print(f"PROVA {PROVA}", flush=True)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cosa = sys.argv[1]
    if cosa == "colori":
        for f in sys.argv[2:]:
            print(f"COLORI {os.path.basename(f)}: " + "  ".join(f"{h} ({q:.0%})" for h, q in colori(f)))
    elif cosa == "font":
        for k, (nome, _, gruppo, _, _) in ritocchi.FONT.items():
            print(f"{k:14} {nome}  ({gruppo})")
    elif cosa == "salva" and len(sys.argv) > 2:
        salva(leggi(sys.argv[2]))
    elif cosa == "prova":
        prova()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
