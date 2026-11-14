"""Passo 3b: il controllo dei tagli "a orecchio". Claude non sente: questo strumento ascolta ogni taglio per lui.

Uso:  PY strumenti/controlla_audio.py <nome-lavoro>

Dopo taglia.py e parole.py. Per ogni taglio del video tagliato cerca:
  PAROLA MOZZATA   la voce è piena proprio sul taglio, o una parola lo attraversa: il taglio cade dentro una parola
  SILLABA IN PIÙ   accanto al taglio resta un pezzetto di voce cortissimo e staccato (l'attacco di una parola scartata)
  PAUSA LUNGA      tra un pezzo e l'altro resta un silenzio che si sente
  RIPETIZIONE      le stesse parole dette prima e dopo il taglio (la frase rifatta è rimasta due volte)
Per ognuna scrive il pezzo di tagli.json da sistemare e i secondi del video ORIGINALE, poi l'ultima riga:
  DA SISTEMARE: N
Si sistema tagli.json e si rilancia taglia.py, parole.py e questo controllo, al massimo 3 giri. Finché DA SISTEMARE non
è 0 non si passa al piano. Se dopo 3 giri resta qualcosa, nel messaggio finale si dice all'utente il secondo da ascoltare.
"""
import os
import re
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import cartella_lavoro, leggi, scrivi  # noqa: E402
from stringi import PASSO, volume  # noqa: E402

SILLABA = 0.12      # voce più corta di così, staccata dal resto, accanto a un taglio = avanzo di una parola
STACCO = 0.15       # silenzio che la separa dal resto
PAUSA = 0.32        # silenzio sul taglio che si sente


def norm(w):
    return re.sub(r"[^a-zàèéìòù0-9]", "", w.lower())


def corse(voce):
    """Tratti di voce e di silenzio: [(è_voce, inizio_idx, fine_idx)]."""
    out, k = [], 0
    while k < len(voce):
        j = k
        while j < len(voce) and voce[j] == voce[k]:
            j += 1
        out.append((bool(voce[k]), k, j))
        k = j
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cart = cartella_lavoro(sys.argv[1])
    segmenti = leggi(os.path.join(cart, "segmenti.json"))
    parole = leggi(os.path.join(cart, "parole.json")) if os.path.exists(os.path.join(cart, "parole.json")) else []
    db = volume(os.path.join(cart, "tagliato.mp4"))
    voce_tipica = float(np.percentile(db[db > -60], 80)) if (db > -60).any() else -20
    soglia = max(voce_tipica - 20, -50)
    voce = db > soglia
    piena = db > voce_tipica - 9

    problemi = []

    grezze = []
    if os.path.exists(os.path.join(cart, "parole_grezze.json")):
        grezze = [w for f in leggi(os.path.join(cart, "parole_grezze.json")) for w in f.get("parole", [])]

    def in_originale(t):
        for sg in segmenti:
            if sg["inizio"] <= t < sg["inizio"] + sg["durata"]:
                return sg["da_originale"] + (t - sg["inizio"])
        return None

    def parola_vera(t0, t1):
        """Il pezzetto di voce è una parola vera della frase tenuta (un "La", un "con")? Allora non è un avanzo.
        Si guarda nel video tagliato e anche nel girato originale (Whisper sul tagliato a volte salta le parole corte)."""
        if any(w["da"] < t1 + 0.05 and w["a"] > t0 - 0.05 for w in parole):
            return True
        o0, o1 = in_originale(t0 + 0.005), in_originale(max(t0 + 0.006, t1 - 0.005))
        return o0 is not None and any(w["da"] < (o1 or o0) + 0.08 and w["a"] > o0 - 0.08 for w in grezze)

    def segnala(tipo, seg_prima, seg_dopo, t, cosa, rimedio):
        problemi.append({"tipo": tipo, "secondo": round(t, 2), "prima": seg_prima["id"], "dopo": seg_dopo["id"],
                         "cosa": cosa, "rimedio": rimedio})

    for prima, dopo in zip(segmenti, segmenti[1:]):
        c = dopo["inizio"]
        i = int(round(c / PASSO))
        if i <= 3 or i >= len(db) - 3:
            continue
        fine_orig, inizio_orig = prima["a_originale"], dopo["da_originale"]
        # 1. parola mozzata
        attraversa = [w for w in parole if w["da"] < c - 0.04 and w["a"] > c + 0.04]
        # Whisper allunga la fine delle parole sopra il silenzio: conta solo se sul taglio c'è voce davvero, da tutte e due le parti
        if piena[i - 4] and piena[i - 2] and piena[i + 1] and piena[i + 3]:
            p = attraversa[0]["testo"] if attraversa else "la parola sul taglio"   # la voce è piena da tutte e due le parti
            segnala("PAROLA MOZZATA", prima, dopo, c, f'"{p}" è tagliata a metà',
                    f'sposta la fine di "{prima["id"]}" dopo la parola (orig. {fine_orig:.2f} s) o l\'inizio di "{dopo["id"]}" prima (orig. {inizio_orig:.2f} s)')
        # 2. sillaba in più: un pezzetto di voce corto e staccato subito prima o subito dopo il taglio
        finestra = 0.5
        a0, a1 = max(0, i - int(finestra / PASSO)), i
        cr = corse(voce[a0:a1])
        if len(cr) >= 3 and cr[-1][0] is False and cr[-1][2] - cr[-1][1] < 3:
            cr = cr[:-1]
        if len(cr) >= 2 and cr[-1][0] and 0.05 <= (cr[-1][2] - cr[-1][1]) * PASSO < SILLABA and not cr[-2][0] and (cr[-2][2] - cr[-2][1]) * PASSO >= STACCO:
            t_av = (a0 + cr[-1][1]) * PASSO
            # un avanzo vero è tagliato dal taglio: la voce c'è proprio sul taglio (non è un respiro o una parola corta)
            if voce[i - 1] and not parola_vera(t_av, (a0 + cr[-1][2]) * PASSO): segnala("SILLABA IN PIÙ", prima, dopo, t_av, "alla fine del pezzo resta un pezzetto di parola",
                    f'chiudi "{prima["id"]}" prima (orig. circa {fine_orig - (c - t_av):.2f} s)')
        b0, b1 = i, min(len(voce), i + int(finestra / PASSO))
        cr = corse(voce[b0:b1])
        if cr and cr[0][0] is False and cr[0][2] - cr[0][1] < 3:
            cr = cr[1:]
        if len(cr) >= 2 and cr[0][0] and 0.05 <= (cr[0][2] - cr[0][1]) * PASSO < SILLABA and not cr[1][0] and (cr[1][2] - cr[1][1]) * PASSO >= STACCO:
            t_av = (b0 + cr[0][2]) * PASSO
            if voce[i] and not parola_vera((b0 + cr[0][1]) * PASSO, t_av): segnala("SILLABA IN PIÙ", prima, dopo, c, "all'inizio del pezzo c'è un pezzetto di parola",
                    f'fai partire "{dopo["id"]}" dopo (orig. circa {inizio_orig + (t_av - c):.2f} s)')
        # 3. pausa lunga sul taglio
        k0 = i
        while k0 > 0 and not voce[k0 - 1]:
            k0 -= 1
        k1 = i
        while k1 < len(voce) and not voce[k1]:
            k1 += 1
        if (k1 - k0) * PASSO > PAUSA:
            segnala("PAUSA LUNGA", prima, dopo, c, f"{(k1 - k0) * PASSO:.2f} s di silenzio",
                    f'accorcia la fine di "{prima["id"]}" o l\'inizio di "{dopo["id"]}"')
        # 4. ripetizione: il pezzo dopo ricomincia con le stesse parole appena dette (una ripresa rimasta due volte)
        pr = [norm(w["testo"]) for w in parole if c - 4 <= w["da"] < c]
        do = [norm(w["testo"]) for w in parole if c <= w["da"] < c + 3]
        pr, do = [w for w in pr if w], [w for w in do if w]
        if len(do) >= 3:
            inizio = tuple(do[:3])
            if any(tuple(pr[j:j + 3]) == inizio for j in range(len(pr) - 2)):
                segnala("RIPETIZIONE", prima, dopo, c, f'"{" ".join(inizio)}" detto due volte di fila',
                        f'tieni una volta sola: togli da "{prima["id"]}" la prima ripresa o da "{dopo["id"]}" la seconda')

    scrivi(os.path.join(cart, "controllo", "audio.json") if os.path.isdir(os.path.join(cart, "controllo"))
           else os.path.join(cart, "controllo_audio.json"), problemi)
    for p in problemi:
        print(f'{p["tipo"]:<15} {p["secondo"]:6.2f} s  {p["cosa"]}  ->  {p["rimedio"]}')
    print(f"Tagli controllati: {len(segmenti) - 1}")
    print(f"DA SISTEMARE: {len(problemi)}")


if __name__ == "__main__":
    main()
