"""Prende un reel di esempio (da copiare come stile) da un link o da un file, e lo mette in DATI/esempi/<nome>/reel.mp4.

Uso:  PY strumenti/prendi_esempio.py "<link o file>" ["<altro link>" ...] [--nome marco] [--browser chrome]

Link: Instagram, TikTok, YouTube, Pinterest, X e quasi tutti gli altri siti di video. La prima volta installa il
programma che scarica (yt-dlp, pochi MB) dentro il Python dello studio.
Per ogni esempio stampa una riga:
  PRONTO <file>          scaricato, ora: PY strumenti/studia.py <file>
  SERVE LOGIN <link>     il sito lo mostra solo a chi ha fatto l'accesso. Chiedi all'utente il permesso di usare
                         l'accesso del suo browser ("Posso usare l'accesso del tuo browser? Non salvo niente.");
                         solo se dice sì, rilancia con --browser chrome (o safari, firefox, edge). Se dice no,
                         il video lo scarica lui e te lo passa come file.
  NON RIUSCITO <link>    chiedi un altro link o il file.
"""
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, codec_video  # noqa: E402

ESEMPI = os.path.join(DATI, "esempi")


def scaricatore():
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("Installo il programma che scarica i video (una volta sola)...", flush=True)
        # il Python dello studio è fatto con uv (niente pip dentro): si usa uv, se no pip
        uv = next((u for u in (shutil.which("uv"), os.path.expanduser("~/.local/bin/uv"), "/opt/homebrew/bin/uv",
                               os.path.expanduser("~/.cargo/bin/uv"), os.path.expanduser("~/.local/bin/uv.exe"))
                   if u and os.path.exists(u)), None)
        cmd = [uv, "pip", "install", "-q", "--python", sys.executable, "yt-dlp"] if uv else \
              [sys.executable, "-m", "pip", "install", "-q", "yt-dlp"]
        subprocess.run(cmd, check=True)
    import yt_dlp
    return yt_dlp


def nome_libero(base):
    os.makedirs(ESEMPI, exist_ok=True)
    if base and not os.path.exists(os.path.join(ESEMPI, base)):
        return base
    n = 1
    while os.path.exists(os.path.join(ESEMPI, f"{base or 'esempio'}-{n}")):
        n += 1
    return f"{base or 'esempio'}-{n}"


def in_mp4(src, dest):
    """Ogni esempio diventa un mp4 normale (H.264, audio AAC), così gli altri strumenti lo leggono sempre."""
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, *codec_video(), "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", dest], check=True)


def scarica(link, cart, browser=None):
    yt_dlp = scaricatore()
    opz = {"outtmpl": os.path.join(cart, "originale.%(ext)s"), "quiet": True, "no_warnings": True,
           "format": "bv*+ba/b", "merge_output_format": "mp4", "noplaylist": True}
    if browser:
        opz["cookiesfrombrowser"] = (browser,)
    try:
        with yt_dlp.YoutubeDL(opz) as y:
            y.download([link])
    except Exception as e:  # noqa: BLE001
        testo = str(e).lower()
        if any(k in testo for k in ("login", "log in", "cookies", "private", "sign in", "rate-limit")):
            return "SERVE LOGIN"
        return "NON RIUSCITO"
    fatti = [f for f in os.listdir(cart) if f.startswith("originale.")]
    return os.path.join(cart, fatti[0]) if fatti else "NON RIUSCITO"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None  # noqa: E731
    browser, base = opz("--browser"), opz("--nome")
    args = [a for a in args if a not in (browser, base)]
    if not args:
        sys.exit(__doc__)
    for k, cosa in enumerate(args):
        nome = nome_libero(base if len(args) == 1 else (f"{base}-{k + 1}" if base else None))
        cart = os.path.join(ESEMPI, nome)
        os.makedirs(cart, exist_ok=True)
        dest = os.path.join(cart, "reel.mp4")
        if os.path.exists(os.path.expanduser(cosa)):
            in_mp4(os.path.expanduser(cosa), dest)
            print(f"PRONTO {dest}", flush=True)
            continue
        if not re.match(r"https?://", cosa):
            shutil.rmtree(cart, ignore_errors=True)
            print(f"NON RIUSCITO {cosa} (non è un link e non trovo il file)", flush=True)
            continue
        esito = scarica(cosa, cart, browser)
        if esito in ("SERVE LOGIN", "NON RIUSCITO"):
            shutil.rmtree(cart, ignore_errors=True)
            print(f"{esito} {cosa}", flush=True)
            continue
        in_mp4(esito, dest)
        os.remove(esito)
        with open(os.path.join(cart, "fonte.txt"), "w", encoding="utf-8") as f:
            f.write(cosa + "\n")
        print(f"PRONTO {dest}", flush=True)


if __name__ == "__main__":
    main()
