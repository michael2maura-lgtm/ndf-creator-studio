"""Confronto fianco a fianco: il reel di esempio sopra, il reel rifatto nel suo stile sotto, negli stessi punti.

Uso:  PY strumenti/confronta.py <esempio> <lavoro> [video]    esempio = file o nome in DATI/esempi; video = di
                                                               default l'ultima versione in lavori/<lavoro>/finale
      [--a 1.2,4.5,8.0]   secondi dell'esempio da confrontare (di default 8 punti dall'inizio alla fine);
                          per il reel rifatto si prende lo stesso punto in proporzione alla durata.

Scrive lavori/<lavoro>/controllo/confronto-esempio.jpg. Guardalo e scrivi all'utente una lista semplice:
cosa è uguale e cosa non si è potuto rifare. Prendi anche dei momenti A META' di un'entrata (dalle strisce di
movimento di studia.py) e confrontali: così si vede se il movimento è uguale, non solo la posa finale.
"""
import glob
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, cartella_lavoro, durata  # noqa: E402

W, H = 240, 426  # pari: il jpg non vuole misure dispari


def fotogramma(video, t, dest):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(t, 0):.2f}", "-i", video, "-frames:v", "1",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2", dest],
                   check=True)


def main():
    from PIL import Image, ImageDraw
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    punti = sys.argv[sys.argv.index("--a") + 1] if "--a" in sys.argv else None
    args = [a for a in args if a != punti]
    if len(args) < 2:
        sys.exit(__doc__)
    esempio = os.path.expanduser(args[0])
    if not os.path.exists(esempio):
        esempio = os.path.join(DATI, "esempi", args[0], "reel.mp4")
    cart = cartella_lavoro(args[1])
    video = args[2] if len(args) > 2 else sorted(glob.glob(os.path.join(cart, "finale", "*-v*.mp4")), key=os.path.getmtime)[-1]
    if not os.path.isabs(video):
        video = os.path.join(cart, video)
    De, Dr = durata(esempio), durata(video)
    tempi = [float(x) for x in punti.split(",")] if punti else [De * (k + 0.5) / 8 for k in range(8)]
    foglio = Image.new("RGB", (len(tempi) * W, 2 * (H + 24)), (20, 20, 20))
    d = ImageDraw.Draw(foglio)
    tmp = os.path.join(cart, "controllo", "_c.jpg")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    for k, t in enumerate(tempi):
        for riga, (v, tt, nome) in enumerate(((esempio, t, "esempio"), (video, t / De * Dr, "tuo"))):
            fotogramma(v, tt, tmp)
            foglio.paste(Image.open(tmp), (k * W, riga * (H + 24) + 24))
            d.text((k * W + 4, riga * (H + 24) + 6), f"{nome} {tt:.1f}s", fill=(255, 220, 90))
    os.remove(tmp)
    dest = os.path.join(cart, "controllo", "confronto-esempio.jpg")
    foglio.save(dest, quality=86)
    print(f"Confronto: {dest}")


if __name__ == "__main__":
    main()
