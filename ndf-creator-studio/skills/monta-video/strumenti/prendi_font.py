"""Scarica un font gratuito (licenza libera, dalla raccolta Google Fonts) quando l'esempio da copiare ne usa uno che
lo studio non ha. Mai un font a pagamento: se non è nella raccolta, si sceglie il più simile tra quelli che ci sono.

Uso:  PY strumenti/prendi_font.py "Nome del font" --stile <nome stile>
      Mette i file .ttf e la licenza in DATI/stili/<stile>/font/ e stampa le righe da scrivere in stile.json
      (font "file", "famiglia", "peso"). Senza --stile li mette in DATI/font/.
Stampa:  PRESO <file> famiglia=<nome>        oppure   NON C'È <nome>  (scegli il più simile tra quelli dello studio)
"""
import json
import os
import re
import sys
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI  # noqa: E402

API = "https://api.github.com/repos/google/fonts/contents/{}/{}"


def elenco(cartella, nome):
    """I file di quel font nella raccolta (solo licenze libere: ofl, apache, ufl)."""
    try:
        req = urllib.request.Request(API.format(cartella, nome), headers={"User-Agent": "studio-video"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:  # noqa: BLE001
        return None


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        sys.exit(__doc__)
    famiglia = sys.argv[1].strip()
    stile = sys.argv[sys.argv.index("--stile") + 1] if "--stile" in sys.argv else None
    dest = os.path.join(DATI, "stili", stile, "font") if stile else os.path.join(DATI, "font")
    chiave = re.sub(r"[^a-z0-9]", "", famiglia.lower())
    for cart in ("ofl", "apache", "ufl"):
        file = elenco(cart, chiave)
        if not file:
            continue
        ttf = [f for f in file if f["name"].lower().endswith(".ttf")]
        lic = [f for f in file if f["name"].upper() in ("OFL.TXT", "LICENSE.TXT", "UFL.TXT")]
        if not ttf:
            continue
        os.makedirs(dest, exist_ok=True)
        for f in ttf + lic:
            nome = f["name"] if f in ttf else f"LICENZA-{chiave}.txt"
            urllib.request.urlretrieve(f["download_url"], os.path.join(dest, nome))
        # il file da usare: il "variabile" (tutti i pesi) se c'è, se no il Regular, se no il primo
        scelto = next((f["name"] for f in ttf if "[" in f["name"] and "italic" not in f["name"].lower()), None) \
            or next((f["name"] for f in ttf if "regular" in f["name"].lower()), ttf[0]["name"])
        for f in ttf:
            print(f"PRESO {os.path.join(dest, f['name'])}")
        print(f'In stile.json: {{"file": "font/{scelto}", "famiglia": "{famiglia}", "peso": 400}}'
              + ("  (variabile: il peso va da 100 a 900, scegli quello dell'esempio)" if "[" in scelto else ""))
        return
    print(f"NON C'È {famiglia}: non è tra i font gratuiti. Usa il più simile tra quelli dello studio e dillo all'utente.")


if __name__ == "__main__":
    main()
