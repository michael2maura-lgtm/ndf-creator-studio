"""Installa tutto in una volta, in primo piano: il programma di avvio (controllo e riparazione) e poi i pezzi grandi.
Serve a chi chiama ancora il vecchio comando ("uv run ... installa.py") e al robot di prova; il cliente usa il
programma di avvio (avvio.sh / avvio.ps1) e scarica.py in sottofondo, come dice il Passo 0 di SKILL.md.

Uso:  <qualsiasi Python 3> strumenti/installa.py
Righe: quelle del controllo (STATO ..., PRONTO / NON PRONTO), quelle di scarica.py, poi FINE.
"""
import os
import platform
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from cartelle import PY  # noqa: E402

WIN = platform.system() == "Windows"


def main():
    print("Installo lo studio: la prima volta ci vogliono 10-20 minuti.", flush=True)
    if WIN:
        avvio = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(QUI, "avvio.ps1")]
    else:
        avvio = ["sh", os.path.join(QUI, "avvio.sh")]
    r = subprocess.run(avvio + sys.argv[1:])
    if r.returncode != 0 or not os.path.exists(PY):
        print("FINE: lo studio NON è pronto (vedi le righe STATO ... MANCA qui sopra).", flush=True)
        sys.exit(1)
    s = subprocess.run([PY, os.path.join(QUI, "scarica.py")])
    print("FINE: lo studio è pronto." if s.returncode == 0 else
          "FINE: lo studio è pronto, ma qualche pezzo grande non è arrivato: il primo montaggio lo riscarica da solo.",
          flush=True)


if __name__ == "__main__":
    main()
