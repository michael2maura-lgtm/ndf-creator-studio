"""Scarica una clip vera o una foto da Pexels (gratuite, anche per le pubblicità) per le scene "clip" e "immagine".
Un link pexels.com/photo/... scarica una foto in DATI/immagini/<nome>.jpg (1080x1920) per la scena "immagine".

Uso:  PY strumenti/clip.py <link o numero della clip Pexels> <nome>
      es.  PY strumenti/clip.py https://www.pexels.com/video/a-woman-opening-a-door-3195394/ porta-aperta

Come trovare il link: cerca sul web "pexels video <cosa> vertical" (in inglese funziona meglio) e prendi un
risultato tipo pexels.com/video/<descrizione>-<numero>/. La ricerca dentro il sito di Pexels non si può usare
(è bloccata ai programmi); lo scaricamento con il numero sì, senza chiavi né account.
Scrive DATI/clip/<nome>.mp4 (1080x1920, 30 fotogrammi al secondo, 5 secondi, senza audio) e DATI/clip/<nome>.jpg
(un fotogramma: guardalo prima di usarla, deve mostrare davvero quello che si dice).
"""
import os
import re
import sys
import tempfile
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, codec_video, esegui  # noqa: E402


def foto(numero, nome):
    """Foto verticale 1080x1920 (se è orizzontale si prende il centro), per la scena "immagine"."""
    dest = os.path.join(DATI, "immagini", nome + ".jpg")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    url = f"https://images.pexels.com/photos/{numero}/pexels-photo-{numero}.jpeg?auto=compress&cs=tinysrgb&w=2000"
    grezzo = os.path.join(tempfile.mkdtemp(), "foto.jpg")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(grezzo, "wb") as f:
        f.write(r.read())
    esegui([FFMPEG, "-v", "error", "-y", "-i", grezzo, "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-q:v", "3", dest])
    os.remove(grezzo)
    print(f"Foto pronta: {dest} · guardala prima di usarla")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    numero = re.findall(r"(\d{5,})", sys.argv[1])
    if not numero:
        sys.exit("Non trovo il numero della clip nel link.")
    nome = re.sub(r"[^\w-]", "-", sys.argv[2].lower())
    if "/photo/" in sys.argv[1]:
        foto(numero[-1], nome)
        return
    dest = os.path.join(DATI, "clip", nome + ".mp4")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    grezzo = os.path.join(tempfile.mkdtemp(), "grezzo.mp4")
    req = urllib.request.Request(f"https://www.pexels.com/download/video/{numero[-1]}/", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(grezzo, "wb") as f:
        f.write(r.read())
    # verticale 9:16 riempiendo lo schermo (se la clip è orizzontale si prende il centro), 5 secondi, senza audio
    esegui([FFMPEG, "-v", "error", "-y", "-i", grezzo, "-t", "5", "-an", "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
            *codec_video(), "-movflags", "+faststart", dest])
    esegui([FFMPEG, "-v", "error", "-y", "-ss", "1.5", "-i", dest, "-frames:v", "1", "-vf", "scale=360:-2",
            os.path.join(DATI, "clip", nome + ".jpg")])
    os.remove(grezzo)
    print(f"Clip pronta: {dest} · guarda {nome}.jpg prima di usarla")


if __name__ == "__main__":
    main()
