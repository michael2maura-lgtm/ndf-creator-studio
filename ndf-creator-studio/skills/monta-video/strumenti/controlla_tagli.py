"""Passo 3: controlla un video tagliato o finito. Si guardano i fotogrammi veri, non ci si fida del codice.

Uso:  PY strumenti/controlla_tagli.py <nome-lavoro> [video.mp4] [--telefono]

Scrive in lavori/<nome>/controllo/:
  tagli.jpg        per ogni taglio: l'ultimo fotogramma prima e il primo dopo, affiancati
  <video>-telefono.mp4  (con --telefono) una copia leggera 720p da mandare sul telefono
  nascosti.jpg     (solo per il video finito) i momenti con nero o con un fotogramma sbagliato tra due tagli
L'ultima riga è il livello dell'audio: picco e media.
"""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, cartella_lavoro, esegui, leggi  # noqa: E402

FPS = 30


def fotogramma(video, n, dest):
    t = max(n, 0) / FPS + 0.5 / FPS
    esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", video, "-frames:v", "1", "-vf", "scale=216:384", dest])


def errori_nascosti(video, out):
    """Nel video finito, gli errori che a occhio sfuggono: pezzi neri e un fotogramma sbagliato tra due tagli
    (due cambi di immagine a meno di 0,2 s: sul telefono è un lampo). Stampa i secondi e fa nascosti.jpg."""
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", video, "-an", "-vf",
                          "blackdetect=d=0.15:pix_th=0.06,select='gt(scene,0.4)',showinfo", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    neri = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    cambi = [float(t) for t in re.findall(r"pts_time:([\d.]+)", err)]
    lampi = [(a, b) for a, b in zip(cambi, cambi[1:]) if b - a < 0.2]
    for a, b in neri:
        print(f"DA GUARDARE: nero da {a:.2f} a {b:.2f} s")
    for a, b in lampi:
        print(f"DA GUARDARE: due cambi di immagine in {(b - a) * 1000:.0f} ms a {a:.2f} s (fotogramma sbagliato?)")
    momenti = [a for a, _ in neri] + [a for a, _ in lampi]
    if not momenti:
        print("Errori nascosti: niente nero, niente fotogrammi sbagliati")
        return
    from PIL import Image
    w, h = 216, 384
    foglio = Image.new("RGB", (w * 3, h * len(momenti)), "white")
    for i, t in enumerate(momenti):
        for j, dt in enumerate((-1 / FPS, 0.5 / FPS, 2 / FPS)):
            p = os.path.join(out, "_n.jpg")
            esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{max(t + dt, 0):.4f}", "-i", video, "-frames:v", "1",
                    "-vf", f"scale={w}:{h}", p])
            foglio.paste(Image.open(p).copy(), (j * w, i * h))
            os.remove(p)
    foglio.save(os.path.join(out, "nascosti.jpg"), quality=85)
    print(f"Guardali in: {os.path.join(out, 'nascosti.jpg')} (per ogni momento: prima, durante, dopo)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    cart = cartella_lavoro(args[0])
    video = args[1] if len(args) > 1 else os.path.join(cart, "tagliato.mp4")
    if not os.path.isabs(video):
        video = os.path.join(cart, video)
    segmenti = leggi(os.path.join(cart, "segmenti.json"))
    out = os.path.join(cart, "controllo")
    os.makedirs(out, exist_ok=True)

    # il video finito va più veloce del tagliato (rendi.py): i tagli cadono prima, nello stesso rapporto
    vel = 1.0
    if len(args) > 1:
        from comune import VELOCITA, con_le_scelte
        pi = leggi(os.path.join(cart, "piano.json")) if os.path.exists(os.path.join(cart, "piano.json")) else {}
        vel = float(pi.get("velocita") or con_le_scelte(pi.get("stile", ""), {}).get("velocita") or VELOCITA)

    from PIL import Image, ImageDraw
    coppie = []
    for s in segmenti[1:]:
        f = round(s["fotogramma"] / vel)
        a, b = os.path.join(out, "_a.jpg"), os.path.join(out, "_b.jpg")
        fotogramma(video, f - 1, a)
        fotogramma(video, f, b)
        coppie.append((s["id"], s["inizio"], Image.open(a).copy(), Image.open(b).copy()))
    if coppie:
        w, h = 216, 384
        foglio = Image.new("RGB", (len(coppie) * (2 * w + 20), h + 30), "white")
        d = ImageDraw.Draw(foglio)
        for i, (nome, t, ia, ib) in enumerate(coppie):
            x = i * (2 * w + 20)
            foglio.paste(ia, (x, 30))
            foglio.paste(ib, (x + w, 30))
            d.text((x + 4, 8), f"{t:.2f}s  prima | dopo  ({nome})", fill="black")
        foglio.save(os.path.join(out, "tagli.jpg"), quality=85)
        for f in ("_a.jpg", "_b.jpg"):
            os.remove(os.path.join(out, f))
        print(f"Tagli: {os.path.join(out, 'tagli.jpg')}")

    if "--telefono" in sys.argv:
        tel = os.path.join(out, os.path.splitext(os.path.basename(video))[0] + "-telefono.mp4")
        esegui([FFMPEG, "-v", "error", "-y", "-i", video, "-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "27",
                "-preset", "fast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", tel])
        print(f"Copia per il telefono: {tel}")

    if len(args) > 1:
        errori_nascosti(video, out)

    err = subprocess.run([FFMPEG, "-i", video, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    picco = re.search(r"max_volume: (-?[\d.]+)", err)
    media = re.search(r"mean_volume: (-?[\d.]+)", err)
    print(f"Audio: picco {picco.group(1)} dB, media {media.group(1)} dB")


if __name__ == "__main__":
    main()
