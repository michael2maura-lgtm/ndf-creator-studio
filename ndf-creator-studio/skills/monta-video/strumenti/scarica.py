"""I pezzi grandi dello studio, scaricati una volta sola e IN SOTTOFONDO, mentre il cliente risponde alle domande del
primo avvio e sceglie lo stile: così il primo video non aspetta i download.

Uso:  PY strumenti/scarica.py            scarica quello che manca (lancialo in sottofondo: ci vogliono minuti)
      PY strumenti/scarica.py --stato    una riga per pezzo (FATTO, IN CORSO, NON RIUSCITO, DA FARE) e il totale
      PY strumenti/scarica.py --quanto   quanto c'è ancora da scaricare, in GB (da dire al cliente PRIMA)

I pezzi (circa 2,3 GB in tutto, una volta sola):
  voce      il modello che trascrive le parole (circa 1,6 GB)
  resa      HyperFrames e il suo browser, che disegnano il video (circa 0,5 GB)
  ritaglio  il ritaglio pulito della persona, per le scritte dietro la testa (circa 0,1 GB)
  faccia    i modelli della faccia e delle mani (pochi MB)
  pulitore  il pulitore della voce DeepFilterNet (circa 30 MB)
Girano uno accanto all'altro. Un pezzo già fatto si salta in un attimo; uno non riuscito si riprova la volta dopo
(e il primo montaggio scarica da solo quello che manca). Stato in <casa>/scarica.json, uscita in <casa>/scarica.log.
Solo libreria standard all'import: controllo.py legge da qui la riga di stato.
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request

sys.dont_write_bytecode = True
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import cartelle  # noqa: E402
from cartelle import CASA, MODELLI, PY  # noqa: E402

PEZZI = ("voce", "resa", "ritaglio", "faccia", "pulitore")
CHE_COSA = {"voce": "modello della voce", "resa": "HyperFrames e il suo browser", "ritaglio": "ritaglio pulito",
            "faccia": "modelli di faccia e mani", "pulitore": "pulitore della voce"}
GB = {"voce": 1.6, "resa": 0.5, "ritaglio": 0.11, "faccia": 0.01, "pulitore": 0.03}
STATO = os.path.join(CASA, "scarica.json")
LOG = os.path.join(CASA, "scarica.log")
MODELLO_VOCE = "large-v3-turbo"
HYPERFRAMES = "hyperframes@0.8.34"
FACCIA = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
MANI = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
RVM = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx"
CHIAVE = threading.Lock()


def leggi_stato():
    return cartelle.leggi(STATO)


def segna(pezzo, come, nota=""):
    with CHIAVE:
        s = leggi_stato()
        s[pezzo] = {"stato": come, "quando": time.strftime("%Y-%m-%d %H:%M"), "nota": nota}
        cartelle.scrivi(STATO, s)
    print(f"STATO scarica {pezzo}: {come}" + (f" · {nota}" if nota else ""), flush=True)


def in_corso():
    """True se uno scarica.py sta già girando (il suo pid è vivo)."""
    pid = leggi_stato().get("_pid")
    if not pid:
        return False
    try:
        if cartelle.WIN:
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, timeout=20)
            return str(pid) in r.stdout
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def c_e(pezzo):
    """Il pezzo è ancora sul computer? (se qualcuno l'ha cancellato, si riscarica)"""
    if pezzo == "voce":
        return any(MODELLO_VOCE in d for d in (os.listdir(MODELLI) if os.path.isdir(MODELLI) else []))
    if pezzo == "ritaglio":
        return os.path.exists(os.path.join(MODELLI, "rvm_resnet50_fp32.onnx"))
    if pezzo == "faccia":
        return os.path.exists(os.path.join(MODELLI, "face_detector.tflite"))
    if pezzo == "pulitore":
        return os.path.exists(os.path.join(cartelle.BIN, "deep-filter.exe" if cartelle.WIN else "deep-filter"))
    return True


def fatti():
    s = leggi_stato()
    return [p for p in PEZZI if s.get(p, {}).get("stato") == "FATTO" and c_e(p)]


def quanto():
    return round(sum(GB[p] for p in PEZZI if p not in fatti()), 1)


def riga_stato():
    if len(fatti()) == len(PEZZI):
        return "STATO pezzi grandi: OK"
    if in_corso():
        return f"STATO pezzi grandi: IN CORSO · mancano circa {quanto()} GB"
    return f"STATO pezzi grandi: DA SCARICARE · circa {quanto()} GB, una volta sola"


def gira(cmd, timeout=3600, **kw):
    with open(LOG, "a", encoding="utf-8") as log:
        log.write(f"\n$ {' '.join(map(str, cmd))}\n")
        log.flush()
        try:
            return subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, timeout=timeout,
                                  env=kw.pop("env", dict(os.environ, PYTHONIOENCODING="utf-8")), **kw).returncode == 0
        except (OSError, subprocess.SubprocessError) as e:
            log.write(f"ERRORE {e}\n")
            return False


def file(url, dest, minimo):
    if os.path.exists(dest) and os.path.getsize(dest) >= minimo:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(dest + ".parziale", "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            if os.path.getsize(dest + ".parziale") >= minimo:
                os.replace(dest + ".parziale", dest)
                return True
        except Exception:
            time.sleep(3)
    return False


def voce():
    return gira([PY, "-c", "import sys; from faster_whisper import WhisperModel; "
                           "WhisperModel(sys.argv[1], device='cpu', compute_type='int8', download_root=sys.argv[2])",
                 MODELLO_VOCE, MODELLI])


def resa():
    p = cartelle.leggi(cartelle.PERCORSI)
    npx = p.get("npx")
    if not npx or not os.path.exists(npx):
        return False
    extra = [p.get("node_dir", ""), os.path.dirname(p.get("ffmpeg", ""))]
    env = dict(os.environ, PATH=os.pathsep.join(extra + [os.environ.get("PATH", "")]), PYTHONIOENCODING="utf-8")
    ok = gira([npx, "--yes", HYPERFRAMES, "--version"], env=env, cwd=CASA)
    ok = ok and gira([npx, "--yes", HYPERFRAMES, "browser", "ensure"], env=env, cwd=CASA)
    gira([npx, "--yes", HYPERFRAMES, "telemetry", "disable"], env=env, cwd=CASA)
    return ok


def ritaglio():
    return file(RVM, os.path.join(MODELLI, "rvm_resnet50_fp32.onnx"), 100_000_000)


def faccia():
    ok = file(FACCIA, os.path.join(MODELLI, "face_detector.tflite"), 100_000)
    file(MANI, os.path.join(MODELLI, "hand_landmarker.task"), 1_000_000)   # senza le mani si monta lo stesso
    return ok


def pulitore():
    from pulitore import deepfilter
    p = deepfilter()
    if p:
        perc = cartelle.leggi(cartelle.PERCORSI)
        perc["deepfilter"] = p
        with CHIAVE:
            cartelle.scrivi(cartelle.PERCORSI, perc)
    return bool(p)


def fai(pezzo, ancora=False):
    if pezzo in fatti() and not ancora:
        print(f"STATO scarica {pezzo}: FATTO (c'era già)", flush=True)
        return True
    segna(pezzo, "IN CORSO")
    try:
        ok = globals()[pezzo]()
    except Exception as e:
        ok = False
        with open(LOG, "a", encoding="utf-8") as log:
            log.write(f"ERRORE {pezzo}: {type(e).__name__} {e}\n")
    segna(pezzo, "FATTO" if ok else "NON RIUSCITO", "" if ok else "riprovo la prossima volta")
    return ok


def main():
    os.makedirs(CASA, exist_ok=True)
    if "--quanto" in sys.argv:
        print(f"DA SCARICARE {quanto()} GB")
        return
    if "--stato" in sys.argv:
        s = leggi_stato()
        corre = in_corso()
        for p in PEZZI:
            come = s.get(p, {}).get("stato", "DA FARE")
            if come == "IN CORSO" and not corre:
                come = "FERMATO"
            print(f"STATO scarica {p}: {come}  ({CHE_COSA[p]})")
        print(riga_stato())
        return
    if in_corso():
        print("STATO scarica: sta già scaricando (un altro scarica.py è in corso)")
        return
    with CHIAVE:
        s = leggi_stato()
        s["_pid"] = os.getpid()
        cartelle.scrivi(STATO, s)
    t0 = time.time()
    ancora = "--ancora" in sys.argv
    esiti = {}
    fili = [threading.Thread(target=lambda p=p: esiti.__setitem__(p, fai(p, ancora))) for p in PEZZI]
    for f in fili:
        f.start()
    for f in fili:
        f.join()
    with CHIAVE:
        s = leggi_stato()
        s.pop("_pid", None)
        cartelle.scrivi(STATO, s)
    tutto = all(esiti.values())
    print(f"STATO scarica: {'FATTO' if tutto else 'INCOMPLETO'} in {time.time() - t0:.0f} s"
          + ("" if tutto else " · il primo montaggio scarica da solo quello che manca"), flush=True)
    sys.exit(0 if tutto else 1)


if __name__ == "__main__":
    main()
