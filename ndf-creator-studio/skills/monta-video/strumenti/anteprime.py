"""Le anteprime video della pagina: non stanno nel programma dello studio (ci/sposta_anteprime.py) ma nella cartella
anteprime/ del progetto. Si prendono solo quando la pagina le mostra, in quest'ordine:
  1. nel programma (le versioni di prima le avevano dentro);
  2. nella copia del progetto che l'app Claude tiene sul computer (~/.claude/plugins/marketplaces/...): niente download;
  3. nella casa dello studio, se scaricate un'altra volta;
  4. da GitHub, scaricate nella casa dello studio (una volta sola).
Solo libreria standard.
"""
import json
import os
import urllib.request

import cartelle

ELENCO = os.path.join(cartelle.PROGRAMMA, "anteprime.json")
GITHUB = "https://raw.githubusercontent.com/michael2maura-lgtm/ndf-creator-studio/main/anteprime/"
CACHE = os.path.join(cartelle.CASA, "anteprime")


def elenco():
    try:
        with open(ELENCO, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _progetto():
    conf = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    # anche la cartella del progetto stesso (prove sul computer di Michael)
    return [os.path.join(conf, "plugins", "marketplaces", "ndf-creator-studio", "anteprime"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(cartelle.PROGRAMMA))), "anteprime")]


def c_e(rel):
    """La pagina può mostrarla? (sta nell'elenco o nel programma)"""
    return rel in elenco() or os.path.exists(os.path.join(cartelle.PROGRAMMA, *rel.split("/")))


def dove(rel, scarica=True):
    """Il file sul computer, o None. Con scarica=True la prende da GitHub se non c'è."""
    parti = rel.split("/")
    byte = elenco().get(rel)
    for base in [cartelle.PROGRAMMA] + _progetto() + [CACHE]:
        p = os.path.join(base, *parti)
        if os.path.exists(p) and (byte is None or os.path.getsize(p) == byte or base == cartelle.PROGRAMMA):
            return p
    if not scarica or rel not in elenco():
        return None
    dest = os.path.join(CACHE, *parti)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        with urllib.request.urlopen(GITHUB + urllib.request.quote(rel), timeout=60) as r, open(dest + ".parziale", "wb") as f:
            f.write(r.read())
        os.replace(dest + ".parziale", dest)
        return dest
    except Exception:
        return None
