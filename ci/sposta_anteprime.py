#!/usr/bin/env python3
"""Le anteprime video della pagina (effetti, sottotitoli, transizioni, stili) fuori dal programma dello studio.

Il programma (ndf-creator-studio/) si copia intero a ogni versione sul computer del cliente: le anteprime, circa
60 MB, stanno invece una volta sola nella cartella anteprime/ del progetto. La pagina le prende quando le mostra
(strumenti/anteprime.py): dalla copia del progetto che l'app Claude tiene già sul computer, o da GitHub.
Si rilancia dopo aver rifatto un'anteprima (anteprima_sottotitoli.py, gli effetti, uno stile):
    python3 ci/sposta_anteprime.py
Scrive l'elenco in ndf-creator-studio/skills/monta-video/anteprime.json ({percorso: byte}).
"""
import glob
import json
import os
import shutil

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO = os.path.join(QUI, "ndf-creator-studio", "skills", "monta-video")
FUORI = os.path.join(QUI, "anteprime")
SCHEMI = ["effetti/anteprime/*.mp4", "sottotitoli/anteprime/*.mp4", "transizioni/anteprime/*.mp4",
          "stili/*/anteprima.mp4", "stili/*/telefono.mp4"]


def main():
    elenco_p = os.path.join(STUDIO, "anteprime.json")
    elenco = json.load(open(elenco_p, encoding="utf-8")) if os.path.exists(elenco_p) else {}
    spostati = 0
    for schema in SCHEMI:
        for p in glob.glob(os.path.join(STUDIO, schema)):
            rel = os.path.relpath(p, STUDIO).replace(os.sep, "/")
            dest = os.path.join(FUORI, *rel.split("/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(p, dest)
            elenco[rel] = os.path.getsize(dest)
            spostati += elenco[rel]
    elenco = {k: v for k, v in sorted(elenco.items()) if os.path.exists(os.path.join(FUORI, *k.split("/")))}
    with open(elenco_p, "w", encoding="utf-8") as f:
        json.dump(elenco, f, indent=1)
        f.write("\n")
    print(f"spostati {spostati / 1e6:.1f} MB; anteprime in elenco: {len(elenco)}")


if __name__ == "__main__":
    main()
