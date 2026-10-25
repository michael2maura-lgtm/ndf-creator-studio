"""Passo 3: controlla un video tagliato o finito. Si guardano i fotogrammi veri, non ci si fida del codice.

Uso:  ~/.studio-video/venv/bin/python strumenti/controlla_tagli.py <nome-lavoro> [video.mp4] [--telefono]

Scrive in lavori/<nome>/controllo/:
  tagli.jpg        per ogni taglio: l'ultimo fotogramma prima e il primo dopo, affiancati
  <video>-telefono.mp4  (con --telefono) una copia leggera 720p da mandare sul telefono
L'ultima riga è il livello dell'audio: picco e media.
"""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, cartella_lavoro, esegui, leggi  # noqa: E402

FPS = 30


def fotogramma(video, n, dest):
    t = max(n, 0) / FPS + 0.5 / FPS
    esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", video, "-frames:v", "1", "-vf", "scale=216:384", dest])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    cart = cartella_lavoro(args[0])
    video = args[1] if len(args) > 1 else os.path.join(cart, "tagliato.mp4")
    if not os.path.isabs(video):
        video = os.path.join(cart, video)
    segmenti = leggi(os.path.join(cart, "segmenti.json"))
    out = os.path.join(cart, "controllo")
    os.makedirs(out, exist_ok=True)

    from PIL import Image, ImageDraw
    coppie = []
    for s in segmenti[1:]:
        f = s["fotogramma"]
        a, b = os.path.join(out, "_a.jpg"), os.path.join(out, "_b.jpg")
        fotogramma(video, f - 1, a)
        fotogramma(video, f, b)
        coppie.append((s["id"], s["inizio"], Image.open(a).copy(), Image.open(b).copy()))
    if coppie:
        w, h = 216, 384
        foglio = Image.new("RGB", (len(coppie) * (2 * w + 20), h + 30), "white")
        d = ImageDraw.Draw(foglio)
        for i, (nome, t, ia, ib) in enumerate(coppie):
            x = i * (2 * w + 20)
            foglio.paste(ia, (x, 30))
            foglio.paste(ib, (x + w, 30))
            d.text((x + 4, 8), f"{t:.2f}s  prima | dopo  ({nome})", fill="black")
        foglio.save(os.path.join(out, "tagli.jpg"), quality=85)
        for f in ("_a.jpg", "_b.jpg"):
            os.remove(os.path.join(out, f))
        print(f"Tagli: {os.path.join(out, 'tagli.jpg')}")

    if "--telefono" in sys.argv:
        tel = os.path.join(out, os.path.splitext(os.path.basename(video))[0] + "-telefono.mp4")
        esegui([FFMPEG, "-v", "error", "-y", "-i", video, "-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "27",
                "-preset", "fast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", tel])
        print(f"Copia per il telefono: {tel}")

    err = subprocess.run([FFMPEG, "-i", video, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    picco = re.search(r"max_volume: (-?[\d.]+)", err)
    media = re.search(r"mean_volume: (-?[\d.]+)", err)
    print(f"Audio: picco {picco.group(1)} dB, media {media.group(1)} dB")


if __name__ == "__main__":
    main()
