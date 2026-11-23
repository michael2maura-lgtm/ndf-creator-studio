"""C'è una versione nuova dello studio? Controlla in silenzio lo spazio GitHub da cui è stato installato.

Uso:  python3 strumenti/aggiornamenti.py
Stampa una riga sola: "AGGIORNATO x.y.z", oppure "NUOVA VERSIONE x.y.z (hai a.b.c)", oppure "DA CARTELLA" se lo studio
è installato da una cartella del computer e non da GitHub (così gli aggiornamenti non arrivano mai: SKILL.md, Passo 0,
dice come reinstallarlo), oppure niente se non può controllare (niente internet): si va avanti come se niente fosse.
"""
import json
import os
import subprocess

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.dirname(os.path.dirname(QUI))
CONFIG = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
NEGOZIO = os.path.join(CONFIG, "plugins", "marketplaces", "ndf-creator-studio")
GITHUB = "michael2maura-lgtm/ndf-creator-studio"


def da_cartella():
    """True se lo studio non arriva da GitHub: marketplace aggiunto da una cartella, o studio caricato fuori dai plugin."""
    try:
        m = json.load(open(os.path.join(CONFIG, "plugins", "known_marketplaces.json"))).get("ndf-creator-studio")
    except (OSError, ValueError):
        m = None
    if m:
        f = m.get("source", {})
        dove = f.get("url", "") + f.get("repo", "")
        if f.get("source") in ("directory", "file") or (dove and GITHUB not in dove):
            return True
    return os.path.join(CONFIG, "plugins") not in os.path.realpath(PLUGIN)


def numeri(v):
    return tuple(int(x) for x in v.split(".")[:3])


def main():
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import comune  # noqa: F401  (all'avvio riprende dal cloud i file dello studio, se il Mac li ha spostati su iCloud)
    except Exception:
        pass
    mia = json.load(open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))["version"]
    if da_cartella():
        print("DA CARTELLA")
        return
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
