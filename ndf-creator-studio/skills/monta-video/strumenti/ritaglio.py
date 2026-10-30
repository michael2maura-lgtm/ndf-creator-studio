"""Ritaglio della persona: separa chi parla dallo sfondo, fotogramma per fotogramma. Serve agli effetti che mettono
qualcosa DIETRO la persona o la fanno uscire da una carta (adesivo, parola dietro la testa, clone, persona in basso).

    PY ritaglio.py <lavoro> [--da 12.5] [--a 18.0] [--duro] [--nome ritaglio]

Legge lavori/<lavoro>/tagliato.mp4 e scrive lavori/<lavoro>/<nome>.webm (1080x1920, con trasparenza, stessi
fotogrammi del tagliato a partire da --da) e controllo/<nome>.jpg (tre momenti ritagliati su un fondo a scacchi).
--duro  bordi pieni, senza mezze trasparenze (per mettere la persona su uno sfondo nuovo).

Modello: RobustVideoMatting resnet50 (pubblico, ~107 MB in ~/.studio-video/modelli). Lento: circa un secondo per
fotogramma, quindi mezzo minuto per ogni secondo di video. Va lanciato in sottofondo, e solo sui pezzi che servono.
La memoria del modello si riparte a ogni taglio (segmenti.json), così un taglio non si porta dietro il ritaglio di prima.
"""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, MODELLI, cartella_lavoro, durata, girato, leggi  # noqa: E402

MODELLO = os.path.join(MODELLI, "rvm_resnet50_fp32.onnx")
URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx"
W, H, FPS = 1080, 1920, 30
RISCALDA = 12      # giri sul primo fotogramma (e dopo ogni taglio) prima di tenere il risultato: il modello si assesta
RIDUZIONE = 0.3    # quanto il modello rimpicciolisce l'immagine per capire la sagoma (più basso = più veloce, meno fine)


def prepara_modello():
    if not os.path.exists(MODELLO) or os.path.getsize(MODELLO) < 50_000_000:
        os.makedirs(MODELLI, exist_ok=True)
        print("Scarico il modello del ritaglio (circa 107 MB, una volta sola)...", flush=True)
        subprocess.run(["curl", "-sfL", URL, "-o", MODELLO], check=True)
    import onnxruntime as ort
    return ort.InferenceSession(MODELLO, providers=["CPUExecutionProvider"])


def pulisci(a, duro):
    """Toglie le macchie staccate dalla persona (un quadro, un riflesso) e i veli quasi trasparenti."""
    import numpy as np
    from scipy import ndimage
    pieno = a > 0.5
    etichette, n = ndimage.label(pieno)
    if n > 1:
        aree = ndimage.sum(pieno, etichette, range(1, n + 1))
        tieni = np.isin(etichette, 1 + np.flatnonzero(aree >= aree.max() * 0.15))
        a = a * ndimage.binary_dilation(tieni, iterations=12)
    a[a < 0.03] = 0
    if duro:
        a = np.clip((a - 0.15) / 0.7, 0, 1)
    return a


def ritaglia(cart, da, a, nome="ritaglio", duro=False):
    """Ritaglia i secondi da-a del tagliato del lavoro in <cart>/<nome>.webm. Se c'è già, non lo rifà."""
    import numpy as np
    sorgente = girato(cart)  # con il colore, se c'è: la persona ritagliata deve avere gli stessi colori del video
    uscita = os.path.join(cart, f"{nome}.webm")
    if os.path.exists(uscita) and os.path.getmtime(uscita) > os.path.getmtime(sorgente):
        return uscita
    n_fot = int(round((a - da) * FPS))
    # i tagli del video, in fotogrammi dall'inizio del pezzo
    tagli = set()
    if os.path.exists(os.path.join(cart, "segmenti.json")):
        tagli = {round(s["inizio"] * FPS) - round(da * FPS) for s in leggi(os.path.join(cart, "segmenti.json"))}
        tagli = {t for t in tagli if 0 < t < n_fot}

    sess = prepara_modello()
    print(f"Ritaglio {a - da:.1f} secondi ({n_fot} fotogrammi): circa {n_fot * 1.1 / 60:.0f} minuti...", flush=True)
    leggi_v = subprocess.Popen([FFMPEG, "-v", "error", "-ss", f"{da:.3f}", "-i", sorgente, "-t", f"{a - da:.3f}",
                                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    scrivi_v = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "28",
                                 "-b:v", "0", "-auto-alt-ref", "0", "-row-mt", "1", uscita], stdin=subprocess.PIPE)
    zero = np.zeros((1, 1, 1, 1), np.float32)
    rid = np.array([RIDUZIONE], np.float32)
    stato = [zero] * 4
    campioni, inizio = {}, time.time()
    quando = {int(n_fot * x) for x in (0.15, 0.5, 0.85)}
    for i in range(n_fot):
        buf = leggi_v.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        src = (rgb.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        giri = RISCALDA if i == 0 or i in tagli else 1
        if i in tagli:
            stato = [zero] * 4
        for _ in range(giri):
            _, pha, *nuovo = sess.run(None, {"src": src, "r1i": stato[0], "r2i": stato[1], "r3i": stato[2],
                                             "r4i": stato[3], "downsample_ratio": rid})
            stato = nuovo
        alfa = pulisci(pha[0, 0], duro)
        rgba = np.dstack([rgb, (alfa * 255).astype(np.uint8)])
        scrivi_v.stdin.write(rgba.tobytes())
        if i in quando:
            campioni[i] = rgba.copy()
        if i % 60 == 59:
            resto = (time.time() - inizio) / (i + 1) * (n_fot - i - 1)
            print(f"  {i + 1}/{n_fot} fotogrammi, mancano circa {resto / 60:.0f} minuti", flush=True)
    leggi_v.stdout.close()
    scrivi_v.stdin.close()
    scrivi_v.wait()
    # foglio di controllo: il ritaglio su scacchi grigi, così si vedono buchi e aloni
    from PIL import Image
    yy, xx = np.indices((H, W))
    scacchi = (yy // 40 + xx // 40) % 2
    fondo = np.where(scacchi[..., None], 200, 120).astype(np.uint8).repeat(3, 2)
    fogli = []
    for i in sorted(campioni):
        c = campioni[i].astype(np.float32)
        al = c[..., 3:] / 255
        fogli.append(Image.fromarray((c[..., :3] * al + fondo * (1 - al)).astype(np.uint8)).resize((360, 640)))
    if fogli:
        foglio = Image.new("RGB", (360 * len(fogli), 640))
        for k, f in enumerate(fogli):
            foglio.paste(f, (360 * k, 0))
        os.makedirs(os.path.join(cart, "controllo"), exist_ok=True)
        foglio.save(os.path.join(cart, "controllo", f"{nome}.jpg"), quality=85)
    print(f"Ritaglio fatto in {(time.time() - inizio) / 60:.1f} minuti", flush=True)
    return uscita


def fotogramma(cart, t, duro=True):
    """Un solo fotogramma ritagliato al secondo t (per l'adesivo): immagine RGBA di PIL. Il modello si scalda sui
    fotogrammi del mezzo secondo prima, così la sagoma è stabile come nel video."""
    import numpy as np
    from PIL import Image
    sess = prepara_modello()
    da = max(0.0, t - 0.4)
    n = max(1, int(round((t - da) * FPS)) + 1)
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{da:.3f}", "-i", girato(cart), "-frames:v", str(n),
                        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    quadri = np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3)
    zero = np.zeros((1, 1, 1, 1), np.float32)
    stato, pha = [zero] * 4, None
    for i, rgb in enumerate(quadri):
        src = (rgb.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        for _ in range(RISCALDA if i == 0 else 1):
            _, pha, *stato = sess.run(None, {"src": src, "r1i": stato[0], "r2i": stato[1], "r3i": stato[2],
                                             "r4i": stato[3], "downsample_ratio": np.array([RIDUZIONE], np.float32)})
    alfa = pulisci(pha[0, 0], duro)
    return Image.fromarray(np.dstack([quadri[-1], (alfa * 255).astype(np.uint8)]), "RGBA")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    opz = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d  # noqa: E731
    cart = cartella_lavoro(args[0])
    da = float(opz("--da", 0))
    a = float(opz("--a", durata(os.path.join(cart, "tagliato.mp4"))))
    print("FATTO", ritaglia(cart, da, a, opz("--nome", "ritaglio"), "--duro" in sys.argv))


if __name__ == "__main__":
    main()
