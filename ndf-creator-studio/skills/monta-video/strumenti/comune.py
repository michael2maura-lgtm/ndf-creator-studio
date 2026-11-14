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
MODELLO_VOCE = "large-v3-turbo"   # trascrizione: il più preciso in italiano, veloce come il medium (dal 14/11/2026)
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
    """Lo stile con dentro le scelte della pagina "Scegli il tuo stile" (DATI/scelte.json).
    Il look del cliente vale per QUALSIASI stile: colore del brand (anche da DATI/profilo.json), colore del video,
    sottotitoli, font e lettere di titoli e sottotitoli (ritocchi.py), testo fisso, velocità, effetti accesi.
    Suoni, musica e transizione valgono solo per lo stile scelto nella pagina.
    I sottotitoli scelti finiscono in stile["sottotitoli_scelti"] (un nome di sottotitoli.CATALOGO)."""
    try:
        sc = leggi(SCELTE)
    except (OSError, ValueError):
        sc = {}
    try:
        profilo = leggi(os.path.join(DATI, "profilo.json"))
    except (OSError, ValueError):
        profilo = {}
    nuovo = dict(stile)
    if sc.get("stile") and sc.get("stile") == nome_stile:   # solo per lo stile scelto: suoni, musica, transizione
        suoni = dict(stile.get("suoni", {}))
        suoni.update({k: v for k, v in sc.get("suoni", {}).items() if v == "" or os.path.exists(v)})  # "" = nessun suono
        if sc.get("musica") == "nessuna":
            suoni.pop("musica", None)
        elif sc.get("musica") and os.path.exists(sc["musica"]):
            suoni["musica"] = sc["musica"]
        nuovo["suoni"] = suoni
        if sc.get("transizione"):
            nuovo["transizione_scelta"] = sc["transizione"]
        if sc.get("diviso") == "fisso":   # schermo diviso: sempre in vista, niente stacchi a tutto schermo
            nuovo["stacchi"] = False
    elif sc.get("musica") == "nessuna" and "suoni" in stile:
        nuovo["suoni"] = {k: v for k, v in stile["suoni"].items() if k != "musica"}
    if sc.get("sottotitoli"):
        nuovo["sottotitoli_scelti"] = sc["sottotitoli"]
    if sc.get("colore"):
        nuovo["colore_scelto"] = sc["colore"]
    if sc.get("velocita"):
        nuovo["velocita"] = sc["velocita"]
    if sc.get("effetti") is not None:  # None = quelli dello stile; [] = nessuno (li piazza Claude dove servono)
        nuovo["effetti_scelti"] = sc["effetti"]
    if sc.get("sott"):
        nuovo["ritocchi_sott"] = sc["sott"]
    if sc.get("titoli"):
        nuovo["ritocchi_titoli"] = sc["titoli"]
        if "font" in stile:
            import ritocchi
            nuovo = ritocchi.font_titoli(nuovo, sc["titoli"])
    if sc.get("testo_fisso"):
        nuovo["testo_fisso"] = sc["testo_fisso"]
        nuovo["fisso"] = sc.get("fisso") or {}
    acc = sc.get("accento") or profilo.get("colore")
    if acc and len(acc) == 7 and "colori" in stile:   # il colore del brand: su titoli, parole in evidenza ed effetti
        rgb = [int(acc[i:i + 2], 16) for i in (1, 3, 5)]
        luce = "#" + "".join(f"{min(255, round(v + (255 - v) * 0.3)):02X}" for v in rgb)
        nuovo["colori"] = dict(stile.get("colori", {}), accento=acc, accento_luce=luce)
        nuovo["pannello"] = dict(stile.get("pannello", {}), acc=acc, acc_rgb=",".join(map(str, rgb)))
        nuovo["accento_brand"] = acc   # grafica.py: anche il giallo di evidenza degli effetti diventa il colore del brand
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


def nomi_con_il_profilo(nomi=""):
    """I nomi detti nel video più le parole speciali del cliente (DATI/profilo.json "parole" e il suo nome):
    così chi ascolta il video non li sbaglia, senza doverli ripetere ogni volta."""
    try:
        with open(os.path.join(DATI, "profilo.json"), encoding="utf-8") as f:
            parole = json.load(f).get("parole") or []
    except (OSError, ValueError):
        parole = []
    tutti = [x.strip() for x in (nomi or "").split(",") if x.strip()]
    tutti += [x for x in parole if x.lower() not in [t.lower() for t in tutti]]
    return ", ".join(tutti)


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
