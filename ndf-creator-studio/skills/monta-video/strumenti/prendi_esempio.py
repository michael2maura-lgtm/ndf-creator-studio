"""Prende un reel di esempio (da copiare come stile) da un link o da un file, e lo mette in DATI/esempi/<nome>/reel.mp4.

Uso:  PY strumenti/prendi_esempio.py "<link o file>" ["<altro link>" ...] [--nome marco] [--browser chrome]

Anche una foto o uno screenshot (file .jpg .png .webp, o l'indirizzo diretto di una foto): diventa foto.png.
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
from comune import CASA, DATI, FFMPEG, codec_video  # noqa: E402

ESEMPI = os.path.join(DATI, "esempi")


def installa(aggiorna=False):
    """Installa (o aggiorna all'ultima versione) il programma che scarica. True se è andato."""
    su = ["-U"] if aggiorna else []
    cmd = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", *su, "yt-dlp"]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def da_aggiornare(giorni=21):
    """Instagram e TikTok cambiano spesso: un programma di qualche settimana fa smette di scaricare.
    Si guarda la data della versione senza aprirlo, e si prova ad aggiornare al massimo una volta al giorno."""
    import datetime
    import importlib.metadata
    segno = os.path.join(CASA, "scaricatore-controllato.txt")
    oggi = datetime.date.today().isoformat()
    try:
        if open(segno, encoding="utf-8").read().strip() == oggi:
            return False
    except OSError:
        pass
    try:
        a, m, g = (int(x) for x in importlib.metadata.version("yt-dlp").split(".")[:3])
        vecchio = (datetime.date.today() - datetime.date(a, m, g)).days > giorni
    except Exception:  # noqa: BLE001
        return False
    if vecchio:
        os.makedirs(os.path.dirname(segno), exist_ok=True)
        with open(segno, "w", encoding="utf-8") as f:
            f.write(oggi)
    return vecchio


def scaricatore():
    try:
        import importlib.metadata
        importlib.metadata.version("yt-dlp")
    except Exception:  # noqa: BLE001
        print("Installo il programma che scarica i video (una volta sola)...", flush=True)
        installa()
    else:
        if da_aggiornare():
            print("Controllo che il programma che scarica i video sia aggiornato...", flush=True)
            installa(aggiorna=True)
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
           "format": "bv*+ba/b", "merge_output_format": "mp4", "noplaylist": True, "noprogress": True}
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


FOTO = (".jpg", ".jpeg", ".png", ".webp", ".heic")


def in_foto(src, dest):
    """Una foto o uno screenshot (un pin, una grafica che piace) diventa foto.png: lo studia studia.py."""
    from PIL import Image
    Image.open(src).convert("RGB").save(dest)


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
        if os.path.exists(os.path.expanduser(cosa)) and os.path.splitext(cosa)[1].lower() in FOTO:
            foto = os.path.join(cart, "foto.png")
            in_foto(os.path.expanduser(cosa), foto)
            print(f"PRONTO {foto}", flush=True)
            continue
        if re.match(r"https?://\S+\.(jpe?g|png|webp)(\?|$)", cosa, re.I):   # l'indirizzo diretto di una foto
            import urllib.request
            tmp = os.path.join(cart, "scaricata" + os.path.splitext(cosa.split("?")[0])[1])
            try:
                urllib.request.urlretrieve(cosa, tmp)
                in_foto(tmp, os.path.join(cart, "foto.png"))
                os.remove(tmp)
                print(f"PRONTO {os.path.join(cart, 'foto.png')}", flush=True)
            except Exception:  # noqa: BLE001
                shutil.rmtree(cart, ignore_errors=True)
                print(f"NON RIUSCITO {cosa}", flush=True)
            continue
        if os.path.exists(os.path.expanduser(cosa)):
            in_mp4(os.path.expanduser(cosa), dest)
            print(f"PRONTO {dest}", flush=True)
            continue
        if not re.match(r"https?://", cosa):
            shutil.rmtree(cart, ignore_errors=True)
            print(f"NON RIUSCITO {cosa} (non è un link e non trovo il file)", flush=True)
            continue
        esito = scarica(cosa, cart, browser)
        if esito == "NON RIUSCITO" and "--aggiornato" not in sys.argv and installa(aggiorna=True):
            # spesso il sito è cambiato: con il programma aggiornato si riprova una volta, da capo
            shutil.rmtree(cart, ignore_errors=True)
            print("Il sito è cambiato: ho aggiornato il programma che scarica, riprovo...", flush=True)
            subprocess.run([sys.executable, os.path.abspath(__file__), cosa, "--nome", nome, "--aggiornato"]
                           + (["--browser", browser] if browser else []))
            continue
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
