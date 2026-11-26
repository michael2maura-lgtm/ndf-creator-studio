"""VSL: la cartella dei materiali del cliente. All'installazione non si crea niente: nasce quando il cliente scrive
"monta la mia VSL".

Uso:  PY strumenti/vsl_materiali.py "<nome VSL>"           crea ~/NDF Creator Studio/<nome VSL> - materiali e la apre sullo schermo
      PY strumenti/vsl_materiali.py "<nome VSL>" --guarda  (dopo "fatto") elenca cosa c'è dentro, diviso per tipo

Stampa la riga da dire al cliente, con dove si trova in parole semplici.
"""
import os
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cartelle import CARTELLA_CLIENTE  # noqa: E402

TIPI = {"foto": (".jpg", ".jpeg", ".png", ".heic", ".webp"), "video": (".mp4", ".mov", ".m4v"),
        "musica": (".mp3", ".wav", ".m4a"), "documenti": (".pdf", ".txt", ".docx")}


def cartella(nome):
    return os.path.join(CARTELLA_CLIENTE, f"{nome} - materiali")   # dove il cliente la vede (non nella casa nascosta)


def apri(percorso):
    """La apre sullo schermo: Finder sul Mac, Esplora file su Windows."""
    try:
        if platform.system() == "Windows":
            os.startfile(percorso)  # noqa: S606
        elif platform.system() == "Darwin":
            subprocess.run(["open", percorso], check=False)
        else:
            subprocess.run(["xdg-open", percorso], check=False)
    except OSError:
        pass


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = sys.argv[1].strip()
    c = cartella(nome)
    dove = f"la tua cartella utente → NDF Creator Studio → {nome} - materiali"
    if "--guarda" in sys.argv:
        if not os.path.isdir(c):
            sys.exit(f"La cartella non c'è ancora: {c}")
        trovati = {k: [] for k in TIPI}
        altri = []
        for radice, _, file in os.walk(c):
            for f in sorted(file):
                if f.startswith("."):
                    continue
                k = next((k for k, est in TIPI.items() if f.lower().endswith(est)), None)
                (trovati[k] if k else altri).append(os.path.relpath(os.path.join(radice, f), c))
        for k, lista in trovati.items():
            print(f"{k.upper()} ({len(lista)}): " + (", ".join(lista) if lista else "nessuno"))
        if altri:
            print(f"ALTRO ({len(altri)}): " + ", ".join(altri))
        return
    os.makedirs(c, exist_ok=True)
    apri(c)
    print(f"CARTELLA {c}")
    print("Ti ho aperto la cartella dei materiali: trascinaci le foto delle tue clienti, le chat, le foto o i video "
          f"del prodotto e la tua musica se ne hai una. Quando hai finito scrivi \"fatto\". La trovi in {dove}.")


if __name__ == "__main__":
    main()
