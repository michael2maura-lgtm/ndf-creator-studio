"""Registro contro le ripetizioni: una riga per ogni video montato, solo le ultime 10 (le altre vanno in archivio).

Uso:  python3 strumenti/registro.py <stile> "<lavoro> | scene: ... | clip: ... | omini: ... | suoni: ..."
Scrive in stili/<stile>/registro.md. Prima di scegliere le scene di un video nuovo, leggi le ultime 5 righe e usa
qualcosa di diverso (clip, pose, scene d'apertura); scrivi quello che hai usato davvero, non quello pianificato.
"""
import os
import sys
from datetime import date

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import cartella_stile  # noqa: E402

TENUTE = 10


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cart = cartella_stile(sys.argv[1])
    reg, arch = os.path.join(cart, "registro.md"), os.path.join(cart, "registro-archivio.md")
    righe = [r for r in open(reg, encoding="utf-8").read().splitlines() if r.startswith("- ")] if os.path.exists(reg) else []
    righe.append(f"- {date.today().isoformat()} | {sys.argv[2]}")
    vecchie, righe = righe[:-TENUTE], righe[-TENUTE:]
    if vecchie:
        with open(arch, "a", encoding="utf-8") as f:
            f.write("\n".join(vecchie) + "\n")
    with open(reg, "w", encoding="utf-8") as f:
        f.write("# Registro: cosa è stato usato negli ultimi video (il più recente in fondo)\n\n" + "\n".join(righe) + "\n")
    print(f"Registro aggiornato: {len(righe)} righe.")


if __name__ == "__main__":
    main()
