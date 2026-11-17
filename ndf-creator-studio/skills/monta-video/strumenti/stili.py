"""Gli stili di chi usa lo studio: quelli pronti (i modelli) e i suoi (copiati da un reel o creati nella pagina).

Uso:  PY strumenti/stili.py elenco            tutti gli stili, quello di default per primo, e da dove viene ognuno
      PY strumenti/stili.py usa "<nome>"      lo fa diventare quello di default ("monta questo video" usa questo)
      PY strumenti/stili.py rinomina "<nome>" "<nome nuovo>"     il nome che si vede nella pagina e in chat
Il default è "stile" in DATI/scelte.json (lo stesso che sceglie la pagina): cambialo solo se l'utente lo chiede.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, leggi, scrivi  # noqa: E402

STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tutti():
    """Come la pagina: i modelli dello studio e gli stili tuoi (una copia di uno stile dello studio non è "tuo")."""
    out = {}
    for base in (os.path.join(STUDIO, "stili"), os.path.join(DATI, "stili")):
        if not os.path.isdir(base):
            continue
        for k in sorted(os.listdir(base)):
            p = os.path.join(base, k, "stile.json")
            if not os.path.exists(p) or k.startswith("zz-"):
                continue
            st = leggi(p)
            mio = base.startswith(DATI) and not os.path.isdir(os.path.join(STUDIO, "stili", k))
            if mio or st.get("modello"):
                out[k] = (st, mio, os.path.join(base, k))
    return out


def trova(nome, stili):
    n = nome.lower().replace("stile ", "").strip()
    for k, (st, _, _) in stili.items():
        if n in (k, st.get("nome", "").lower().replace("stile ", "").strip()):
            return k
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    stili = tutti()
    sc_p = os.path.join(DATI, "scelte.json")
    sc = leggi(sc_p) if os.path.exists(sc_p) else {}
    if sys.argv[1] == "elenco":
        ordine = sorted(stili, key=lambda k: (k != sc.get("stile"), stili[k][1], stili[k][0].get("ordine", 50), k))
        for k in ordine:
            st, mio, _ = stili[k]
            fonte = st.get("fonte") or {}
            da = ", ".join(fonte.get("esempi") or ([fonte["esempio"]] if fonte.get("esempio") else []))
            print(f'{"* " if k == sc.get("stile") else "  "}{st.get("nome", k).replace("Stile ", "")}  ({k})'
                  f'  {"tuo" if mio else "modello"}{"  da: " + da if da else ""}')
        if not sc.get("stile"):
            print("Nessuno di default: si usa quello scelto in chat, se no il modello consigliato (Chiaro).")
    elif sys.argv[1] == "usa" and len(sys.argv) > 2:
        k = trova(sys.argv[2], stili)
        if not k:
            sys.exit(f"Non trovo lo stile \"{sys.argv[2]}\". Quelli che ci sono: " + ", ".join(stili))
        sc["stile"] = k
        scrivi(sc_p, sc)
        print(f"DEFAULT {k}")
    elif sys.argv[1] == "rinomina" and len(sys.argv) > 3:
        k = trova(sys.argv[2], stili)
        if not k or not stili[k][1]:
            sys.exit("Si rinominano solo gli stili tuoi, non i modelli.")
        p = os.path.join(stili[k][2], "stile.json")
        st = leggi(p)
        st["nome"] = "Stile " + sys.argv[3].strip()
        scrivi(p, st)
        print(f"RINOMINATO {k} -> {st['nome']}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
