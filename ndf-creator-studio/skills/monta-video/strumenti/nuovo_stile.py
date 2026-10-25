"""Crea lo stile di chi usa lo studio, dalle risposte dell'intervista, e ne fa un'anteprima.

Uso:  python3 strumenti/nuovo_stile.py <nome> --accento "#E86530" --luce "#FF8A4C" --testo "#F9F7F4" --scuro "#140E0A"
          --font-titoli "Plus Jakarta Sans" --font-corsivo "Instrument Serif" [--finale "COMMENTA INFO"]
          [--note "frasi dell'intervista da ricordare"]
      python3 strumenti/nuovo_stile.py <nome> --anteprima        (rifà solo l'immagine di prova)

Scrive DATI/stili/<nome>/: stile.json (i valori), stile.md (come si usa), font/, suoni/, anteprima.png.
I font si scaricano da Google Fonts (tutti con licenza libera, anche per uso commerciale): se un font non c'è,
si ferma e lo dice, mai un font sostitutivo di nascosto.
"""
import argparse
import json
import os
import shutil
import sys
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, STUDIO, trova  # noqa: E402

API = "https://api.github.com/repos/google/fonts/contents/ofl/"


def scarica_font(famiglia, dest, corsivo=False):
    """Il file del font da Google Fonts (cartella ofl/<nome>). Restituisce il nome del file salvato."""
    cart = famiglia.lower().replace(" ", "")
    try:
        with urllib.request.urlopen(API + urllib.parse.quote(cart), timeout=60) as r:
            files = [f for f in json.load(r) if f["name"].endswith(".ttf")]
    except Exception:
        sys.exit(f"Non trovo il font '{famiglia}' su Google Fonts: scegline un altro con l'utente.")
    def peso(f):
        n = f["name"]
        return (("Italic" in n) != corsivo, "[" not in n and "Regular" not in n and "Bold" not in n, n)
    scelto = sorted(files, key=peso)[0]
    os.makedirs(dest, exist_ok=True)
    urllib.request.urlretrieve(scelto["download_url"], os.path.join(dest, scelto["name"]))
    try:
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/google/fonts/main/ofl/{cart}/OFL.txt",
                                   os.path.join(dest, f"OFL-{cart}.txt"))
    except Exception:
        pass
    return scelto["name"]


def anteprima(cart):
    """Un fotogramma di prova: titolo grande con il corsivo, un sottotitolo, i colori dello stile."""
    from PIL import Image, ImageDraw, ImageFont
    s = json.load(open(os.path.join(cart, "stile.json"), encoding="utf-8"))
    c = s["colori"]
    im = Image.new("RGB", (1080, 1920), c["scuro"])
    d = ImageDraw.Draw(im)
    for y in range(1920):  # alone caldo al centro
        a = max(0, 1 - abs(y - 900) / 900) * 0.25
        d.line([(0, y), (1080, y)], fill=tuple(int(int(c["accento"][i:i + 2], 16) * a + int(c["scuro"][i:i + 2], 16) * (1 - a)) for i in (1, 3, 5)))
    def grassetto(size):
        f = ImageFont.truetype(os.path.join(cart, s["font"]["titoli"]["file"]), size)
        try:
            f.set_variation_by_axes([800])
        except Exception:
            pass
        return f
    ft, fs = grassetto(130), grassetto(76)
    fc = ImageFont.truetype(os.path.join(cart, s["font"]["corsivo"]["file"]), 76)
    d.text((540, 700), "il tuo stile", font=fc, fill=c["testo"], anchor="mm")
    d.text((540, 820), "IN UN REEL", font=ft, fill=c["accento"], anchor="mm")
    d.text((540, 920), "così appaiono i titoli", font=fc, fill=c["accento_luce"], anchor="mm")
    d.text((540, 1250), "SOTTOTITOLO", font=fs, fill=c["testo"], anchor="mm")
    d.text((540, 1400), s["finale"]["testo"], font=ft, fill=c["accento"], anchor="mm")
    im.save(os.path.join(cart, "anteprima.png"))
    return os.path.join(cart, "anteprima.png")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("nome")
    for k in ("accento", "luce", "testo", "scuro", "font-titoli", "font-corsivo", "finale", "note"):
        p.add_argument("--" + k)
    p.add_argument("--anteprima", action="store_true")
    a = p.parse_args()
    cart = os.path.join(DATI, "stili", a.nome)
    if a.anteprima:
        print(anteprima(cart))
        return
    os.makedirs(os.path.join(cart, "suoni"), exist_ok=True)
    ft = scarica_font(a.font_titoli or "Plus Jakarta Sans", os.path.join(cart, "font"))
    fc = scarica_font(a.font_corsivo or "Instrument Serif", os.path.join(cart, "font"), corsivo=True)
    # suoni di partenza: si cambiano dopo, ascoltando il catalogo
    for rel, nome in (("mixkit-whoosh/1493.mp3", "transizione.mp3"), ("mixkit/impatto.mp3", "colpo.mp3"),
                      ("mixkit/tastiera.mp3", "tastiera.mp3"), ("kit/musica-base.wav", "musica.wav")):
        shutil.copy2(trova(rel), os.path.join(cart, "suoni", nome))
    stile = {
        "nome": a.nome,
        "colori": {"accento": a.accento or "#E86530", "accento_luce": a.luce or a.accento or "#FF8A4C",
                   "testo": a.testo or "#F9F7F4", "scuro": a.scuro or "#140E0A"},
        "font": {"titoli": {"file": f"font/{ft}", "famiglia": a.font_titoli or "Plus Jakarta Sans", "peso": 800},
                 "corsivo": {"file": f"font/{fc}", "famiglia": a.font_corsivo or "Instrument Serif", "stile": "italic"}},
        "sottotitoli": {"parole_insieme": 1, "maiuscolo": True, "dimensione": 76, "colore": "testo"},
        "titoli": {"dimensione_grande": 118, "dimensione_corsivo": 66, "durata_minima": 1.2, "entrata": 0.35, "uscita": 0.2},
        "finale": {"testo": a.finale or "COMMENTA INFO", "secondi": 2.6, "colore": "accento"},
        "suoni": {"transizione": "suoni/transizione.mp3", "colpo": "suoni/colpo.mp3", "tastiera": "suoni/tastiera.mp3",
                  "musica": "suoni/musica.wav"},
    }
    json.dump(stile, open(os.path.join(cart, "stile.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    modello = open(os.path.join(STUDIO, "regole", "stile-modello.md"), encoding="utf-8").read()
    open(os.path.join(cart, "stile.md"), "w", encoding="utf-8").write(
        modello.replace("{NOME}", a.nome).replace("{NOTE}", a.note or "-"))
    print(anteprima(cart))


if __name__ == "__main__":
    main()
