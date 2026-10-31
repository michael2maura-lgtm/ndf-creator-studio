"""Studia per intero un reel di esempio, per rifarne lo stile: cosa c'è sullo schermo, come si muove, il ritmo, il suono.

Uso:  PY strumenti/studia.py <file o nome dell'esempio>      (es. DATI/esempi/marco/reel.mp4, oppure "marco")

Scrive DATI/esempi/<nome>/studio/:
  foglio_01.jpg ...    tutti i fotogrammi, uno ogni mezzo secondo, con il secondo scritto sopra: COSA c'è
  tagli.jpg            il fotogramma prima e dopo ogni taglio
  movimento_01.jpg ... per ogni momento in cui qualcosa entra o si muove (non i tagli), 8 fotogrammi di fila,
                       uno ogni trentesimo di secondo: COME si muovono scritte e grafiche (da dove, quanto, rimbalzo)
  grandi/              alcuni fotogrammi a grandezza piena, per caratteri e colori
  studio.json          misure: durata, tagli, inquadrature, volume nel tempo, salti di suono, parole con i tempi
E stampa le misure in poche righe. Poi GUARDA tutti i fogli e tutte le strisce, in ordine: tre fotogrammi non bastano.
Tu non senti l'audio: la riga del volume e i salti di suono sono le tue orecchie (un pop su una parola, un whoosh
su un taglio, la musica sotto). Controlla ogni salto sul fotogramma di quel secondo.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, MODELLI, durata  # noqa: E402

PICCOLO = (180, 320)


def fotogrammi(video, fps, w, h):
    """Tutti i fotogrammi a fps, rimpiccioliti a w x h, come array (n, h, w, 3)."""
    import numpy as np
    r = subprocess.run([FFMPEG, "-v", "error", "-i", video, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, 3)


def foglio(immagini, scritte, colonne, dest):
    from PIL import Image, ImageDraw
    w, h = immagini[0].size
    righe = (len(immagini) + colonne - 1) // colonne
    f = Image.new("RGB", (colonne * w, righe * (h + 22)), (20, 20, 20))
    d = ImageDraw.Draw(f)
    for i, (im, s) in enumerate(zip(immagini, scritte)):
        x, y = (i % colonne) * w, (i // colonne) * (h + 22)
        f.paste(im, (x, y + 22))
        d.text((x + 4, y + 4), s, fill=(255, 220, 90))
    f.save(dest, quality=85)


def tagli(video):
    err = subprocess.run([FFMPEG, "-v", "info", "-i", video, "-vf", "select='gt(scene,0.32)',showinfo", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", err)]


def volume(video, passo=0.25):
    """Volume (dB) ogni 0,25 s, e i salti: dove sale di colpo di almeno 9 dB rispetto a mezzo secondo prima."""
    import numpy as np
    r = subprocess.run([FFMPEG, "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768
    n = int(16000 * passo)
    db = [round(float(20 * np.log10(np.sqrt(np.mean(a[i:i + n] ** 2)) + 1e-6)), 1) for i in range(0, len(a) - n, n)]
    salti = [round(i * passo, 2) for i in range(2, len(db)) if db[i] - min(db[i - 2:i]) >= 9 and db[i] > -35]
    return db, salti


def parole(video, cart):
    """Le parole con i tempi (lingua riconosciuta da sola: gli esempi possono essere in inglese)."""
    wav = os.path.join(cart, "audio.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000", wav], check=True)
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel("medium", device="cpu", compute_type="int8", download_root=MODELLI)
        seg, info = m.transcribe(wav, word_timestamps=True, vad_filter=True)
        out = [{"testo": w.word.strip(), "da": round(w.start, 2), "a": round(w.end, 2)} for s in seg for w in (s.words or [])]
        return out, info.language
    except Exception:  # noqa: BLE001  senza voce (solo musica) o senza modello: si va avanti senza parole
        return [], None
    finally:
        os.remove(wav)


def main():
    import numpy as np
    from PIL import Image
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    video = os.path.expanduser(sys.argv[1])
    if not os.path.exists(video):
        video = os.path.join(DATI, "esempi", sys.argv[1], "reel.mp4")
    if not os.path.exists(video):
        sys.exit(f"Non trovo l'esempio: {sys.argv[1]}")
    cart = os.path.join(os.path.dirname(video), "studio")
    os.makedirs(os.path.join(cart, "grandi"), exist_ok=True)
    D = durata(video)

    # 1. cosa c'è: un fotogramma ogni mezzo secondo, fogli da 24
    f2 = fotogrammi(video, 2, *PICCOLO)
    imm = [Image.fromarray(x) for x in f2]
    fogli = []
    for k in range(0, len(imm), 24):
        dest = os.path.join(cart, f"foglio_{k // 24 + 1:02d}.jpg")
        foglio(imm[k:k + 24], [f"{(k + i) / 2:.1f}s" for i in range(len(imm[k:k + 24]))], 6, dest)
        fogli.append(dest)

    # 2. i tagli: prima e dopo
    tt = [t for t in tagli(video) if 0.2 < t < D - 0.1]
    if tt:
        coppie, scritte = [], []
        for t in tt[:30]:
            for dt in (-0.07, 0.04):
                subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(t + dt, 0):.2f}", "-i", video, "-frames:v", "1",
                                "-vf", f"scale={PICCOLO[0]}:{PICCOLO[1]}", os.path.join(cart, "_t.jpg")], check=True)
                coppie.append(Image.open(os.path.join(cart, "_t.jpg")).copy())
                scritte.append(f"{t:.2f}s {'prima' if dt < 0 else 'dopo'}")
        os.remove(os.path.join(cart, "_t.jpg"))
        foglio(coppie, scritte, 8, os.path.join(cart, "tagli.jpg"))

    # 3. come si muove: dove cambia molto l'immagine fuori dai tagli (scritte e grafiche che entrano)
    f10 = fotogrammi(video, 10, 72, 128).astype(np.float32)
    diff = np.abs(np.diff(f10, axis=0)).mean(axis=(1, 2, 3))
    soglia = max(np.percentile(diff, 85), 4.0)
    momenti = []
    for i in range(1, len(diff) - 1):
        t = (i + 1) / 10
        if diff[i] >= soglia and diff[i] >= diff[i - 1] and diff[i] >= diff[i + 1] \
                and all(abs(t - x) > 0.25 for x in tt) and all(abs(t - m) > 0.8 for m in momenti):
            momenti.append(round(t, 2))
    momenti = sorted(momenti, key=lambda t: -diff[int(t * 10) - 1])[:16]
    momenti.sort()
    f30 = None
    strisce = []
    for j, t in enumerate(momenti):
        da = max(t - 0.1, 0)
        r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{da:.3f}", "-i", video, "-frames:v", "8",
                            "-vf", f"fps=30,scale={PICCOLO[0]}:{PICCOLO[1]}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True)
        f30 = np.frombuffer(r.stdout, np.uint8).reshape(-1, PICCOLO[1], PICCOLO[0], 3)
        dest = os.path.join(cart, f"movimento_{j + 1:02d}.jpg")
        foglio([Image.fromarray(x) for x in f30], [f"{da + k / 30:.2f}s" for k in range(len(f30))], 8, dest)
        strisce.append(dest)

    # 4. fotogrammi grandi per caratteri e colori: a un quarto, metà, tre quarti, e nel mezzo dei primi momenti
    for t in sorted({round(D * q, 2) for q in (0.25, 0.5, 0.75)} | {m + 0.2 for m in momenti[:3]}):
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                        os.path.join(cart, "grandi", f"{t:.2f}s.jpg")], check=True)

    # 5. suono e parole
    db, salti = volume(video)
    pp, lingua = parole(video, cart)
    inquadrature = np.diff([0] + tt + [D]).tolist()
    misure = {"durata": round(D, 2), "tagli": tt, "tagli_ogni_10s": round(len(tt) / D * 10, 1),
              "inquadratura_media": round(float(np.mean(inquadrature)), 2), "momenti_di_movimento": momenti,
              "salti_di_suono": salti, "volume_db_ogni_0.25s": db, "lingua": lingua,
              "parole_al_secondo": round(len(pp) / D, 2) if pp else 0, "parole": pp}
    with open(os.path.join(cart, "studio.json"), "w", encoding="utf-8") as f:
        json.dump(misure, f, ensure_ascii=False, indent=1)
    print(f"Durata {D:.1f} s · {len(tt)} tagli ({misure['tagli_ogni_10s']} ogni 10 s, un'inquadratura dura in media "
          f"{misure['inquadratura_media']} s) · {misure['parole_al_secondo']} parole al secondo"
          + (f" ({lingua})" if lingua else " (nessuna voce)"))
    print(f"Momenti di movimento ({len(momenti)}): {', '.join(f'{m:.1f}' for m in momenti)}")
    print(f"Salti di suono ({len(salti)}): {', '.join(f'{s:.1f}' for s in salti[:30])}")
    print(f"Da guardare: {len(fogli)} fogli, tagli.jpg, {len(strisce)} strisce di movimento, grandi/  in {cart}")


if __name__ == "__main__":
    main()
