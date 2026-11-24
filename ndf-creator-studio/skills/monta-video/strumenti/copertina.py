"""Copertina del reel: un fotogramma nitido, senza mani davanti alla faccia, con un titolo grosso nel font e nel colore
dello stile. Il titolo sta nella parte che si vede anche nella griglia del profilo (il centro 3:4, da y 240 a 1680).

    PY copertina.py NOME --titolo "IL PROBLEMA *NON SEI TU*" [--sotto "riga piccola"] [--t 12.5]

--titolo  2-6 parole, quelle del gancio o della promessa del video; le parole tra *asterischi* vanno sulla fascia
          del colore d'accento (una o due, non di più).
--sotto   facoltativa: una riga piccola sotto il titolo.
--t       facoltativo: il secondo da usare (del video tagliato); se no lo sceglie lo studio: faccia trovata, mani giù,
          il fotogramma più nitido.
Scrive finale/NOME-copertina.jpg (1080x1920) e controllo/copertina.jpg (la copertina intera e com'è nella griglia):
guardalo: occhi aperti, espressione buona, titolo leggibile e lontano dalla faccia. Se gli occhi sono chiusi o
l'espressione è brutta, rilancia con un altro --t.
"""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import (DATI, FFMPEG, SCELTE, STUDIO, cartella_lavoro, cartella_stile, con_le_scelte, durata,  # noqa: E402
                    girato, leggi, mani_sulla_faccia)

W, H = 1080, 1920
GRIGLIA = (240, 1680)   # la parte che si vede nella griglia del profilo (3:4 al centro)


def fotogramma(video, t):
    import numpy as np
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf",
                        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(H, W, 3)


def nitidezza(img, c):
    """Quanto è nitida la faccia (varianza del laplaciano): più alto = meno mosso."""
    import numpy as np
    from scipy import ndimage
    x0, y0 = max(0, c["x"]), max(0, c["y"])
    g = img[y0:y0 + c["h"], x0:x0 + c["l"]].mean(axis=2)
    return float(ndimage.laplace(g).var()) if g.size else 0.0


def scegli_momento(cart, faccia, D, t=None):
    camp = [c for c in faccia.get("campioni", []) if "y" in c and not mani_sulla_faccia(c)]
    if t is not None:
        vicini = [c for c in camp if abs(c["t"] - t) <= 1.0]
        return min(vicini, key=lambda c: abs(c["t"] - t)) if vicini else {"t": t}
    dentro = [c for c in camp if 0.1 * D <= c["t"] <= 0.9 * D] or camp
    if not dentro:
        return {"t": D * 0.3}
    passo = max(1, len(dentro) // 14)   # al massimo 14 candidati
    video = girato(cart)
    return max(dentro[::passo], key=lambda c: nitidezza(fotogramma(video, c["t"]), c))


def font_dello_stile(cart):
    """Il font dei titoli e il colore d'accento dello stile del lavoro (con le scelte della pagina e il brand)."""
    try:
        piano = leggi(os.path.join(cart, "piano.json"))
    except (OSError, ValueError):
        piano = {}
    try:
        scelto = leggi(SCELTE).get("stile")
    except (OSError, ValueError):
        scelto = None
    nome = piano.get("stile") or scelto or "pulito"
    cs = cartella_stile(nome)
    stile = con_le_scelte(nome, leggi(os.path.join(cs, "stile.json")))
    acc = (piano.get("colori") or {}).get("accento") or stile.get("colori", {}).get("accento") or "#E86530"
    f = (stile.get("font") or {}).get("titoli") or {}
    percorso = os.path.join(cs, f["file"]) if f.get("file") else ""
    if not os.path.exists(percorso):
        percorso = os.path.join(STUDIO, "font", "Anton-Regular.ttf")
    return percorso, acc


def carattere(percorso, misura):
    from PIL import ImageFont
    f = ImageFont.truetype(percorso, misura)
    try:   # font variabili (Plus Jakarta, Archivo...): il più grassetto
        assi = f.get_variation_axes()
        f.set_variation_by_axes([a.get("maximum", 800) if "eight" in str(a.get("name", "")) else a.get("default", 0)
                                 for a in assi])
    except Exception:
        pass
    return f


def righe_del_titolo(parole, font, largo):
    """Va a capo dove serve: parole = [(testo, evidenziata)]."""
    righe, riga = [], []
    for p in parole:
        prova = riga + [p]
        if riga and font.getlength(" ".join(x[0] for x in prova)) > largo:
            righe.append(riga)
            riga = [p]
        else:
            riga = prova
    if riga:
        righe.append(riga)
    return righe


def main():
    import numpy as np
    from PIL import Image, ImageDraw
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d  # noqa: E731
    if not args or not opz("--titolo"):
        sys.exit(__doc__)
    nome = args[0]
    cart = cartella_lavoro(nome)
    faccia = leggi(os.path.join(cart, "faccia.json"))
    D = durata(os.path.join(cart, "tagliato.mp4"))
    t = float(opz("--t")) if opz("--t") else None
    c = scegli_momento(cart, faccia, D, t)
    img = Image.fromarray(fotogramma(girato(cart), c["t"])).convert("RGBA")

    percorso, acc = font_dello_stile(cart)
    # il titolo: sul petto, sotto il mento, sempre dentro la parte della griglia
    mento = c["y"] + c["h"] if "y" in c else faccia.get("mento", 1000)
    alto_min = max(mento + 70, 1020)
    pezzi = [(p.strip("*"), p.startswith("*") or p.endswith("*")) for p in
             re.findall(r"\*[^*]+\*|\S+", opz("--titolo").upper())]
    pezzi = [(w, ev) for frase, ev in pezzi for w in frase.split()] if pezzi else []
    uniti = []
    for w, ev in pezzi:   # "?", "!", "," da soli si attaccano alla parola prima
        if uniti and re.fullmatch(r"[?!.,:;…]+", w):
            uniti[-1] = (uniti[-1][0] + w, uniti[-1][1])
        else:
            uniti.append((w, ev))
    pezzi = uniti
    sotto = opz("--sotto")
    for misura in range(128, 60, -6):   # la misura più grande che sta in 3 righe e dentro la griglia
        font = carattere(percorso, misura)
        righe = righe_del_titolo(pezzi, font, 960)
        largo = 960
        while largo > 300 and len(righe_del_titolo(pezzi, font, largo - 20)) == len(righe):
            largo -= 20   # righe di lunghezza simile: niente parola sola sull'ultima riga
        righe = righe_del_titolo(pezzi, font, largo)
        alt_riga = int(misura * 1.12)
        totale = len(righe) * alt_riga + (int(misura * 0.55) if sotto else 0)
        orfana = len(righe) > 1 and len(righe[-1]) == 1 and len(pezzi) >= 4 and misura > 84   # una parola sola in fondo
        if len(righe) <= 3 and alto_min + totale <= GRIGLIA[1] - 40 and not orfana:
            break
    y0 = min(alto_min, GRIGLIA[1] - 40 - totale)   # sotto il mento; se non ci sta, sale quanto basta

    # una sfumatura scura sotto il titolo, perché si legga su qualsiasi maglia o sfondo
    sf = np.zeros((H, W, 4), np.uint8)
    inizio = max(0, y0 - 260)
    for y in range(inizio, H):
        sf[y, :, 3] = int(min(1, (y - inizio) / 260) * 170)
    img = Image.alpha_composite(img, Image.fromarray(sf, "RGBA"))
    d = ImageDraw.Draw(img)
    y = y0
    for riga in righe:
        spazio = font.getlength(" ")
        pad = 16   # quanto la fascia sborda attorno alle parole: le parole vicine si scostano di altrettanto
        xs, x = [], 0.0
        for k, (w, ev) in enumerate(riga):
            if k and ev != riga[k - 1][1]:
                x += pad
            xs.append(x)
            x += font.getlength(w) + spazio
        largo_riga = x - spazio
        xs = [v + (W - largo_riga) / 2 for v in xs]
        # la fascia del colore d'accento dietro le parole che contano (una fascia sola per le parole vicine)
        i = 0
        while i < len(riga):
            if riga[i][1]:
                j = i
                while j + 1 < len(riga) and riga[j + 1][1]:
                    j += 1
                d.rounded_rectangle([xs[i] - pad, y + misura * 0.04, xs[j] + font.getlength(riga[j][0]) + pad,
                                     y + misura * 1.1], radius=10, fill=acc)
                i = j + 1
            else:
                i += 1
        for (w, ev), x in zip(riga, xs):
            if not ev:
                d.text((x + 3, y + 5), w, font=font, fill=(0, 0, 0, 140))
            d.text((x, y), w, font=font, fill="white")
        y += alt_riga
    if sotto:
        fs = carattere(os.path.join(STUDIO, "font", "PlusJakartaSans.ttf"), int(misura * 0.42))
        d.text(((W - fs.getlength(sotto)) / 2, y + 10), sotto, font=fs, fill=(244, 237, 224))

    finale = os.path.join(cart, "finale")
    os.makedirs(finale, exist_ok=True)
    uscita = os.path.join(finale, f"{nome}-copertina.jpg")
    img.convert("RGB").save(uscita, quality=92)
    # controllo: la copertina intera e com'è nella griglia del profilo
    os.makedirs(os.path.join(cart, "controllo"), exist_ok=True)
    intera = img.convert("RGB").resize((360, 640))
    griglia = img.convert("RGB").crop((0, GRIGLIA[0], W, GRIGLIA[1])).resize((360, 480))
    foglio = Image.new("RGB", (740, 640), (20, 20, 22))
    foglio.paste(intera, (0, 0))
    foglio.paste(griglia, (380, 80))
    foglio.save(os.path.join(cart, "controllo", "copertina.jpg"), quality=85)
    print(f"COPERTINA {uscita} (secondo {c['t']:.1f} del video tagliato){'' if 'y' in c else ' · faccia non trovata'}")


if __name__ == "__main__":
    main()
