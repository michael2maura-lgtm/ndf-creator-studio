"""Il secondo controllo, prima di consegnare: prepara per un secondo Claude (il «critico», un subagente con occhi nuovi)
tutto quello che serve a giudicare il reel FINITO senza sentire l'audio, e gli scrive cosa controllare.

    PY critico.py NOME [--versione v2]

Scrive lavori/NOME/controllo/critico/:
  LEGGIMI.md      le istruzioni per il critico: cosa guardare e come rispondere (solo problemi veri, con il secondo)
  gancio.jpg      i primi 5 secondi, fotogramma per fotogramma, con le zone di Instagram segnate
  foglio-NN.jpg   tutto il video, un fotogramma ogni 1,5 secondi, con le zone segnate
  fine.jpg        gli ultimi 4 secondi
  testi.txt       le parole dette (con i secondi del video finito) e tutte le scritte del piano, per i refusi
  copertina.jpg e didascalia.txt, se ci sono
Stampa: CRITICO PRONTO <percorso di LEGGIMI.md>
I secondi sono quelli del video FINITO (accelerato): nel piano si correggono a t x velocita (in LEGGIMI.md).
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, STUDIO, cartella_lavoro, durata, leggi  # noqa: E402
import revisione  # noqa: E402

W, H = 1080, 1920
PICCOLO = (270, 480)


def fotogrammi(video, tempi):
    from PIL import Image
    out = []
    for t in tempi:
        r = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf",
                            f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
        if len(r.stdout) == W * H * 3:
            out.append((t, Image.frombytes("RGB", (W, H), r.stdout)))
    return out


def con_zone(im):
    """Le zone di Instagram (regole/instagram.md) segnate a filo, per vedere se una scritta ci finisce sotto."""
    from PIL import ImageDraw
    im = im.copy()
    d = ImageDraw.Draw(im)
    for y in (220, 1470):
        d.line([0, y, W, y], fill=(255, 40, 40), width=5)
    d.line([980, 1155, 980, H], fill=(255, 40, 40), width=5)
    return im


def foglio(quadri, colonne, percorso):
    from PIL import Image, ImageDraw
    if not quadri:
        return
    righe = (len(quadri) + colonne - 1) // colonne
    w, h = PICCOLO
    out = Image.new("RGB", (colonne * w, righe * (h + 26)), (18, 18, 20))
    d = ImageDraw.Draw(out)
    for i, (t, im) in enumerate(quadri):
        x, y = (i % colonne) * w, (i // colonne) * (h + 26)
        out.paste(con_zone(im).resize(PICCOLO), (x, y + 26))
        d.text((x + 6, y + 6), f"{t:.1f} s", fill=(255, 210, 80))
    out.save(percorso, quality=85)


def scritte(piano):
    """Tutte le scritte che finiscono a schermo (titoli, targhe, righe, voci...), per controllare i refusi."""
    trovate = []

    def giro(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, str) and k in ("testo", "sopra", "targa", "sotto", "riga", "riga1", "riga2", "titolo",
                                                "etichetta", "bottone", "parola", "frase", "nome", "risposta", "ok",
                                                "vuoto", "chip", "finale_testo", "finale_sopra", "finale_bottone"):
                    trovate.append(v)
                else:
                    giro(v)
        elif isinstance(x, list):
            for v in x:
                if isinstance(v, str) and len(v) > 1 and not re.fullmatch(r"[\w./#-]+\.(mp4|jpg|png|mp3)", v):
                    trovate.append(v)
                else:
                    giro(v)
    giro(piano)
    return [s for s in dict.fromkeys(trovate) if re.search(r"[A-Za-zÀ-ú]", s)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    nome = args[0]
    cart = cartella_lavoro(nome)
    vv = revisione.versioni(cart, nome)
    if not vv:
        sys.exit("Non c'è ancora un video finito: prima rendi.py.")
    chiesta = sys.argv[sys.argv.index("--versione") + 1] if "--versione" in sys.argv else None
    versione, video = next(((v, p) for v, p in vv if v == chiesta), vv[-1])
    vel = revisione.velocita(cart)
    D = durata(video)
    out = os.path.join(cart, "controllo", "critico")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    foglio(fotogrammi(video, [0.2, 0.7, 1.2, 1.7, 2.3, 3.0, 3.8, 4.6]), 4, os.path.join(out, "gancio.jpg"))
    tempi = [round(5 + i * 1.5, 2) for i in range(int(max(0, D - 5) / 1.5) + 1) if 5 + i * 1.5 < D - 0.2]
    for k in range(0, len(tempi), 12):
        foglio(fotogrammi(video, tempi[k:k + 12]), 4, os.path.join(out, f"foglio-{k // 12 + 1:02d}.jpg"))
    foglio(fotogrammi(video, [max(0, D - x) for x in (4, 3, 2, 1.2, 0.6, 0.15)]), 3, os.path.join(out, "fine.jpg"))

    righe = [f"Video {nome}-{versione}: {D:.1f} secondi (accelerato x{vel:g} rispetto al montaggio).", "",
             "PAROLE DETTE (secondo del video finito: parola):"]
    try:
        parole = leggi(os.path.join(cart, "parole.json"))
        frase, inizio = [], None
        for w in parole:
            if inizio is None:
                inizio = w["da"] / vel
            frase.append(w["testo"])
            if re.search(r"[.!?]$", w["testo"]) or len(frase) >= 14:
                righe.append(f"  {inizio:6.1f}  " + " ".join(frase))
                frase, inizio = [], None
        if frase:
            righe.append(f"  {inizio:6.1f}  " + " ".join(frase))
    except (OSError, ValueError):
        righe.append("  (parole.json non c'è)")
    try:
        piano = leggi(os.path.join(cart, "piano.json"))
    except (OSError, ValueError):
        piano = {}
    righe += ["", "SCRITTE A SCHERMO (dal piano, controlla i refusi):"] + [f"  - {s}" for s in scritte(piano)]
    righe += ["", f"Stile: {piano.get('stile', '?')} · musica: {piano.get('musica', 'dello stile')}"]
    with open(os.path.join(out, "testi.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    extra = []
    for sorgente, dest in ((os.path.join(cart, "finale", f"{nome}-copertina.jpg"), "copertina.jpg"),
                           (os.path.join(cart, "finale", f"{nome}-didascalia.txt"), "didascalia.txt")):
        if os.path.exists(sorgente):
            shutil.copy2(sorgente, os.path.join(out, dest))
            extra.append(dest)

    fogli = sorted(f for f in os.listdir(out) if f.startswith("foglio-"))
    istruzioni = open(os.path.join(STUDIO, "regole", "critico.md"), encoding="utf-8").read()
    istruzioni = istruzioni.replace("{CARTELLA}", out).replace("{FOGLI}", ", ".join(fogli)) \
        .replace("{EXTRA}", ", ".join(extra) or "nessuno").replace("{VEL}", f"{vel:g}")
    with open(os.path.join(out, "LEGGIMI.md"), "w", encoding="utf-8") as f:
        f.write(istruzioni)
    print(f"CRITICO PRONTO {os.path.join(out, 'LEGGIMI.md')}")


if __name__ == "__main__":
    main()
