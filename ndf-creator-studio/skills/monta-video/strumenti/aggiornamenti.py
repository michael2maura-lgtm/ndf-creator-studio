"""Aggiornamenti dello studio: c'è una versione nuova? Con il sì del cliente la installa da solo.

Uso:  PY strumenti/aggiornamenti.py              il controllo (lo fa già da solo controllo.py, una volta al giorno)
      PY strumenti/aggiornamenti.py --installa   installa la versione nuova (il cliente ha detto sì, o "aggiorna lo studio")

Il cliente non apre mai un terminale: il comando dei plugin lo lancia questo programma, anche sui computer che hanno solo
l'app Claude (usa quello che c'è dentro l'app). Lavori, stili e scelte stanno nella casa dello studio (cartelle.py) e un
aggiornamento non li tocca. Ogni versione ha una riga di novità in novita.json (cartella principale del progetto).

Righe del controllo:
    STATO aggiornamento: NESSUNO (0.2.0 è l'ultima)
    STATO aggiornamento: DISPONIBILE 0.2.0 -> 0.2.1 · novità: <una riga>     chiedi se aggiornare
    STATO aggiornamento: GIA SCARICATO 0.2.1 (stai usando 0.2.0) · di' al cliente: <come riaprire>
    STATO aggiornamento: DA CARTELLA · ...                                     installato da una cartella
Righe di --installa (l'ultima è sempre DI': la frase da dire al cliente, parola per parola):
    FATTO 0.2.0 -> 0.2.1  /  GIA SCARICATO 0.2.1  /  RIPARATO 0.2.1  /  SENZA COMANDO  /  NON RIUSCITO <perché>
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.dirname(os.path.dirname(QUI))
CONFIG = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
PLUGINS = os.path.join(CONFIG, "plugins")
NOME = "ndf-creator-studio"
ID = f"{NOME}@{NOME}"
GITHUB = "michael2maura-lgtm/ndf-creator-studio"
ULTIMA_URL = f"https://raw.githubusercontent.com/{GITHUB}/main/{NOME}/.claude-plugin/plugin.json"

if sys.platform == "win32":
    CHIUDI = ("chiudi del tutto l'app Claude (tasto destro sull'icona di Claude vicino all'orologio, poi Esci), "
              "riaprila e apri una nuova sessione in Code")
else:
    CHIUDI = ("chiudi del tutto l'app Claude (con l'app davanti premi Cmd+Q: chiudere la finestra non basta), "
              "riaprila e apri una nuova sessione in Code")


def numeri(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:3])


def leggi(percorso):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def mia():
    """La versione che sta girando adesso."""
    return leggi(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")).get("version", "")


def scaricata():
    """La versione che l'app caricherà alla prossima apertura (può essere più nuova di quella che gira)."""
    voci = leggi(os.path.join(PLUGINS, "installed_plugins.json")).get("plugins", {}).get(ID) or []
    versioni = [v.get("version", "") for v in voci if v.get("version")]
    return max(versioni, key=numeri) if versioni else ""


def ultima():
    """La versione su GitHub, o None se non c'è internet."""
    try:
        with urllib.request.urlopen(ULTIMA_URL, timeout=8) as r:
            return json.loads(r.read().decode("utf-8"))["version"]
    except Exception:
        pass
    negozio = os.path.join(PLUGINS, "marketplaces", NOME)
    if shutil.which("git") and os.path.isdir(os.path.join(negozio, ".git")):
        try:
            subprocess.run(["git", "-C", negozio, "fetch", "--quiet"], timeout=20, capture_output=True)
            r = subprocess.run(["git", "-C", negozio, "show", f"origin/HEAD:{NOME}/.claude-plugin/plugin.json"],
                               capture_output=True, text=True, timeout=10)
            return json.loads(r.stdout)["version"]
        except Exception:
            pass
    return None


def da_cartella():
    """True se lo studio non arriva da GitHub: marketplace aggiunto da una cartella, o studio caricato fuori dai plugin."""
    m = leggi(os.path.join(PLUGINS, "known_marketplaces.json")).get(NOME)
    if m:
        f = m.get("source", {})
        dove = f.get("url", "") + f.get("repo", "")
        if f.get("source") in ("directory", "file") or (dove and GITHUB not in dove):
            return True
    return PLUGINS not in os.path.realpath(PLUGIN)


def comando_claude():
    """Il comando dei plugin: quello installato, o quello dentro l'app Claude (chi ha solo l'app)."""
    trovati = []
    if shutil.which("claude"):
        return shutil.which("claude")
    for p in ("~/.local/bin/claude", "~/.claude/local/claude"):
        if os.path.isfile(os.path.expanduser(p)):
            return os.path.expanduser(p)
    if sys.platform == "darwin":
        trovati = glob.glob(os.path.expanduser(
            "~/Library/Application Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude"))
    elif sys.platform == "win32":
        for base in (os.environ.get("APPDATA"), os.environ.get("LOCALAPPDATA")):
            if base:
                trovati += glob.glob(os.path.join(base, "Claude", "claude-code", "**", "claude.exe"), recursive=True)
    trovati = [t for t in trovati if os.path.isfile(t)]
    if not trovati:
        return None
    return max(trovati, key=lambda t: numeri((re.findall(r"claude-code[\\/]([\d.]+)", t) or [""])[0]))


def lancia(cmd, *args):
    # Con un wifi lento lo scaricamento da GitHub dura più dei 2 minuti che l'app aspetta di serie: qui si aspetta 15 minuti.
    env = dict(os.environ, CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS="900000")
    try:
        r = subprocess.run([cmd, "plugin", *args], capture_output=True, text=True, timeout=1000, env=env)
        return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    except Exception as e:
        return False, [str(e)]


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cartelle  # noqa: E402

NOVITA_URL = f"https://raw.githubusercontent.com/{GITHUB}/main/novita.json"
RICORDO = os.path.join(cartelle.CASA, "aggiornamento.json")


def novita(versione):
    """La riga di novità della versione nuova (novita.json nella cartella principale del progetto su GitHub)."""
    try:
        with urllib.request.urlopen(NOVITA_URL, timeout=8) as r:
            return json.loads(r.read().decode("utf-8")).get(versione, "")
    except Exception:
        return ""


def riga():
    """Una riga STATO aggiornamento, o None senza internet. Non scrive niente."""
    if da_cartella():
        return "STATO aggiornamento: DA CARTELLA · con il sì del cliente: PY strumenti/aggiornamenti.py --installa"
    gira, pronta = mia(), scaricata()
    if pronta and numeri(pronta) > numeri(gira):
        return f"STATO aggiornamento: GIA SCARICATO {pronta} (stai usando {gira}) · di' al cliente: {CHIUDI}"
    nuova = ultima()
    if nuova is None:
        return None
    if numeri(nuova) <= numeri(gira):
        return f"STATO aggiornamento: NESSUNO ({gira} è l'ultima)"
    cosa = novita(nuova)
    return f"STATO aggiornamento: DISPONIBILE {gira} -> {nuova}" + (f" · novità: {cosa}" if cosa else "")


def una_volta_al_giorno():
    """Per il controllo di ogni chat: chiede a GitHub al massimo una volta al giorno; le altre volte ripete la risposta
    di oggi solo se c'è qualcosa da dire (una versione nuova), se no niente."""
    import datetime
    oggi = datetime.date.today().isoformat()
    r = cartelle.leggi(RICORDO)
    if r.get("giorno") == oggi and r.get("versione") == mia():
        detta = r.get("riga") or ""
        return None if "NESSUNO" in detta else (detta or None)
    detta = riga()
    if detta is not None:
        cartelle.scrivi(RICORDO, {"giorno": oggi, "versione": mia(), "riga": detta})
    return detta


def installa():
    gira = mia()
    cmd = comando_claude()
    if not cmd:
        print("SENZA COMANDO")
        print(f"DI': L'app Claude scarica da sola la versione nuova: {CHIUDI}. "
              f"Se dopo non è cambiato niente, riprova tra qualche minuto.")
        return
    if da_cartella():
        lancia(cmd, "marketplace", "remove", NOME)
        ok, ultima_riga = lancia(cmd, "marketplace", "add", GITHUB)
        if ok:
            ok, ultima_riga = lancia(cmd, "install", ID)
        pronta = scaricata()
        if ok and pronta:
            print(f"RIPARATO {pronta}")
            print(f"DI': Ho sistemato lo studio, d'ora in poi gli aggiornamenti arrivano. Adesso {CHIUDI}.")
        else:
            print(f"NON RIUSCITO {ultima_riga[0]}")
            print("DI': Non sono riuscito a sistemare lo studio da qui. Controlla internet e riprova tra poco; "
                  "se non va, scrivi all'assistenza.")
        return
    prima = scaricata()
    lancia(cmd, "marketplace", "update", NOME)
    ok, ultima_riga = lancia(cmd, "update", ID)
    dopo = scaricata()
    nuova = ultima()
    if dopo and numeri(dopo) > numeri(gira):
        if prima and numeri(prima) >= numeri(dopo):
            print(f"GIA SCARICATO {dopo}")
        else:
            print(f"FATTO {gira} -> {dopo}")
        print(f"DI': Aggiornato alla versione {dopo}. Adesso {CHIUDI}.")
    elif nuova and dopo and numeri(dopo) >= numeri(nuova):
        print(f"AGGIORNATO {gira}")
        print("DI': Lo studio è già all'ultima versione.")
    else:
        print(f"NON RIUSCITO {ultima_riga[0] if not ok else 'versione non arrivata'}")
        print("DI': L'aggiornamento non è arrivato. Controlla internet e riprova tra qualche minuto.")


def main():
    if "--installa" in sys.argv:
        installa()
    else:
        print(riga() or "STATO aggiornamento: NON CONTROLLATO (niente internet: si va avanti)")


if __name__ == "__main__":
    main()
