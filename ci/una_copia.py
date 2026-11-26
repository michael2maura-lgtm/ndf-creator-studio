#!/usr/bin/env python3
"""Una sola copia dei file uguali tra gli stili pronti (suoni e font): lo studio pesa meno a ogni versione.

I font uguali a quelli di STUDIO/font restano solo lì; i suoni ripetuti in più stili vanno una volta sola in
STUDIO/suoni/stili. stile.json punta lì con un percorso relativo ("../../font/X.ttf", "../../suoni/stili/x.mp3"),
che vale in tutti gli strumenti perché tutti uniscono la cartella dello stile con il percorso scritto in stile.json.
Si rilancia quando si aggiunge o si cambia uno stile pronto:   python3 ci/una_copia.py
"""
import collections
import hashlib
import json
import os
import shutil

STUDIO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ndf-creator-studio", "skills",
                      "monta-video")
STILI = os.path.join(STUDIO, "stili")
FONT = os.path.join(STUDIO, "font")
COMUNI = os.path.join(STUDIO, "suoni", "stili")


def impronta(p):
    with open(p, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def main():
    font_di_serie = {impronta(os.path.join(FONT, f)): f for f in os.listdir(FONT) if f.endswith(".ttf")}
    usi = collections.defaultdict(list)
    for k in sorted(os.listdir(STILI)):
        for sotto in ("suoni", "font"):
            d = os.path.join(STILI, k, sotto)
            for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                usi[impronta(os.path.join(d, f))].append((k, f"{sotto}/{f}"))
    os.makedirs(COMUNI, exist_ok=True)
    nuovi = {}
    for h, lista in usi.items():
        k0, rel0 = lista[0]
        if rel0.startswith("font/") and h in font_di_serie:
            dove = f"../../font/{font_di_serie[h]}"
        elif len(lista) > 1 and rel0.startswith("suoni/"):
            nome = os.path.basename(rel0)
            if os.path.exists(os.path.join(COMUNI, nome)) and impronta(os.path.join(COMUNI, nome)) != h:
                b, e = os.path.splitext(nome)
                nome = f"{b}-{h[:6]}{e}"
            if not os.path.exists(os.path.join(COMUNI, nome)):
                shutil.copy2(os.path.join(STILI, k0, rel0), os.path.join(COMUNI, nome))
            dove = f"../../suoni/stili/{nome}"
        else:
            continue
        for k, rel in lista:
            nuovi.setdefault(k, {})[rel] = dove
    tolti = 0

    for k, mappa in nuovi.items():
        p = os.path.join(STILI, k, "stile.json")
        with open(p, encoding="utf-8") as f:
            testo = f.read()
        for vecchio, nuovo in mappa.items():   # sul testo, così il file resta scritto come prima
            testo = testo.replace(f'"{vecchio}"', f'"{nuovo}"')
        with open(p, "w", encoding="utf-8") as f:
            f.write(testo)
        for rel in mappa:
            fp = os.path.join(STILI, k, rel)
            tolti += os.path.getsize(fp)
            os.remove(fp)
        for sotto in ("suoni", "font"):
            d = os.path.join(STILI, k, sotto)
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
    print(f"tolti {tolti / 1e6:.1f} MB di copie")


if __name__ == "__main__":
    main()
