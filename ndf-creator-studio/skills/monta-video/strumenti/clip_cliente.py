"""Le due cartelle del cliente: le clip da montare e i video finiti (scelte al primo avvio, cartelle.py).

Uso:  PY strumenti/clip_cliente.py elenco             i video da montare (non ancora montati), dal più nuovo
      PY strumenti/clip_cliente.py metti "<file>"     copia un video (per esempio allegato in chat) tra le clip
      PY strumenti/clip_cliente.py consegna NOME      il video approvato, la copertina e la didascalia in "2 - Video
                                                      finiti"; la clip montata in "1 - Clip da montare/Già montate"
Righe:  CLIP <percorso> | <ora> | <durata s>   /   NESSUNA CLIP   /   MESSA <percorso>
        CONSEGNATO <cartella>  (più VECCHIA <file> per ogni versione di prima spostata in "Versioni vecchie")
Nei video finiti resta solo l'ultima versione approvata di ogni video; le altre vanno in "Versioni vecchie".
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cartelle  # noqa: E402

VIDEO = (".mp4", ".mov", ".m4v")
GIA = "Già montate"
VECCHIE = "Versioni vecchie"


def durata(f):
    try:
        ffprobe = cartelle.leggi(cartelle.PERCORSI).get("ffprobe") or "ffprobe"
        r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                           capture_output=True, text=True, timeout=30)
        return round(float(r.stdout.strip()))
    except Exception:
        return 0


def elenco():
    cart = cartelle.cartella_clip()
    video = [os.path.join(cart, f) for f in os.listdir(cart) if f.lower().endswith(VIDEO)] if os.path.isdir(cart) else []
    if not video:
        print("NESSUNA CLIP")
        return
    for f in sorted(video, key=os.path.getmtime, reverse=True):
        print(f"CLIP {f} | {time.strftime('%d/%m %H:%M', time.localtime(os.path.getmtime(f)))} | {durata(f)} s")


def libero(cart, nome):
    base, est = os.path.splitext(nome)
    dest, n = os.path.join(cart, nome), 2
    while os.path.exists(dest):
        dest, n = os.path.join(cart, f"{base} ({n}){est}"), n + 1
    return dest


def metti(file):
    file = os.path.abspath(os.path.expanduser(file))
    cart = cartelle.cartella_clip()
    os.makedirs(cart, exist_ok=True)
    if os.path.dirname(file) == cart:
        print(f"MESSA {file}")
        return
    dest = libero(cart, os.path.basename(file))
    shutil.copy2(file, dest)
    print(f"MESSA {dest}")


def numero(f):
    m = re.search(r"-v(\d+)\.mp4$", f)
    return int(m.group(1)) if m else 0


def consegna(nome):
    lavoro = os.path.join(cartelle.DATI, "lavori", nome)
    finale = os.path.join(lavoro, "finale")
    versioni = sorted(glob.glob(os.path.join(finale, f"{nome}-v*.mp4")), key=numero)
    if not versioni:
        sys.exit(f"Nessun video finito in {finale}")
    dest = cartelle.cartella_finiti()
    vecchie = os.path.join(dest, VECCHIE)
    os.makedirs(dest, exist_ok=True)
    pezzi = [(versioni[-1], f"{nome}.mp4"),
             (os.path.join(finale, f"{nome}-copertina.jpg"), f"{nome} - copertina.jpg"),
             (os.path.join(finale, f"{nome}-didascalia.txt"), f"{nome} - didascalia.txt")]
    for sorgente, nuovo in pezzi:
        if not os.path.exists(sorgente):
            continue
        meta = os.path.join(dest, nuovo)
        if os.path.exists(meta):   # la versione di prima: nelle vecchie, con la data
            os.makedirs(vecchie, exist_ok=True)
            base, est = os.path.splitext(nuovo)
            vecchio = libero(vecchie, f"{base} {time.strftime('%Y-%m-%d %H.%M', time.localtime(os.path.getmtime(meta)))}{est}")
            shutil.move(meta, vecchio)
            print(f"VECCHIA {vecchio}")
        shutil.copy2(sorgente, meta)
    # la clip montata: tolta dalle clip da montare, così la volta dopo non si rimonta
    try:
        with open(os.path.join(lavoro, "sorgente.json"), encoding="utf-8") as f:
            girato = json.load(f).get("video", "")
    except (OSError, ValueError):
        girato = ""
    clip = cartelle.cartella_clip()
    if girato and os.path.exists(girato) and os.path.dirname(os.path.abspath(girato)) == os.path.abspath(clip):
        os.makedirs(os.path.join(clip, GIA), exist_ok=True)
        shutil.move(girato, libero(os.path.join(clip, GIA), os.path.basename(girato)))
    print(f"CONSEGNATO {dest}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "elenco":
        elenco()
    elif cmd == "metti" and len(sys.argv) > 2:
        metti(sys.argv[2])
    elif cmd == "consegna" and len(sys.argv) > 2:
        consegna(sys.argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
