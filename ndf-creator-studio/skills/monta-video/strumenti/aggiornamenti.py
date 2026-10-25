"""C'è una versione nuova dello studio? Controlla in silenzio lo spazio GitHub da cui è stato installato.

Uso:  python3 strumenti/aggiornamenti.py
Stampa una riga sola: "AGGIORNATO x.y.z", oppure "NUOVA VERSIONE x.y.z (hai a.b.c)", oppure niente se non può
controllare (niente internet, installazione a mano): in quel caso si va avanti come se niente fosse.
"""
import json
import os
import subprocess

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.dirname(os.path.dirname(QUI))
NEGOZIO = os.path.expanduser("~/.claude/plugins/marketplaces/ndf-creator-studio")


def numeri(v):
    return tuple(int(x) for x in v.split(".")[:3])


def main():
    mia = json.load(open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))["version"]
    if not os.path.isdir(os.path.join(NEGOZIO, ".git")):
        return
    try:
        subprocess.run(["git", "-C", NEGOZIO, "fetch", "--quiet"], timeout=20, capture_output=True)
        r = subprocess.run(["git", "-C", NEGOZIO, "show", "origin/HEAD:ndf-creator-studio/.claude-plugin/plugin.json"],
                           capture_output=True, text=True, timeout=10)
        ultima = json.loads(r.stdout)["version"]
    except Exception:
        return
    print(f"NUOVA VERSIONE {ultima} (hai {mia})" if numeri(ultima) > numeri(mia) else f"AGGIORNATO {mia}")


if __name__ == "__main__":
    main()
