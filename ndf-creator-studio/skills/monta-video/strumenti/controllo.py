"""Il controllo dello studio: la prima volta installa, poi a ogni chat controlla in silenzio e ripara da solo quello che
manca. Lo lancia SEMPRE il programma di avvio (avvio.sh sul Mac, avvio.ps1 su Windows), con il Python dello studio.
Solo libreria standard: gira prima che l'ambiente dello studio esista.

Uso:  sh strumenti/avvio.sh                 (Mac)       controllo e riparazione, pochi secondi quando c'è tutto
      powershell ... strumenti/avvio.ps1    (Windows)
      opzioni:  --senza-aggiornamenti   non chiede a GitHub se c'è una versione nuova (il robot di prova)

Cosa controlla, in quest'ordine, e ripara se manca (tutto nella CASA dello studio, vedi cartelle.py):
  passaggio   chi aveva lo studio di prima (~/.studio-video, Documenti/NDFCreatorStudio): sposta modelli e lavori
  ambiente    il Python dello studio con i pacchetti a versione fissa (pip, circa 0,4 GB la prima volta)
  ffmpeg      il suo ffmpeg (dentro l'ambiente, pacchetto static-ffmpeg)
  Node        il suo Node 22, controllato con l'impronta SHA-256 di nodejs.org
  suoni       i suoni gratuiti (da-scaricare.json)
  musiche     le musiche libere (una sola copia, nella CASA)
  icona       l'icona "NDF Creator Studio" sulla Scrivania
  cartelle    le due cartelle del cliente (solo dopo il primo avvio, quando config.json c'è)
  pezzi grandi  voce, resa, ritaglio: li scarica scarica.py (in sottofondo); qui si dice solo se ci sono
  aggiornamento una volta al giorno: c'è una versione nuova? (aggiornamenti.py)

Righe (una per pezzo):  STATO <pezzo>: OK  /  STATO <pezzo>: MANCA · <cosa fare su questo computer>
Righe speciali:  STATO primo avvio: DA FARE      (config.json non c'è: le due domande e lo stile, SKILL.md)
                 STATO pezzi grandi: DA SCARICARE / IN CORSO / OK
                 STATO aggiornamento: DISPONIBILE <versione> · <novità>
Ultima riga: PRONTO (si può montare) o NON PRONTO (manca qualcosa senza cui non si monta).
Scrive percorsi.json (dove stanno python, ffmpeg, Node: lo leggono tutti gli strumenti) e pronto.json.
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile

sys.dont_write_bytecode = True
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import cartelle  # noqa: E402
from cartelle import CASA, DATI, PY, VENV, WIN  # noqa: E402

for _s in (sys.stdout, sys.stderr):     # Windows: la console è cp1252, le righe hanno lettere accentate
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# I REQUISITI: il numero si alza di 1 ogni volta che il controllo installa qualcosa di nuovo o di diverso. Serve a
# chi viene da una versione vecchia: controllo e scarica.py rifanno i pezzi interessati. Storia: 1 = fino alla 0.1.80;
# 2 = la casa nuova, Python e Node propri con l'impronta, pacchetti a versione fissa.
REQUISITI = 2

# Le versioni sono fisse: le stesse provate dal robot. Un pacchetto nuovo che rompe le cose non arriva da solo.
PACCHETTI = ["faster-whisper==1.2.1", "ctranslate2==4.8.3", "mediapipe==1.1.1", "opencv-python-headless==5.0.0.93",
             "Pillow==13.0.0", "numpy==2.5.4", "scipy==1.18.1", "av==16.1.0", "onnxruntime==1.31.0",
             "static-ffmpeg==3.0", "yt-dlp>=2026.11.23"]   # yt-dlp si aggiorna da solo (prendi_esempio.py)

# I Mac Intel: mediapipe e onnxruntime non escono più per loro, le ultime versioni che ci sono (trovato dal robot sul
# Mac Intel di GitHub, 27/11/2026: con le versioni di sopra l'installazione si fermava)
if cartelle.MAC and platform.machine().lower() in ("x86_64", "amd64"):
    PACCHETTI = [{"mediapipe": "mediapipe==0.10.14", "onnxruntime": "onnxruntime==1.23.2"}.get(p.split("=")[0], p)
                 for p in PACCHETTI]

NODE = "v22.11.0"
NODE_IMPRONTE = {
    "darwin-arm64.tar.gz": "2e89afe6f4e3aa6c7e21c560d8a0453d84807e97850bbb819b998531a22bdfde",
    "darwin-x64.tar.gz": "668d30b9512137b5f5baeef6c1bb4c46efff9a761ba990a034fb6b28b9da2465",
    "win-x64.zip": "905373a059aecaf7f48c1ce10ffbd5334457ca00f678747f19db5ea7d256c236",
}

percorsi = cartelle.leggi(cartelle.PERCORSI)
percorsi["python"] = PY
MANCANTI = []
GRAVI = []   # senza questi non si monta: NON PRONTO
INTERNET = "controlla che internet funzioni, poi scrivi di nuovo \"installa lo studio\""


def stato(cosa, ok, nota="", grave=True):
    if not ok:
        MANCANTI.append(cosa)
        if grave:
            GRAVI.append(cosa)
    print(f"STATO {cosa}: {'OK' if ok else 'MANCA'}{' · ' + nota if nota else ''}", flush=True)


def gira(cmd, timeout=3600, **kw):
    kw.setdefault("env", dict(os.environ, PYTHONIOENCODING="utf-8"))
    try:
        return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, **kw)
    except (OSError, subprocess.SubprocessError) as e:
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


def scarica(url, dest, impronta=None, prove=3):
    """Scarica con 3 prove; con l'impronta controlla il file e, se non è quello giusto, lo butta."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".parziale"
    for prova in range(1, prove + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
            if impronta:
                h = hashlib.sha256()
                with open(tmp, "rb") as f:
                    for blocco in iter(lambda: f.read(1 << 20), b""):
                        h.update(blocco)
                if h.hexdigest() != impronta:
                    os.remove(tmp)
                    raise ValueError("impronta diversa: il file non è quello giusto")
            os.replace(tmp, dest)
            return True
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            if prova == prove:
                print(f"  (download non riuscito: {type(e).__name__} {str(e)[:80]})", flush=True)
                return False
            print(f"  il download si è fermato, riprovo ({prova + 1} di {prove})", flush=True)
            time.sleep(3)


# ---------------------------------------------------------------- il passaggio da com'era fino alla 0.1.81
def passaggio():
    """Chi aveva lo studio di prima: i modelli (circa 3 GB) da ~/.studio-video e i lavori, gli stili, il brand da
    Documenti/NDFCreatorStudio vengono spostati nella casa nuova. Si sposta, non si copia: niente spazio in più.
    La vecchia cartella resta con un LEGGIMI che dice dov'è andato tutto. Una volta sola."""
    if os.environ.get("NDF_STUDIO_CASA") and not os.environ.get("NDF_STUDIO_PROVA_PASSAGGIO"):
        return   # il robot: la sua casa finta non pesca da quella vera
    segno = os.path.join(CASA, "passaggio-fatto.txt")
    if os.path.exists(segno):
        return
    vecchia_casa = os.environ.get("NDF_STUDIO_VECCHIA_CASA") or cartelle.VECCHIA_CASA
    vecchi_dati = os.environ.get("NDF_STUDIO_VECCHI_DATI") or cartelle.VECCHI_DATI
    spostati = []
    os.makedirs(CASA, exist_ok=True)
    da = os.path.join(vecchia_casa, "modelli")
    if os.path.isdir(da) and not os.path.isdir(cartelle.MODELLI):
        try:
            shutil.move(da, cartelle.MODELLI)
            spostati.append("modelli")
        except OSError:
            pass
    if os.path.isdir(vecchi_dati) and os.path.realpath(vecchi_dati) != os.path.realpath(DATI):
        try:   # sul Mac i file finiti solo su iCloud vanno ripresi prima di spostarli
            if cartelle.MAC:
                subprocess.run(["brctl", "download", vecchi_dati], capture_output=True, timeout=60)
        except Exception:
            pass
        os.makedirs(DATI, exist_ok=True)
        for nome in os.listdir(vecchi_dati):
            sorgente, meta = os.path.join(vecchi_dati, nome), os.path.join(DATI, nome)
            if nome.startswith(".") or nome == "LEGGIMI.txt":
                continue
            try:
                if not os.path.exists(meta):
                    shutil.move(sorgente, meta)
                elif os.path.isdir(sorgente) and os.path.isdir(meta):
                    for sotto in os.listdir(sorgente):   # due cartelle uguali (lavori, stili): si uniscono
                        if not os.path.exists(os.path.join(meta, sotto)):
                            shutil.move(os.path.join(sorgente, sotto), os.path.join(meta, sotto))
                spostati.append(nome)
            except OSError:
                pass
        try:
            with open(os.path.join(vecchi_dati, "LEGGIMI.txt"), "w", encoding="utf-8") as f:
                f.write(f"Dalla versione 0.2 lo studio tiene i suoi file qui:\n{DATI}\n"
                        "Puoi cancellare questa cartella quando vuoi.\n")
        except OSError:
            pass
    if spostati:
        print(f"STATO passaggio alla casa nuova: OK · spostati {', '.join(spostati)}", flush=True)
    with open(segno, "w", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M") + " " + ", ".join(spostati) + "\n")


# ---------------------------------------------------------------- i programmi
def python_base():
    """Il Python proprio dello studio (scaricato da avvio.sh / avvio.ps1), quello da cui nasce l'ambiente."""
    proprio = os.path.join(CASA, "python", "python.exe" if WIN else os.path.join("bin", "python3"))
    if os.path.exists(proprio):
        return proprio
    return getattr(sys, "_base_executable", None) or sys.executable


def pacchetti_giusti():
    """Controllo veloce (meno di un secondo): l'ambiente c'è e ha i pacchetti alle versioni giuste."""
    if not os.path.exists(PY):
        return False
    prova = ("import importlib.metadata as m, sys\n"
             "for r in sys.argv[1:]:\n"
             "    n, v = r.replace('>=', '==').split('==')\n"
             "    assert m.version(n) == v or '>=' in r, r\n")
    return gira([PY, "-c", prova, *PACCHETTI], timeout=60).returncode == 0


def ambiente():
    if pacchetti_giusti():
        stato("ambiente dello studio", True)
        return
    print("STATO ambiente dello studio: lo preparo (circa 0,4 GB, qualche minuto la prima volta)", flush=True)
    if not os.path.exists(PY) or gira([PY, "-c", "import sys"], timeout=60).returncode != 0:
        if os.path.exists(VENV):
            shutil.rmtree(VENV, ignore_errors=True)
        r = gira([python_base(), "-m", "venv", VENV], timeout=600)
        if r.returncode != 0:
            stato("ambiente dello studio", False, "non riesco a creare l'ambiente: " + (r.stderr or "")[-120:].strip())
            return
    pip = [PY, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", "--quiet"]
    r = None
    for prova in range(3):   # il download dei pacchetti a volte si interrompe
        r = gira([*pip, *PACCHETTI], timeout=3600)
        if r.returncode == 0:
            break
        print(f"  i pacchetti non sono arrivati tutti, riprovo ({prova + 2} di 3)", flush=True)
    ok = pacchetti_giusti()
    stato("ambiente dello studio", ok, "" if ok else INTERNET + " · " + (r.stderr or r.stdout or "")[-160:].strip())


def ffmpeg():
    ff = percorsi.get("ffmpeg")
    if ff and os.path.exists(ff) and VENV in ff:
        stato("ffmpeg", True)
        return
    for _ in range(3):   # static-ffmpeg scarica i programmi la prima volta: a volte si interrompe
        r = gira([PY, "-c", "import json; from static_ffmpeg import run; "
                            "print(json.dumps(run.get_or_fetch_platform_executables_else_raise()))"], timeout=900)
        try:
            percorsi["ffmpeg"], percorsi["ffprobe"] = json.loads(r.stdout.strip().splitlines()[-1])
            break
        except Exception:
            continue
    stato("ffmpeg", os.path.exists(percorsi.get("ffmpeg") or ""), "" if percorsi.get("ffmpeg") else INTERNET)


def node():
    cart = os.path.join(CASA, "node")
    exe = os.path.join(cart, "node.exe") if WIN else os.path.join(cart, "bin", "node")
    if not (os.path.exists(exe) and gira([exe, "--version"], timeout=30).stdout.startswith(NODE)):
        arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") and not WIN else "x64"
        coda = "win-x64.zip" if WIN else f"darwin-{arch}.tar.gz"
        nome = f"node-{NODE}-{coda}"
        archivio = os.path.join(CASA, nome)
        print("STATO Node: lo scarico (circa 45 MB, una volta sola)", flush=True)
        if scarica(f"https://nodejs.org/dist/{NODE}/{nome}", archivio, NODE_IMPRONTE[coda]):
            nuovo = os.path.join(CASA, "node.nuovo")
            shutil.rmtree(nuovo, ignore_errors=True)
            if WIN:
                with zipfile.ZipFile(archivio) as z:
                    z.extractall(nuovo)
            else:
                with tarfile.open(archivio) as t:
                    t.extractall(nuovo, **({"filter": "tar"} if hasattr(tarfile, "data_filter") else {}))
            os.remove(archivio)
            shutil.rmtree(cart, ignore_errors=True)
            os.rename(os.path.join(nuovo, nome[:-len(".zip" if WIN else ".tar.gz")]), cart)
            shutil.rmtree(nuovo, ignore_errors=True)
    bin_dir = cart if WIN else os.path.join(cart, "bin")
    percorsi["node_dir"] = bin_dir
    percorsi["npx"] = os.path.join(bin_dir, "npx.cmd" if WIN else "npx")
    ok = os.path.exists(exe) and gira([exe, "--version"], timeout=30).returncode == 0
    stato("Node", ok, "" if ok else INTERNET)


def salva_percorsi():
    cartelle.scrivi(cartelle.PERCORSI, percorsi)


# ---------------------------------------------------------------- suoni, musiche, icona, cartelle
def suoni():
    elenco = cartelle.leggi(os.path.join(cartelle.PROGRAMMA, "suoni", "da-scaricare.json"))
    mancanti = {rel: url for rel, url in elenco.items()
                if not os.path.exists(os.path.join(DATI, "suoni", *rel.split("/")))}
    falliti = sum(not scarica(url, os.path.join(DATI, "suoni", *rel.split("/")), prove=2) for rel, url in mancanti.items())
    stato("suoni", falliti == 0, f"{len(elenco) - falliti} su {len(elenco)}" + (" · riprovo da solo la prossima volta" if falliti else ""),
          grave=False)


def musiche():
    catalogo = cartelle.leggi(os.path.join(cartelle.PROGRAMMA, "musica", "libere.json")).get("voci", [])
    cart = os.path.join(DATI, "suoni", "musiche-libere")
    ci_sono = len([f for f in os.listdir(cart) if f.endswith(".mp3")]) if os.path.isdir(cart) else 0
    if catalogo and ci_sono >= len(catalogo):
        stato("musiche", True, f"{ci_sono} brani")
        return
    if not os.path.exists(PY):
        stato("musiche", False, "prima serve l'ambiente dello studio", grave=False)
        return
    r = gira([PY, os.path.join(QUI, "musiche.py"), "scarica"], timeout=1800)
    righe = [x for x in (r.stdout or "").splitlines() if x.startswith("MUSICHE PRONTE")]
    n = int(righe[-1].split()[-1]) if righe else 0
    stato("musiche", n >= len(catalogo), f"{n} su {len(catalogo)} brani" +
          ("" if n >= len(catalogo) else " · riprovo da solo la prossima volta"), grave=False)


def icona():
    if os.environ.get("NDF_STUDIO_PROVA_SENZA_ICONA"):   # prova sul Mac di Michael: non toccare la sua icona vera
        return
    py = PY if os.path.exists(PY) else sys.executable
    if gira([py, os.path.join(QUI, "icona.py"), "--c-e"], timeout=60).returncode == 0:
        stato("icona sulla Scrivania", True)
        return
    r = gira([py, os.path.join(QUI, "icona.py")], timeout=120)
    stato("icona sulla Scrivania", r.returncode == 0, "" if r.returncode == 0 else (r.stderr or "")[-100:].strip(),
          grave=False)


def cartelle_cliente():
    conf = cartelle.config()
    if not conf:
        print("STATO primo avvio: DA FARE", flush=True)
        return
    ok = True
    for chiave, di_serie in (("clip", cartelle.CLIP_DI_SERIE), ("finiti", cartelle.FINITI_DI_SERIE)):
        c = os.path.expanduser(conf.get(chiave) or di_serie)
        try:
            os.makedirs(c, exist_ok=True)
        except OSError:
            ok = False
    stato("cartelle", ok, "" if ok else "non riesco a creare le cartelle scelte al primo avvio", grave=False)


def pezzi_grandi():
    try:
        import scarica as sc
        print(sc.riga_stato(), flush=True)
    except Exception as e:
        print(f"STATO pezzi grandi: DA SCARICARE · {type(e).__name__}", flush=True)


def aggiornamento():
    try:
        import aggiornamenti
        riga = aggiornamenti.una_volta_al_giorno()
        if riga:
            print(riga, flush=True)
    except Exception:
        pass   # senza internet si va avanti


def main():
    if platform.system() not in ("Darwin", "Windows"):
        print("STATO sistema: MANCA · lo studio funziona su Mac e su Windows")
        print("NON PRONTO")
        sys.exit(1)
    os.makedirs(CASA, exist_ok=True)
    passaggio()
    for c in ("lavori", "stili", "suoni"):
        os.makedirs(os.path.join(DATI, c), exist_ok=True)
    ambiente()
    ffmpeg()
    node()
    salva_percorsi()
    suoni()
    musiche()
    icona()
    cartelle_cliente()
    salva_percorsi()
    cartelle.scrivi(cartelle.PRONTO, {"versione": cartelle.versione_programma(), "requisiti": REQUISITI,
                                      "mancanti": MANCANTI, "dati": DATI, "quando": time.strftime("%Y-%m-%d %H:%M")})
    pezzi_grandi()
    if "--senza-aggiornamenti" not in sys.argv:
        aggiornamento()
    print(f"STATO PY: {PY}")
    print(f"STATO DATI: {DATI}")
    print(f"STATO casa dello studio: {CASA}")
    print("NON PRONTO" if GRAVI else "PRONTO", flush=True)
    sys.exit(1 if GRAVI else 0)


if __name__ == "__main__":
    main()
