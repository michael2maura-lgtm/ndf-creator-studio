"""Foto di prova del reel (prima di creare il video): fotogrammi in alcuni momenti, in un foglio unico.

Uso:  python3 strumenti/foto.py <nome-lavoro> 2.5,10.4,33.0
Scrive lavori/<nome>/reel/snapshots/contact-sheet.jpg (da guardare). Prima lancia costruisci.py (anche con --zone).
"""
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import HYPERFRAMES, NPX, cartella_lavoro, env_node  # noqa: E402


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    reel = os.path.join(cartella_lavoro(sys.argv[1]), "reel")
    shutil.rmtree(os.path.join(reel, "snapshots"), ignore_errors=True)
    r = subprocess.run([NPX, "--yes", HYPERFRAMES, "snapshot", "--at", sys.argv[2], "--no-end", "--describe", "false"],
                       cwd=reel, capture_output=True, text=True, env=env_node())
    foglio = os.path.join(reel, "snapshots", "contact-sheet.jpg")
    print(foglio if os.path.exists(foglio) else "Errore:\n" + (r.stderr or r.stdout)[-1500:])


if __name__ == "__main__":
    main()
