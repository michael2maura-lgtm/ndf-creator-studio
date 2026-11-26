"""Cose in comune a tutti i pezzi dello studio: dove stanno i programmi e i lavori."""
import json
import os
import shutil
import subprocess
import sys

# Il MOTORE (questa cartella) è uguale per tutti e si aggiorna. I DATI di chi lo usa (lavori, stili, suoni e clip
# scaricati) stanno in una cartella sua, che gli aggiornamenti non toccano mai.
STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cartelle import CASA, DATI, MODELLI, PERCORSI, cartella_clip, cartella_finiti  # noqa: E402,F401
VELOCITA = 1.05  # il reel finito va il 5% più veloce del girato (era 12%: clienti e Michael, 23/11/2026, "troppo veloce, sembra che tagli")
LAVORI = os.path.join(DATI, "lavori")
STRUMENTI_UTENTE = CASA
MODELLO_VOCE = "large-v3-turbo"   # trascrizione: il più preciso in italiano, veloce come il medium (dal 14/11/2026)
_BIN = os.path.join(STRUMENTI_UTENTE, "bin")
HYPERFRAMES = "hyperframes@0.8.34"

# dove stanno i programmi: li scrive installa.py (Mac e Windows); se manca il file, si cercano nel sistema
try:
    with open(PERCORSI, encoding="utf-8") as _f:
        _P = json.load(_f)
except (OSError, ValueError):
    _P = {}


def tieni_sul_mac(attesa=240):
    """Mac con Documenti su iCloud: quando il disco si riempie, il Mac toglie dal computer i file meno usati e lascia
    solo un segnaposto ("dataless"). Lo studio, leggendoli, resterebbe fermo ad aspettare (pagina che non si apre,
    montaggio bloccato). Qui li riprendiamo tutti prima di cominciare: un controllo di un decimo di secondo.
    Stampa ICLOUD ... solo se c'era qualcosa da fare; DISCO PIENO se lo spazio libero è sotto 8 GB."""
    # dalla 0.2 i dati stanno in Library/Application Support, che iCloud non tocca: serve solo a chi li ha ancora
    # in Documenti o sulla Scrivania (prima del passaggio)
    dentro_icloud = any(f"{os.sep}{c}{os.sep}" in DATI + os.sep for c in ("Documents", "Desktop"))
    if sys.platform != "darwin" or not dentro_icloud or not os.path.isdir(DATI) or os.environ.get("NDF_STUDIO_ICLOUD_FATTO"):
        return
    os.environ["NDF_STUDIO_ICLOUD_FATTO"] = "1"   # una volta sola per comando (anche per i pezzi che lancia)
    try:
        libero = shutil.disk_usage(DATI).free / 1e9
        if libero < 8:
            print(f"DISCO PIENO: liberi {libero:.0f} GB. Con il disco pieno il Mac sposta su iCloud i file dello studio "
                  "e i video ci mettono di più: conviene liberare spazio.", file=sys.stderr, flush=True)

        def nel_cloud():
            r = subprocess.run(["find", DATI, "-flags", "+dataless"], capture_output=True, text=True, timeout=60)
            return [p for p in r.stdout.splitlines() if p and os.path.isfile(p)]

        fuori = nel_cloud()
        if not fuori:
            return
        print(f"ICLOUD riprendo sul Mac {len(fuori)} file dello studio che erano solo su iCloud...", file=sys.stderr, flush=True)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(8) as pool:
            list(pool.map(lambda p: subprocess.run(["brctl", "download", p], capture_output=True, timeout=30), fuori))
        import time
        fine = time.time() + attesa
        while fuori and time.time() < fine:
            time.sleep(3)
            fuori = nel_cloud()
        if fuori:
            print(f"ICLOUD BLOCCATO: {len(fuori)} file dello studio sono ancora solo su iCloud (internet lento o disco "
                  "pieno). Nel Finder: Documenti, clic destro su NDFCreatorStudio, \"Mantieni scaricato\".",
                  file=sys.stderr, flush=True)
        else:
            print("ICLOUD OK: tutti i file dello studio sono di nuovo sul Mac.", file=sys.stderr, flush=True)
    except Exception:
        pass   # il controllo non deve mai fermare lo studio


tieni_sul_mac()


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
        nuovo["suoni"] = suoni
        if sc.get("transizione"):
            nuovo["transizione_scelta"] = sc["transizione"]
        if sc.get("diviso") == "fisso":   # schermo diviso: sempre in vista, niente stacchi a tutto schermo
            nuovo["stacchi"] = False
    elif sc.get("musica") == "nessuna" and "suoni" in stile:
        nuovo["suoni"] = {k: v for k, v in stile["suoni"].items() if k != "musica"}
    if sc.get("musica") not in (None, "", "nessuna", "modello") and os.path.exists(sc["musica"]) and "suoni" in nuovo:
        nuovo["suoni"] = dict(nuovo["suoni"], musica=sc["musica"])   # un brano scelto nella pagina: con qualsiasi stile
    nuovo["musica_scelta"] = sc.get("musica")   # None = la sceglie lo studio dal tono del video (musiche.py)
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
        if "pannello" in stile and acc.upper() != str(stile["pannello"].get("acc", "")).upper():
            nuovo["pannello_dal_brand"] = True   # brand diverso dai colori fatti a mano: tutto il pannello nel colore
        nuovo["accento_brand"] = acc   # grafica.py: anche il giallo di evidenza degli effetti diventa il colore del brand
    return nuovo


def stile_autonomo(cart):
    """Uno stile copiato fuori da STUDIO/stili (in DATI/stili): i file che lo stile pronto prende dalla copia unica
    ("../../font/X.ttf", "../../suoni/stili/x.mp3", ci/una_copia.py) si copiano dentro lo stile, e stile.json punta
    lì. Così lo stile del cliente funziona da solo, anche dopo un aggiornamento."""
    import re
    p = os.path.join(cart, "stile.json")
    with open(p, encoding="utf-8") as f:
        testo = f.read()
    for rel in set(re.findall(r'"(\.\./\.\./[^"]+)"', testo)):
        sotto = "font" if "/font/" in rel else "suoni"
        sorgente = os.path.normpath(os.path.join(STUDIO, "stili", "x", rel))
        if os.path.exists(sorgente):
            os.makedirs(os.path.join(cart, sotto), exist_ok=True)
            shutil.copy2(sorgente, os.path.join(cart, sotto, os.path.basename(rel)))
            testo = testo.replace(f'"{rel}"', f'"{sotto}/{os.path.basename(rel)}"')
    with open(p, "w", encoding="utf-8") as f:
        f.write(testo)


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


def riepilogo_scelte():
    """Una riga con quello che il cliente ha scelto nella pagina: stile, sottotitoli, effetti. Claude la scrive al
    cliente prima di montare, così se qualcosa non è quello che voleva lo vede subito (Michael, 23/11)."""
    try:
        sc = leggi(SCELTE)
    except (OSError, ValueError):
        sc = {}
    nome_stile = sc.get("stile") or "pulito"
    try:
        st = leggi(os.path.join(cartella_stile(nome_stile), "stile.json"))
    except SystemExit:
        st = {}
    stile = str(st.get("nome") or nome_stile).replace("Stile ", "")
    try:
        import sottotitoli
        k = sc.get("sottotitoli") or st.get("sottotitoli_nome")
        sott = sottotitoli.CATALOGO.get(k, {}).get("nome") if k else None
    except Exception:  # noqa: BLE001
        sott = None
    try:
        import effetti
        eff = [effetti.CATALOGO[k]["nome"] for k in (sc.get("effetti") or []) if k in effetti.CATALOGO and k != "zoom"]
    except Exception:  # noqa: BLE001
        eff = []
    pezzi = [f"stile {stile}" + ("" if sc.get("stile") else " (nella pagina non è salvato nessuno stile: uso Pulito)")]
    if sott:
        pezzi.append(f"sottotitoli {sott}")
    pezzi.append(f"{len(eff)} effetti: {', '.join(eff)}" if eff else "nessun effetto acceso")
    m = sc.get("musica")
    pezzi.append("musica: " + ("nessuna" if m == "nessuna" else "quella del modello" if m == "modello" else
                               "dal tono del video (musiche.py scegli)" if not m else os.path.basename(str(m))))
    return "SCELTE DEL CLIENTE: " + "; ".join(pezzi)


def _tocca(a, b):
    """True se i riquadri [x0, y0, x1, y1] a e b si sovrappongono."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def mani_sulla_faccia(c):
    """True se nel campione c di faccia.json una mano passa davanti alla faccia (con un po' di margine)."""
    if "y" not in c:
        return False
    m = 0.15 * c["l"]
    faccia = [c["x"] - m, c["y"] - m, c["x"] + c["l"] + m, c["y"] + c["h"] + m]
    return any(_tocca(faccia, r) for r in c.get("mani", []))


def senza_mani(faccia, t, raggio=0.6):
    """Il secondo più vicino a t (entro raggio) in cui nessuna mano copre la faccia: per fermi immagine, adesivi e
    copertine. Se non c'è, o se faccia.json non ha le mani, torna t."""
    camp = [c for c in faccia.get("campioni", []) if abs(c["t"] - t) <= raggio and "mani" in c and "y" in c]
    puliti = [c for c in camp if not mani_sulla_faccia(c)]
    return min(puliti, key=lambda c: abs(c["t"] - t))["t"] if puliti else t


def mani_nella_fascia(faccia, da, a, y0, y1):
    """Quanta parte del tempo da-a (0-1) le mani stanno nella fascia orizzontale y0-y1 (es. il petto, dove vanno i
    titoli). None se faccia.json non ha le mani."""
    camp = [c for c in faccia.get("campioni", []) if da <= c["t"] <= a and "mani" in c]
    if not camp:
        return None
    fascia = [0, y0, 1080, y1]
    return sum(1 for c in camp if any(_tocca(fascia, r) for r in c["mani"])) / len(camp)
