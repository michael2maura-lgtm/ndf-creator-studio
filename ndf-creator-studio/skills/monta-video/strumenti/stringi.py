"""Passo 2b: toglie da solo le pause, dentro e ai bordi dei pezzi scelti in tagli.json. Lo lancia taglia.py.

Uso:  PY strumenti/stringi.py <nome-lavoro> [--respiri]

Claude sceglie in tagli.json QUALI frasi tenere (l'ultima ripresa buona). Questo strumento ascolta il volume della voce
e taglia ogni silenzio più lungo di PAUSA_MAX, lasciando un margine ai bordi delle parole, così il reel non si
ferma mai. Il file scelto da Claude resta in tagli-scelti.json; tagli.json diventa la versione stretta.
--respiri: lascia le pause dentro le frasi (ritmo calmo), stringe solo i bordi dei pezzi.
Nel pezzo di tagli.json "stringi": false lo lascia com'è (una pausa voluta).
"""
import os
import subprocess
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, cartella_lavoro, leggi, scrivi  # noqa: E402

SR = 16000
PASSO = 0.01            # 10 ms per misura
PAUSA_MAX = 0.32        # un silenzio più lungo di così si taglia (era 0,22: frasi attaccate senza respiro, 23/11/2026)
MARGINE_PRIMA = 0.10    # aria lasciata prima che riparta la voce (non mangiare la prima lettera)
MARGINE_DOPO = 0.18     # aria lasciata dopo l'ultima parola (le code basse e un piccolo respiro: tra due frasi restano
                        # circa 0,28 s, approvato da Michael sul reel prova-2 v6, 23/11/2026)
PEZZO_MIN = 0.18        # pezzi di voce più corti di così non si separano (una sillaba sola non sta da sola)


def volume(video, pulizia="highpass=f=90"):
    """Il volume della voce ogni 10 ms, in dB. pulizia: i filtri della voce, così si misura come suonerà nel reel."""
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", str(SR), "-af", pulizia,
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = int(SR * PASSO)
    a = a[: len(a) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((a ** 2).mean(axis=1)) + 1e-9)


def parti_di_voce(db, da, a, soglia):
    """I tratti con la voce dentro [da, a], come (inizio, fine) in secondi."""
    i0, i1 = int(da / PASSO), min(int(a / PASSO), len(db))
    voce = db[i0:i1] > soglia
    out, inizio = [], None
    for k, v in enumerate(voce):
        t = (i0 + k) * PASSO
        if v and inizio is None:
            inizio = t
        if not v and inizio is not None:
            out.append([inizio, t])
            inizio = None
    if inizio is not None:
        out.append([inizio, i1 * PASSO])
    # silenzi corti dentro la voce: non sono pause, si uniscono
    unite = []
    for p in out:
        if unite and p[0] - unite[-1][1] <= PAUSA_MAX:
            unite[-1][1] = p[1]
        else:
            unite.append(p)
    # schiocchi isolati (< 60 ms) non sono voce
    return [p for p in unite if p[1] - p[0] >= 0.06]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cart = cartella_lavoro(sys.argv[1])
    respiri = "--respiri" in sys.argv
    scelti_f = os.path.join(cart, "tagli-scelti.json")
    tagli_f = os.path.join(cart, "tagli.json")
    # se Claude ha riscritto tagli.json dopo l'ultima stretta, quello nuovo è la scelta
    if not os.path.exists(scelti_f) or os.path.getmtime(tagli_f) > os.path.getmtime(scelti_f) + 1:
        scrivi(scelti_f, leggi(tagli_f))
    scelti = leggi(scelti_f)
    sorgente = leggi(os.path.join(cart, "sorgente.json"))
    from taglia import VOCE   # la stessa pulizia di taglia.py: il fruscio che toglie non è voce
    db = volume(sorgente["video"], "anull" if "--voce-originale" in sys.argv else VOCE)
    # soglia della voce: 20 dB sotto la voce tipica di questo girato
    voce_tipica = float(np.percentile(db[db > -60], 80)) if (db > -60).any() else -20
    soglia = max(voce_tipica - 18, -50)   # il fruscio di fondo che la pulizia della voce toglie non conta come voce

    nuovi, tolto, n_pause = [], 0.0, 0
    for t in scelti:
        if t.get("stringi") is False:
            nuovi.append(t)
            continue
        parti = parti_di_voce(db, t["da"], t["a"], soglia)
        if not parti:
            nuovi.append(t)
            continue
        # ai bordi del pezzo: una coda corta e bassa (la fine della frase prima, un respiro) non è voce da tenere
        def debole(p):
            i0, i1 = int(p[0] / PASSO), int(p[1] / PASSO)
            return p[1] - p[0] < PEZZO_MIN and float(db[i0:i1].max()) < voce_tipica - 5
        while len(parti) > 1 and debole(parti[0]):
            parti = parti[1:]
        while len(parti) > 1 and debole(parti[-1]):
            parti = parti[:-1]
        if respiri:
            parti = [[parti[0][0], parti[-1][1]]]
        # i pezzi troppo corti si attaccano al vicino (mai una sillaba da sola)
        unite = []
        for p in parti:
            if unite and (p[1] - p[0] < PEZZO_MIN or unite[-1][1] - unite[-1][0] < PEZZO_MIN):
                unite[-1][1] = p[1]
            else:
                unite.append(p)
        for k, (a, b) in enumerate(unite):
            da = max(t["da"], a - MARGINE_PRIMA)
            fine = min(t["a"], b + MARGINE_DOPO)
            nuovo = dict(t, id=t["id"] if len(unite) == 1 else f"{t['id']}-{k + 1}", da=round(da, 3), a=round(fine, 3))
            nuovi.append(nuovo)
        tenuto = sum(min(t["a"], b + MARGINE_DOPO) - max(t["da"], a - MARGINE_PRIMA) for a, b in unite)
        tolto += (t["a"] - t["da"]) - tenuto
        n_pause += len(unite) - 1
    scrivi(tagli_f, nuovi)
    print(f"Pause tolte: {n_pause} dentro le frasi, {tolto:.1f} s in tutto ({len(scelti)} pezzi scelti -> {len(nuovi)} pezzi)")


if __name__ == "__main__":
    main()
