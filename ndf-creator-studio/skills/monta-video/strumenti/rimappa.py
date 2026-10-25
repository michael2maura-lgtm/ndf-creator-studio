"""Quando i tagli cambiano, sposta da solo tutti i tempi del piano (scene, titoli, elenchi, colpi, finale)
sui nuovi tempi del video tagliato. Così non si riscrive il piano a mano.

Uso:  python3 strumenti/rimappa.py <nome-lavoro> <segmenti-vecchi.json>
      (prima di rifare il taglio: cp segmenti.json segmenti-vecchi.json; poi taglia.py; poi questo)
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import cartella_lavoro, leggi, scrivi  # noqa: E402


def a_originale(t, segmenti):
    for s in segmenti:
        if s["inizio"] - 0.001 <= t <= s["inizio"] + s["durata"] + 0.001:
            return s["da_originale"] + (t - s["inizio"])
    return segmenti[-1]["a_originale"]


def da_originale(o, segmenti):
    """Tempo nel nuovo taglio; se quel momento è stato tolto, il primo istante dopo."""
    for s in segmenti:
        if o < s["da_originale"]:
            return s["inizio"]
        if o <= s["a_originale"]:
            return s["inizio"] + (o - s["da_originale"])
    ultimo = segmenti[-1]
    return ultimo["inizio"] + ultimo["durata"]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cart = cartella_lavoro(sys.argv[1])
    vecchi = leggi(sys.argv[2] if os.path.isabs(sys.argv[2]) else os.path.join(cart, sys.argv[2]))
    nuovi = leggi(os.path.join(cart, "segmenti.json"))

    def m(t):
        return round(da_originale(a_originale(t, vecchi), nuovi), 2)

    piano = leggi(os.path.join(cart, "piano.json"))
    for gruppo in ("scene", "titoli", "liste"):
        for x in piano.get(gruppo, []):
            for k in ("da", "a"):
                if k in x:
                    x[k] = m(x[k])
            if "voci" in x:
                x["voci"] = [[v, m(t)] for v, t in x["voci"]]
            if "passi" in x:
                x["passi"] = [[n, v, m(t)] for n, v, t in x["passi"]]
    if "suoni" in piano and "colpi" in piano["suoni"]:
        piano["suoni"]["colpi"] = [m(t) for t in piano["suoni"]["colpi"]]
    if "finale_da" in piano:
        piano["finale_da"] = m(piano["finale_da"])
    for w in piano.get("aggiungi", []):
        w["da"], w["a"] = m(w["da"]), m(w["a"])
    scrivi(os.path.join(cart, "piano.json"), piano)
    print("Piano spostato sui nuovi tempi.")


if __name__ == "__main__":
    main()
