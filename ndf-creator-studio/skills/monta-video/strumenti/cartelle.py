"""Dove stanno le cose dello studio sul computer di chi lo usa. Solo libreria standard: lo usano anche controllo.py
e aggiornamenti.py, che girano prima che il Python dello studio esista.

Due posti, e basta:
- il PROGRAMMA (la cartella del plugin): uguale per tutti, lo cambia ogni aggiornamento, qui non si scrive mai;
- la CASA dello studio: tutto quello che è di chi lo usa e tutto quello che lo studio si scarica (il suo Python,
  Node, ffmpeg, i modelli, le musiche, i suoni, i lavori, gli stili, le scelte). Un aggiornamento non la tocca.
  Mac:     ~/Library/Application Support/NDFCreatorStudio   (fuori da Documenti, quindi fuori da iCloud)
  Windows: %USERPROFILE%\\.NDFCreatorStudio                  (fuori da OneDrive e fuori da AppData: l'app Claude di
           Windows chiude in una sua cartella nascosta quello che i suoi comandi scrivono in AppData, e l'icona sul
           desktop, che parte fuori dall'app, non lo trovava; fino alla 0.2.5 era in %LOCALAPPDATA%\\NDFCreatorStudio)
  Il robot di prova la sposta con NDF_STUDIO_CASA (e i soli dati con NDF_STUDIO_DATI).
Le cartelle che il cliente vede (dove arrivano le clip e dove vanno i video finiti) sono scritte in CASA/config.json,
scelte al primo avvio: di serie "1 - Clip da montare" e "2 - Video finiti" in ~/NDF Creator Studio.
"""
import json
import os
import platform

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"
PROGRAMMA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # skills/monta-video


def _casa():
    if os.environ.get("NDF_STUDIO_CASA"):
        return os.path.abspath(os.path.expanduser(os.environ["NDF_STUDIO_CASA"]))
    if MAC:
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "NDFCreatorStudio")
    if WIN:
        return os.path.join(os.path.expanduser("~"), ".NDFCreatorStudio")
    return os.path.join(os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share"),
                        "NDFCreatorStudio")


CASA = _casa()
DATI = os.path.abspath(os.path.expanduser(os.environ.get("NDF_STUDIO_DATI") or os.path.join(CASA, "dati")))
VENV = os.path.join(CASA, "venv")
PY = os.path.join(VENV, "Scripts", "python.exe") if WIN else os.path.join(VENV, "bin", "python")
MODELLI = os.path.join(CASA, "modelli")
BIN = os.path.join(CASA, "bin")
PERCORSI = os.path.join(CASA, "percorsi.json")
PRONTO = os.path.join(CASA, "pronto.json")
CONFIG = os.path.join(CASA, "config.json")

# dove stava tutto fino alla 0.1.81: il passaggio (controllo.py) sposta da qui alla CASA
VECCHIA_CASA = os.path.join(os.path.expanduser("~"), ".studio-video")
VECCHI_DATI = os.path.join(os.path.expanduser("~"), "Documents", "NDFCreatorStudio")
# Windows, 0.2.0-0.2.5: la casa in AppData (vista dai comandi dell'app Claude; avvio.ps1 la sposta)
VECCHIA_CASA_WIN = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local"),
                                "NDFCreatorStudio")

CARTELLA_CLIENTE = os.path.join(os.path.expanduser("~"), "NDF Creator Studio")
CLIP_DI_SERIE = os.path.join(CARTELLA_CLIENTE, "1 - Clip da montare")
FINITI_DI_SERIE = os.path.join(CARTELLA_CLIENTE, "2 - Video finiti")


def leggi(percorso, ripiego=None):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {} if ripiego is None else ripiego


def scrivi(percorso, dati):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    tmp = percorso + ".nuovo"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=1, ensure_ascii=False)
    os.replace(tmp, percorso)


def config():
    return leggi(CONFIG)


def cartella_clip():
    return os.path.expanduser(config().get("clip") or CLIP_DI_SERIE)


def cartella_finiti():
    return os.path.expanduser(config().get("finiti") or FINITI_DI_SERIE)


def versione_programma():
    return leggi(os.path.join(os.path.dirname(os.path.dirname(PROGRAMMA)), ".claude-plugin", "plugin.json")).get("version", "")
