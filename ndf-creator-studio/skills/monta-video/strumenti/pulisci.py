"""Libera spazio togliendo i file di lavoro dei video già finiti (Michael, 25/11/2026: una cliente non riusciva a
montare con il disco pieno). Si cancella SOLO con il permesso del cliente: prima `controlla`, poi `libera`.

    PY pulisci.py controlla    quanto si libera, lavoro per lavoro (non cancella niente)
    PY pulisci.py libera       cancella i file di lavoro dei lavori finiti (dopo il sì del cliente)

Quali lavori: quelli con un video finito in finale/, fermi da almeno 3 giorni, che non aspettano correzioni
(note.json "da correggere") e che non sono VSL (il nome o il piano dicono vsl).
Di ognuno TIENE: l'ultima versione finita e la sua copia per il telefono, copertina, didascalia, crediti, il video
tagliato e il suo audio (servono per una correzione), piano, tagli, parole, trascrizione, faccia, i fogli di controllo.
TOGLIE (si rifà tutto da solo se serve): le versioni finite vecchie e le loro copie per il telefono, la cartella di
montaggio reel/, i pezzi scontornati (*.webm), l'audio grezzo audio.wav, le cartelle temporanee, tagliato-colore.mp4.
Righe:  LAVORO <nome> <MB>   /   SI POSSONO LIBERARE <GB> GB (<n> lavori)   /   LIBERATI <GB> GB   /   NIENTE DA LIBERARE
"""
import os
import re
import shutil
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, leggi  # noqa: E402

LAVORI = os.path.join(DATI, "lavori")
FERMO = 3 * 24 * 3600   # un lavoro toccato negli ultimi 3 giorni è ancora in corso


def peso(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    tot = 0
    for radice, _, file in os.walk(p):
        for f in file:
            try:
                tot += os.path.getsize(os.path.join(radice, f))
            except OSError:
                pass
    return tot


def ultimo_ritocco(cart):
    t = 0
    for radice, _, file in os.walk(cart):
        for f in file:
            try:
                t = max(t, os.path.getmtime(os.path.join(radice, f)))
            except OSError:
                pass
    return t


def da_togliere(nome):
    """I file di lavoro che si possono togliere da questo lavoro, o [] se il lavoro va lasciato com'è."""
    cart = os.path.join(LAVORI, nome)
    fin = os.path.join(cart, "finale")
    versioni = []
    for f in os.listdir(fin) if os.path.isdir(fin) else []:
        m = re.fullmatch(re.escape(nome) + r"-v(\d+)\.mp4", f)
        if m:
            versioni.append(int(m.group(1)))
    if not versioni or "vsl" in nome.lower():
        return []
    try:
        piano = leggi(os.path.join(cart, "piano.json"))
    except (OSError, ValueError):
        piano = {}
    if "vsl" in str(piano.get("stile", "")).lower() or piano.get("orizzontale"):
        return []
    try:
        if leggi(os.path.join(cart, "note.json")).get("stato") == "da correggere":
            return []
    except (OSError, ValueError):
        pass
    if time.time() - ultimo_ritocco(cart) < FERMO:
        return []
    ultima = max(versioni)
    via = []
    for v in versioni:
        if v != ultima:
            via.append(os.path.join(fin, f"{nome}-v{v}.mp4"))
    ctrl = os.path.join(cart, "controllo")
    for f in os.listdir(ctrl) if os.path.isdir(ctrl) else []:
        m = re.fullmatch(re.escape(nome) + r"-v(\d+)-telefono\.mp4", f)
        if (m and int(m.group(1)) != ultima) or f == "tagliato-telefono.mp4":
            via.append(os.path.join(ctrl, f))
    for f in os.listdir(cart):
        p = os.path.join(cart, f)
        if f in ("reel", "audio.wav", "tagliato-colore.mp4") or f.endswith(".webm") or \
                (os.path.isdir(p) and f.startswith("tmp")):
            via.append(p)
    return [p for p in via if os.path.exists(p)]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in ("controlla", "libera"):
        sys.exit(__doc__)
    totale, quanti = 0, 0
    for nome in sorted(os.listdir(LAVORI)) if os.path.isdir(LAVORI) else []:
        if not os.path.isdir(os.path.join(LAVORI, nome)):
            continue
        via = da_togliere(nome)
        mb = sum(peso(p) for p in via)
        if mb < 5 * 1024 * 1024:   # meno di 5 MB: non vale la pena
            continue
        quanti += 1
        totale += mb
        print(f"LAVORO {nome} {mb / 1024 / 1024:.0f} MB", flush=True)
        if cmd == "libera":
            for p in via:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    try:
                        os.remove(p)
                    except OSError:
                        pass
    if not quanti:
        print("NIENTE DA LIBERARE")
    elif cmd == "controlla":
        print(f"SI POSSONO LIBERARE {totale / 1024 ** 3:.1f} GB ({quanti} lavori)")
    else:
        print(f"LIBERATI {totale / 1024 ** 3:.1f} GB ({quanti} lavori)")


if __name__ == "__main__":
    main()
