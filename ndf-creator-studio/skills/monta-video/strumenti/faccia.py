"""Passo 5: trova dove sta la faccia nel video tagliato, per non coprirla mai con le scritte.

Uso:  ~/.studio-video/venv/bin/python strumenti/faccia.py <nome-lavoro>

Guarda 2 fotogrammi al secondo e scrive lavori/<nome>/faccia.json, in pixel del video 1080x1920:
  {"occhi": 640, "mento": 980, "sinistra": 330, "destra": 760, "trovata": 0.97, "campioni": [...]}
occhi e mento valgono per tutto il video (il punto più in alto e più in basso in cui la faccia arriva quasi sempre).
Scrive anche controllo/faccia.jpg: un fotogramma con il riquadro della faccia, da guardare.
"""
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, MODELLI, cartella_lavoro, esegui, scrivi  # noqa: E402

LARGO, ALTO = 1080, 1920
SCALA = 0.5  # i fotogrammi si analizzano a metà misura: basta e va più veloce


def percentile(valori, p):
    v = sorted(valori)
    return v[min(len(v) - 1, max(0, round(p * (len(v) - 1))))]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cart = cartella_lavoro(sys.argv[1])
    video = os.path.join(cart, "tagliato.mp4")
    tmp = tempfile.mkdtemp()
    esegui([FFMPEG, "-v", "error", "-i", video, "-vf", f"fps=2,scale={int(LARGO * SCALA)}:{int(ALTO * SCALA)}",
            os.path.join(tmp, "f%05d.jpg")])

    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    rilevatore = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(MODELLI, "face_detector.tflite")),
        min_detection_confidence=0.5))

    campioni, file = [], sorted(os.listdir(tmp))
    for i, nome in enumerate(file):
        r = rilevatore.detect(mp.Image.create_from_file(os.path.join(tmp, nome)))
        t = round(i / 2, 2)
        if not r.detections:
            campioni.append({"t": t})
            continue
        b = max(r.detections, key=lambda d: d.bounding_box.width * d.bounding_box.height).bounding_box
        # il riquadro del rilevatore parte dalla fronte: il mento sta circa al fondo del riquadro
        campioni.append({"t": t, "x": round(b.origin_x / SCALA), "y": round(b.origin_y / SCALA),
                         "l": round(b.width / SCALA), "h": round(b.height / SCALA)})
    trovati = [c for c in campioni if "y" in c]
    if not trovati:
        shutil.rmtree(tmp)
        sys.exit("Non trovo nessuna faccia nel video: controlla un fotogramma a mano.")
    risultato = {
        "occhi": percentile([c["y"] + c["h"] * 0.25 for c in trovati], 0.05),
        "mento": percentile([c["y"] + c["h"] for c in trovati], 0.95),
        "sinistra": percentile([c["x"] for c in trovati], 0.05),
        "destra": percentile([c["x"] + c["l"] for c in trovati], 0.95),
        "trovata": round(len(trovati) / len(campioni), 2),
        "campioni": campioni,
    }
    risultato = {k: (round(v) if isinstance(v, float) and k != "trovata" else v) for k, v in risultato.items()}
    scrivi(os.path.join(cart, "faccia.json"), risultato)

    # fotogramma di controllo: riquadro della faccia e linee occhi/mento
    from PIL import Image, ImageDraw
    os.makedirs(os.path.join(cart, "controllo"), exist_ok=True)
    c = trovati[len(trovati) // 2]
    im = Image.open(os.path.join(tmp, file[campioni.index(c)])).resize((LARGO, ALTO))
    d = ImageDraw.Draw(im)
    d.rectangle([c["x"], c["y"], c["x"] + c["l"], c["y"] + c["h"]], outline="lime", width=6)
    for y, col in ((risultato["occhi"], "yellow"), (risultato["mento"], "red")):
        d.line([0, y, LARGO, y], fill=col, width=4)
    im.resize((LARGO // 2, ALTO // 2)).save(os.path.join(cart, "controllo", "faccia.jpg"), quality=85)
    shutil.rmtree(tmp)
    print(f"Faccia trovata nel {risultato['trovata'] * 100:.0f}% dei fotogrammi. "
          f"Occhi da y {risultato['occhi']}, mento fino a y {risultato['mento']}.")


if __name__ == "__main__":
    main()
