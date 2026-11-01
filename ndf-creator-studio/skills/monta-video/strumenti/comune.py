"""Cose in comune a tutti i pezzi dello studio: dove stanno i programmi e i lavori."""
import json
import os
import shutil
import subprocess
import sys

# Il MOTORE (questa cartella) è uguale per tutti e si aggiorna. I DATI di chi lo usa (lavori, stili, suoni e clip
# scaricati) stanno in una cartella sua, che gli aggiornamenti non toccano mai.
STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.expanduser(os.environ.get("NDF_STUDIO_DATI", os.path.join("~", "Documents", "NDFCreatorStudio")))
VELOCITA = 1.12  # il reel finito va il 12% più veloce del girato: ritmo più svelto, voce naturale
LAVORI = os.path.join(DATI, "lavori")
STRUMENTI_UTENTE = os.path.join(os.path.expanduser("~"), ".studio-video")
MODELLI = os.path.join(STRUMENTI_UTENTE, "modelli")
_BIN = os.path.join(STRUMENTI_UTENTE, "bin")
HYPERFRAMES = "hyperframes@0.8.34"

# dove stanno i programmi: li scrive installa.py (Mac e Windows); se manca il file, si cercano nel sistema
try:
    with open(os.path.join(STRUMENTI_UTENTE, "percorsi.json"), encoding="utf-8") as _f:
        _P = json.load(_f)
except (OSError, ValueError):
    _P = {}


def _primo(*candidati, ripiego):
    return next((p for p in candidati if p and os.path.exists(p)), ripiego)


FFMPEG = _primo(_P.get("ffmpeg"), os.path.join(_BIN, "ffmpeg"), shutil.which("ffmpeg"), "/opt/homebrew/bin/ffmpeg", ripiego="ffmpeg")
FFPROBE = _primo(_P.get("ffprobe"), os.path.join(_BIN, "ffprobe"), shutil.which("ffprobe"), "/opt/homebrew/bin/ffprobe", ripiego="ffprobe")
NPX = _primo(_P.get("npx"), os.path.join(_BIN, "npx"), shutil.which("npx"), ripiego="npx")


def env_node():
    """PATH con Node e ffmpeg dello studio davanti: npx deve trovare node, e HyperFrames deve trovare ffmpeg."""
    cartelle = [_P.get("node_dir") or os.path.dirname(os.path.realpath(NPX)), os.path.dirname(FFMPEG), _BIN]
    return dict(os.environ, PATH=os.pathsep.join([c for c in cartelle if c] + [os.environ.get("PATH", "")]))


def cartella_stile(nome):
    """Prima lo stile dell'utente (DATI/stili), poi quelli pronti che arrivano con il motore (STUDIO/stili)."""
    for base in (DATI, STUDIO):
        c = os.path.join(base, "stili", nome)
        if os.path.isdir(c):
            return c
    sys.exit(f"Non trovo lo stile '{nome}'.")


SCELTE = os.path.join(DATI, "scelte.json")  # quello che l'utente ha scelto nella pagina "Scegli il tuo look" (scegli.py)


def con_le_scelte(nome_stile, stile):
    """Lo stile con dentro i sottotitoli, i suoni e la musica scelti nella pagina, se li ha scelti per questo stile.
    I sottotitoli scelti finiscono in stile["sottotitoli_scelti"] (un nome di sottotitoli.CATALOGO).
    I suoni scelti sono percorsi interi: os.path.join(cartella_stile, percorso intero) dà il percorso intero."""
    try:
        sc = leggi(SCELTE)
    except (OSError, ValueError):
        return stile
    if sc.get("stile") != nome_stile:
        return stile
    suoni = dict(stile.get("suoni", {}))
    suoni.update({k: v for k, v in sc.get("suoni", {}).items() if v == "" or os.path.exists(v)})  # "" = nessun suono
    if sc.get("musica") == "nessuna":
        suoni.pop("musica", None)
    elif sc.get("musica") and os.path.exists(sc["musica"]):
        suoni["musica"] = sc["musica"]
    nuovo = dict(stile, suoni=suoni)
    if sc.get("sottotitoli"):
        nuovo["sottotitoli_scelti"] = sc["sottotitoli"]
    if sc.get("colore"):
        nuovo["colore_scelto"] = sc["colore"]
    if sc.get("transizione"):
        nuovo["transizione_scelta"] = sc["transizione"]
    if sc.get("velocita"):
        nuovo["velocita"] = sc["velocita"]
    if sc.get("diviso") == "fisso":   # schermo diviso: sempre in vista, niente stacchi a tutto schermo
        nuovo["stacchi"] = False
    if sc.get("effetti") is not None:  # None = quelli dello stile; [] = nessuno
        nuovo["effetti_scelti"] = sc["effetti"]
    return nuovo


def girato(cart):
    """Il video su cui si monta: quello con il colore (colore.py) se c'è, se no il tagliato."""
    c = os.path.join(cart, "tagliato-colore.mp4")
    if os.path.exists(c) and os.path.exists(os.path.join(cart, "colore.json")) \
            and os.path.getmtime(c) > os.path.getmtime(os.path.join(cart, "tagliato.mp4")):
        return c
    return os.path.join(cart, "tagliato.mp4")


def trova(rel, cartella="suoni"):
    """Un file di suoni o clip: prima nei dati dell'utente (scaricati all'installazione), poi nel motore."""
    for base in (DATI, STUDIO):
        p = os.path.join(base, cartella, rel)
        if os.path.exists(p):
            return p
    sys.exit(f"Non trovo {cartella}/{rel}. Rilancia l'installazione dello studio.")


def cartella_lavoro(nome, crea=False):
    c = os.path.join(LAVORI, nome)
    if crea:
        os.makedirs(c, exist_ok=True)
    elif not os.path.isdir(c):
        sys.exit(f"Non trovo il lavoro '{nome}'. Prima lancia prepara.py.")
    return c


def esegui(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Errore:\n" + (r.stderr or r.stdout)[-2000:])
    return r


def leggi(percorso):
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


def scrivi(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=1)


def codec_video():
    """Sul Mac usa il chip video (veloce), altrimenti il codificatore standard."""
    enc = subprocess.run([FFMPEG, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    if "h264_videotoolbox" in enc:
        return ["-c:v", "h264_videotoolbox", "-b:v", "16M", "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p"]


def durata(video):
    out = esegui([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]).stdout
    return float(out.strip())
