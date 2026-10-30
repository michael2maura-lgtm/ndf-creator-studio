"""Installa tutto quello che serve allo studio, su Mac e su Windows. Si può rilanciare quando si vuole: rifà solo
quello che manca o che è rotto. Usa solo la libreria standard di Python.

Uso:  uv run --python 3.12 --no-project strumenti/installa.py      (Mac e Windows, fuori dalla sandbox)
      (uv si installa prima con una riga: vedi il passo 0 di SKILL.md)

Mette i programmi in ~/.studio-video (Python dello studio, ffmpeg, Node, modelli) e i dati in
~/Documents/NDFCreatorStudio (suoni scaricati, lavori, stili). Niente password, niente amministratore.
Scrive ~/.studio-video/percorsi.json (dove stanno python, ffmpeg, ffprobe, Node): lo leggono tutti gli strumenti,
così non servono collegamenti (che su Windows richiedono permessi speciali). Ogni passo stampa una riga STATO.
Soluzioni a problemi già incontrati:
- il Python 3.12 di Homebrew su alcuni Mac è rotto (pyexpat): si usa sempre quello di uv, che è autonomo;
- av 19 rompe faster-whisper: si fissa av < 17;
- il download di ffmpeg a volte si interrompe: si riprova da solo;
- cv2 e faster_whisper non vanno caricati nello stesso script (lo studio li tiene in pezzi separati).
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

sys.dont_write_bytecode = True
WIN = platform.system() == "Windows"
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(os.path.expanduser("~"), ".studio-video")
VENV = os.path.join(CASA, "venv")
PY = os.path.join(VENV, "Scripts", "python.exe") if WIN else os.path.join(VENV, "bin", "python")
MODELLI = os.path.join(CASA, "modelli")
DATI = os.path.expanduser(os.environ.get("NDF_STUDIO_DATI", os.path.join("~", "Documents", "NDFCreatorStudio")))
HYPERFRAMES = "hyperframes@0.8.34"
NODE = "v22.11.0"
PACCHETTI = ["faster-whisper", "mediapipe", "opencv-python-headless", "Pillow", "numpy", "scipy", "av>=12,<17", "static-ffmpeg"]
FACCIA = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
percorsi = {"python": PY}


def stato(cosa, ok, nota=""):
    print(f"STATO {cosa}: {'OK' if ok else 'MANCA'}{' · ' + nota if nota else ''}", flush=True)


def gira(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, **kw)
    except (FileNotFoundError, OSError) as e:
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


def scarica(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".parziale"
    with urllib.request.urlopen(url, timeout=180) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(tmp, dest)


def uv():
    nome = "uv.exe" if WIN else "uv"
    candidati = [shutil.which("uv"), os.path.join(os.path.expanduser("~"), ".local", "bin", nome),
                 os.path.join(os.path.expanduser("~"), ".cargo", "bin", nome), "/opt/homebrew/bin/uv"]
    trovato = next((p for p in candidati if p and os.path.exists(p)), None)
    if not trovato:
        if WIN:
            gira(["powershell", "-ExecutionPolicy", "ByPass", "-c", "irm https://astral.sh/uv/install.ps1 | iex"])
        else:
            gira(["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"])
        trovato = next((p for p in candidati[1:] if p and os.path.exists(p)), None)
    stato("uv", bool(trovato))
    return trovato


def python_studio(uv_bin):
    def sano():
        return gira([PY, "-c", "import faster_whisper, mediapipe, cv2, PIL, numpy, scipy, onnxruntime, av, static_ffmpeg;"
                               "assert int(av.__version__.split('.')[0]) < 17"]).returncode == 0
    if not (os.path.exists(PY) and sano()):
        if os.path.exists(VENV):
            shutil.rmtree(VENV)
        gira([uv_bin, "venv", "--python", "3.12", VENV])
        gira([uv_bin, "pip", "install", "--python", PY, *PACCHETTI])
    stato("Python dello studio", sano())


def ffmpeg():
    for _ in range(3):  # il download a volte si interrompe: si riprova
        r = gira([PY, "-c", "import json; from static_ffmpeg import run; "
                            "print(json.dumps(run.get_or_fetch_platform_executables_else_raise()))"])
        try:
            percorsi["ffmpeg"], percorsi["ffprobe"] = json.loads(r.stdout.strip().splitlines()[-1])
            break
        except Exception:
            continue
    stato("ffmpeg", os.path.exists(percorsi.get("ffmpeg", "")))


def node():
    def versione(n):
        r = gira([n, "--version"]) if n and os.path.exists(n) else None
        try:
            return int(r.stdout.strip().lstrip("v").split(".")[0]) if r and r.returncode == 0 else 0
        except ValueError:
            return 0
    di_sistema = shutil.which("node")
    if versione(di_sistema) >= 20 and shutil.which("npx"):
        cart = os.path.dirname(di_sistema)
    else:
        cart = os.path.join(CASA, "node")
        exe = os.path.join(cart, "node.exe" if WIN else os.path.join("bin", "node"))
        if versione(exe) < 20:
            arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"
            nome = f"node-{NODE}-{'win' if WIN else 'darwin'}-{arch}"
            archivio = os.path.join(CASA, nome + (".zip" if WIN else ".tar.gz"))
            scarica(f"https://nodejs.org/dist/{NODE}/{os.path.basename(archivio)}", archivio)
            if WIN:
                with zipfile.ZipFile(archivio) as z:
                    z.extractall(CASA)
            else:
                with tarfile.open(archivio) as t:
                    t.extractall(CASA)
            os.remove(archivio)
            if os.path.exists(cart):
                shutil.rmtree(cart)
            os.rename(os.path.join(CASA, nome), cart)
        if not WIN:
            cart = os.path.join(cart, "bin")
    percorsi["node_dir"] = cart
    percorsi["npx"] = os.path.join(cart, "npx.cmd" if WIN else "npx")
    stato("Node", os.path.exists(percorsi["npx"]))


def env_node():
    extra = [percorsi["node_dir"], os.path.dirname(percorsi.get("ffmpeg", ""))]
    return dict(os.environ, PATH=os.pathsep.join(extra + [os.environ.get("PATH", "")]))


def hyperframes():
    npx = percorsi["npx"]
    v = gira([npx, "--yes", HYPERFRAMES, "--version"], env=env_node(), cwd=CASA)
    b = gira([npx, "--yes", HYPERFRAMES, "browser", "ensure"], env=env_node(), cwd=CASA)
    gira([npx, "--yes", HYPERFRAMES, "telemetry", "disable"], env=env_node(), cwd=CASA)
    stato("HyperFrames e il suo browser", v.returncode == 0 and b.returncode == 0)


def modelli():
    os.makedirs(MODELLI, exist_ok=True)
    f = os.path.join(MODELLI, "face_detector.tflite")
    if not os.path.exists(f):
        scarica(FACCIA, f)
    r = gira([PY, "-c", "import sys; from faster_whisper import WhisperModel; "
                        "WhisperModel('medium', device='cpu', compute_type='int8', download_root=sys.argv[1])", MODELLI])
    stato("modelli (voce e faccia)", r.returncode == 0 and os.path.exists(f), "la prima volta scarica circa 1,5 GB")


def suoni():
    elenco = json.load(open(os.path.join(QUI, "suoni", "da-scaricare.json")))
    mancati = 0
    for rel, url in elenco.items():
        dest = os.path.join(DATI, "suoni", *rel.split("/"))
        if not os.path.exists(dest):
            try:
                scarica(url, dest)
            except Exception:
                mancati += 1
    stato("suoni gratuiti", mancati == 0, f"{len(elenco) - mancati} su {len(elenco)}")


def main():
    if platform.system() not in ("Darwin", "Windows"):
        sys.exit("Lo studio funziona su Mac e su Windows.")
    for c in ("lavori", "stili", "suoni", "clip"):
        os.makedirs(os.path.join(DATI, c), exist_ok=True)
    print("Installo lo studio: la prima volta ci vogliono 10-20 minuti.", flush=True)
    python_studio(uv())
    ffmpeg()
    node()
    hyperframes()
    modelli()
    suoni()
    with open(os.path.join(CASA, "percorsi.json"), "w", encoding="utf-8") as f:
        json.dump(percorsi, f, indent=1, ensure_ascii=False)
    plugin = os.path.join(os.path.dirname(os.path.dirname(QUI)), ".claude-plugin", "plugin.json")
    with open(os.path.join(CASA, "pronto.json"), "w", encoding="utf-8") as f:
        json.dump({"versione": json.load(open(plugin))["version"], "dati": DATI}, f)
    print("FINE: lo studio è pronto.")


if __name__ == "__main__":
    main()
