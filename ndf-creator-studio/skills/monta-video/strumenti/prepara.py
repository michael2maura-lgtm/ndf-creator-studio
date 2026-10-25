"""Passo 1: prepara un lavoro. L'originale si legge soltanto, non si copia e non si tocca.

Uso:  ~/.studio-video/venv/bin/python strumenti/prepara.py "<video>" <nome-lavoro> [--nomi "Claude, NDF"]

Scrive in lavori/<nome>/:
  sorgente.json      il percorso dell'originale, durata, misure
  foglio.jpg         8 fotogrammi lungo il video (inquadratura, luce, oggetti in mano)
  parole_grezze.json ogni parola con il suo tempo, come la sente Whisper
  trascrizione.txt   le frasi con i tempi, parola per parola, e le pause: serve per scegliere le riprese
"""
import argparse
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, FFPROBE, MODELLI, cartella_lavoro, durata, esegui, scrivi  # noqa: E402


def misure(video):
    """Larghezza e altezza come si vedono (tenendo conto della rotazione del telefono)."""
    out = esegui([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                  "stream=width,height:stream_side_data=rotation", "-of", "default=nw=1", video]).stdout
    w = int(re.search(r"width=(\d+)", out).group(1))
    h = int(re.search(r"height=(\d+)", out).group(1))
    rot = re.search(r"rotation=(-?\d+)", out)
    if rot and abs(int(rot.group(1))) % 180 == 90:
        w, h = h, w
    return w, h


def foglio(video, dur, dest):
    """8 fotogrammi in fila, per vedere a colpo d'occhio com'è il girato."""
    from PIL import Image
    tmp = []
    for i in range(8):
        t = dur * (i + 0.5) / 8
        f = dest + f".{i}.jpg"
        esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                "-vf", "scale=270:-2", f])
        tmp.append((t, f))
    imgs = [Image.open(f) for _, f in tmp]
    w, h = imgs[0].size
    out = Image.new("RGB", (w * 8, h), "black")
    for i, im in enumerate(imgs):
        out.paste(im, (i * w, 0))
    out.save(dest, quality=85)
    for _, f in tmp:
        os.remove(f)


def pause(audio, soglia="-40dB", minima=0.15):
    """Dove c'è silenzio: [inizio, fine] in secondi."""
    err = subprocess.run([FFMPEG, "-i", audio, "-af", f"silencedetect=n={soglia}:d={minima}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return [[round(s, 2), round(e, 2)] for s, e in zip(st, en)]


def trascrivi(audio, nomi):
    from faster_whisper import WhisperModel
    modello = WhisperModel("medium", device="cpu", compute_type="int8", download_root=MODELLI)
    # condition_on_previous_text=False: altrimenti Whisper "salta" le frasi ripetute, e sono proprio
    # le riprese che ci servono per scegliere la migliore.
    segmenti, _ = modello.transcribe(audio, language="it", word_timestamps=True, vad_filter=False,
                                     condition_on_previous_text=False, initial_prompt=nomi or None)
    frasi = []
    for s in segmenti:
        frasi.append({"da": round(s.start, 2), "a": round(s.end, 2), "testo": s.text.strip(),
                      "parole": [{"testo": w.word.strip(), "da": round(w.start, 2), "a": round(w.end, 2)}
                                 for w in (s.words or [])]})
    return frasi


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("nome")
    p.add_argument("--nomi", default="", help="nomi e parole speciali dette nel video, per non sbagliarli")
    a = p.parse_args()
    video = os.path.abspath(os.path.expanduser(a.video))
    if not os.path.exists(video):
        sys.exit(f"Non trovo il video: {video}")
    cart = cartella_lavoro(a.nome, crea=True)
    dur = durata(video)
    w, h = misure(video)
    scrivi(os.path.join(cart, "sorgente.json"), {"video": video, "durata": round(dur, 2), "larghezza": w, "altezza": h})
    print(f"Video: {w}x{h}, {dur:.1f} secondi")

    foglio(video, dur, os.path.join(cart, "foglio.jpg"))
    audio = os.path.join(cart, "audio.wav")
    esegui([FFMPEG, "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", audio])
    print("Trascrivo (qualche minuto)...")
    frasi = trascrivi(audio, a.nomi)
    scrivi(os.path.join(cart, "parole_grezze.json"), frasi)
    silenzi = pause(audio)

    with open(os.path.join(cart, "trascrizione.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {os.path.basename(video)} · {dur:.2f} s\n")
        f.write("# [da → a] frase, poi ogni parola come parola@inizio-fine\n\n")
        for fr in frasi:
            f.write(f"[{fr['da']:7.2f} → {fr['a']:7.2f}] {fr['testo']}\n")
            f.write("    " + " ".join(f"{p['testo']}@{p['da']:.2f}-{p['a']:.2f}" for p in fr["parole"]) + "\n")
        f.write("\n# PAUSE (silenzio sotto -40 dB, almeno 0,15 s): inizio-fine\n")
        f.write(" ".join(f"{s:.2f}-{e:.2f}" for s, e in silenzi) + "\n")
    print(f"Fatto: {len(frasi)} frasi. Leggi {os.path.join(cart, 'trascrizione.txt')}")


if __name__ == "__main__":
    main()
