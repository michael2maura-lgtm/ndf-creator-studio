"""Musiche libere (pubblico dominio, CC0): elenco in STUDIO/musica/libere.json. Non stanno nel plugin: si scaricano
dalla loro pagina originale sul computer del cliente, in DATI/suoni/musiche-libere/ (così compaiono anche nella pagina
"Scegli il tuo look", tra le Musiche).

    PY musiche.py scarica          scarica quelle che mancano (all'installazione; si può rilanciare)
    PY musiche.py scegli <tono>    il brano per questo video: calma | energica | positiva | morbida | carica
                                   (stampa il percorso da mettere nel piano: "musica": "<percorso>"); non ripete
                                   i brani usati negli ultimi video
    PY musiche.py elenco           i brani con il loro tono

Righe:  MUSICHE PRONTE n   /   MUSICA <percorso> (<tono>)   /   MANCA <id> (non scaricata: si usa la musica dello stile)
"""
import hashlib
import json
import os
import random
import subprocess
import sys
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, STUDIO, leggi, scrivi  # noqa: E402

CATALOGO = os.path.join(STUDIO, "musica", "libere.json")
CARTELLA = os.path.join(DATI, "suoni", "musiche-libere")
USATE = os.path.join(DATI, "musiche-usate.json")
TONI = ("calma", "energica", "positiva", "morbida", "carica")


def voci():
    return leggi(CATALOGO)["voci"]


def percorso(v):
    return os.path.join(CARTELLA, f"musica-{v['tono']}-{v['id']}.mp3")


def scarica():
    os.makedirs(CARTELLA, exist_ok=True)
    pronte = 0
    for v in voci():
        dest = percorso(v)
        if os.path.exists(dest):
            pronte += 1
            continue
        grezzo = dest + ".scarico." + v["estensione"]
        try:
            req = urllib.request.Request(v["file"], headers={"User-Agent": "Mozilla/5.0 (NDF Creator Studio)"})
            with urllib.request.urlopen(req, timeout=180) as r, open(grezzo, "wb") as f:
                f.write(r.read())
            if hashlib.sha256(open(grezzo, "rb").read()).hexdigest() != v["sha256"]:
                print(f"MANCA {v['id']} (il file alla fonte è cambiato: non lo uso)", flush=True)
                continue
            subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-i", grezzo, "-ac", "2", "-ar", "44100",
                            "-b:a", "160k", dest], check=True)
            pronte += 1
        except Exception:
            print(f"MANCA {v['id']} (non scaricata: si usa la musica dello stile)", flush=True)
        finally:
            if os.path.exists(grezzo):
                os.remove(grezzo)
    print(f"MUSICHE PRONTE {pronte}", flush=True)


def scegli(tono):
    if tono not in TONI:
        sys.exit(f"Tono sconosciuto: {tono}. Toni: {', '.join(TONI)}")
    try:
        usate = leggi(USATE)
    except (OSError, ValueError):
        usate = []
    tutte = [v for v in voci() if v["tono"] == tono and os.path.exists(percorso(v))]
    if not tutte:
        scarica()
        tutte = [v for v in voci() if v["tono"] == tono and os.path.exists(percorso(v))]
    if not tutte:
        print(f"MANCA {tono} (nessuna musica scaricata: si usa quella dello stile)")
        return
    fresche = [v for v in tutte if v["id"] not in usate[-6:]] or tutte   # non ripetere gli ultimi 6 video
    v = random.choice(fresche)
    scrivi(USATE, (usate + [v["id"]])[-30:])
    print(f"MUSICA {percorso(v)} ({tono})")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "scarica":
        scarica()
    elif cmd == "scegli" and len(sys.argv) > 2:
        scegli(sys.argv[2])
    elif cmd == "elenco":
        for v in voci():
            print(f"{v['tono']:9} {v['id']:15} di {v['autore']}{'' if os.path.exists(percorso(v)) else '  (non scaricata)'}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
