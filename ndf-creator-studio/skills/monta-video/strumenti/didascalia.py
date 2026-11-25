"""Controlla la didascalia del reel (finale/NOME-didascalia.txt) prima di consegnarla. Regole in regole/didascalia.md.

    PY didascalia.py NOME

Stampa la prima riga come la vede chi scorre (fino a «...altro»), poi:
  DIDASCALIA OK                         oppure
  DA SISTEMARE: <cosa>                   una riga per ogni problema (la prima riga troppo lunga, troppi hashtag,
                                         un link, due richieste, una frase rischiosa per il network...)
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, cartella_lavoro, leggi  # noqa: E402

# frasi che nel network marketing possono creare problemi (promesse di soldi o di salute)
RISCHIO = [
    (r"guadagn\w*\s+(garantit|sicur|assicurat)\w*|guadagni\s+da\s+\d|\d[\d.]*\s*(€|euro)\s*(al|a)\s*(mese|settimana|giorno)",
     "promessa di guadagno"),
    (r"soldi\s+facili|rendita\s+passiva|libert[àa]\s+finanziaria|diventa\w*\s+ricc", "promessa di soldi"),
    (r"\bguarisc\w*|\bcura\s+(il|la|i|le|l')|\bcurare\b|\bprevien\w*|elimina\w*\s+(il\s+)?dolor\w*|antinfiammatori",
     "effetto medico"),
    (r"dimagri\w*\s+(di\s+)?\d+\s*(kg|chil)|perso\s+\d+\s*(kg|chil)|brucia\s*grassi|perdi\s+peso\s+(in|senza)", "promessa di peso"),
    (r"senza\s+fatica|risultati\s+garantit\w*|garantit[oa]\s+al\s+100", "risultato garantito"),
]
RICHIESTE = r"\b(commenta|scrivimi|scrivi\s+in\s+dm|mandami|seguimi|segui\s+per|salva(lo|la)?\b|condividi|clicca|tagga)"
BANALI = {"#viral", "#fyp", "#foryou", "#foryoupage", "#explorepage", "#explore", "#reels", "#instagram"}


def crediti_da_citare(nome):
    """Le righe di credito delle foto usate nel piano che lo chiedono (DATI/immagini/<foto>.crediti.json)."""
    try:
        piano = leggi(os.path.join(cartella_lavoro(nome), "piano.json"))
    except (OSError, ValueError):
        return []
    trovate = []

    def giro(x):
        if isinstance(x, dict):
            for v in x.values():
                giro(v)
        elif isinstance(x, list):
            for v in x:
                giro(v)
        elif isinstance(x, str):
            base = os.path.splitext(os.path.basename(x))[0]
            c = os.path.join(DATI, "immagini", base + ".crediti.json")
            if base and os.path.exists(c):
                testo = leggi(c).get("testo")
                if testo and testo not in trovate:
                    trovate.append(testo)
    giro(piano)
    return trovate


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = sys.argv[1]
    p = os.path.join(cartella_lavoro(nome), "finale", f"{nome}-didascalia.txt")
    if not os.path.exists(p):
        sys.exit(f"Manca {p}: scrivila prima (regole/didascalia.md).")
    testo = open(p, encoding="utf-8").read().strip()
    righe = [r for r in testo.splitlines() if r.strip()]
    prima = righe[0] if righe else ""
    print("PRIMA RIGA (prima di «...altro»): " + prima[:125] + ("…" if len(prima) > 125 else ""))
    problemi = []
    if len(prima) > 125:
        problemi.append(f"la prima riga è lunga {len(prima)} caratteri: sotto i 125 si legge intera")
    if prima.lstrip().startswith("#") or re.match(r"^(ciao|buongiorno|buonasera|hey)\b", prima.strip(), re.I):
        problemi.append("la prima riga non deve essere un saluto o un hashtag")
    if len(testo) > 2200:
        problemi.append(f"troppo lunga: {len(testo)} caratteri (Instagram ne tiene 2.200)")
    tag = re.findall(r"#\w+", testo)
    if len(tag) > 5:
        problemi.append(f"{len(tag)} hashtag: al massimo 5")
    banali = [t for t in tag if t.lower() in BANALI]
    if banali:
        problemi.append("hashtag che non descrivono niente: " + " ".join(banali))
    if re.search(r"https?://|www\.|\b\w+\.(com|it|net|ly)\b", testo, re.I):
        problemi.append("c'è un link: nella didascalia non si clicca, va nella bio o in DM")
    tipi = {re.sub(r"(lo|la)$", "", m.group(1).lower().split()[0]) for m in re.finditer(RICHIESTE, testo, re.I)}
    if len(tipi) > 1:
        problemi.append("più di una richiesta (" + ", ".join(sorted(tipi)) + "): tienine una sola")
    for schema, cosa in RISCHIO:
        for m in re.finditer(schema, testo, re.I):
            problemi.append(f"frase rischiosa per il network ({cosa}): «{m.group(0)}»")
    for cred in crediti_da_citare(nome):   # foto di Wikimedia con licenza CC BY: l'autore va citato
        if cred.split(",")[0].replace("Foto: ", "").strip().lower() not in testo.lower():
            problemi.append(f"manca il credito di una foto: aggiungi in fondo la riga «{cred}»")
    if problemi:
        for x in problemi:
            print("DA SISTEMARE: " + x)
    else:
        print(f"DIDASCALIA OK ({len(testo)} caratteri, {len(tag)} hashtag)")


if __name__ == "__main__":
    main()
