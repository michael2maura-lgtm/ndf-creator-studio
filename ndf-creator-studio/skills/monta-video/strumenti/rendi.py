"""Passo 7: crea il video finito dalla pagina del reel e sistema il volume.

Uso:  python3 strumenti/rendi.py <nome-lavoro> [--bozza]
      --bozza: qualità più bassa, più veloce, per le prove
      --solo-audio: cambiati solo suoni o musica? rifà solo l'audio sopra l'ultima versione (secondi, non minuti).
                    Prima rilancia costruisci.py, che aggiorna l'elenco dei suoni.

Scrive lavori/<nome>/finale/<nome>-vN.mp4 (ogni versione resta, non si sovrascrive mai).
Volume: -14 LUFS come vuole Instagram, picchi mai sopra -1 dB. L'immagine non si tocca.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, HYPERFRAMES, NPX, cartella_lavoro, env_node, esegui  # noqa: E402

OBIETTIVO = "I=-14:TP=-2:LRA=11"


def volume_giusto(entrata, uscita):
    """Due passate: prima misura, poi regola. In una passata sola loudnorm sbaglia di 1-2 dB."""
    import json
    import re
    err = subprocess.run([FFMPEG, "-i", entrata, "-af", f"loudnorm={OBIETTIVO}:print_format=json", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\}", err[err.rfind("Parsed_loudnorm"):], re.S).group(0))
    filtro = (f"loudnorm={OBIETTIVO}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    esegui([FFMPEG, "-v", "error", "-y", "-i", entrata, "-c:v", "copy", "-af", filtro,
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", uscita])


def solo_audio(reel, video_prima, finito):
    """Rifà solo l'audio (voce + suoni + musica, letti dalla pagina del reel) sopra un video già creato.
    Si usa quando sono cambiati solo suoni o musica: pochi secondi invece di 4-5 minuti."""
    import re
    pagina = open(os.path.join(reel, "index.html"), encoding="utf-8").read()
    tracce = []
    for tag in re.findall(r"<audio [^>]*>", pagina):
        att = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        tracce.append((att.get("id", ""), os.path.join(reel, att["src"]), float(att["data-start"]), float(att.get("data-media-start", 0)),
                       float(att["data-duration"]), float(att.get("data-volume", 1))))
    ingressi, filtri, nomi = [], [], []
    i_voce = i_musica = None
    for i, (id_, src, da, ms, dur, vol) in enumerate(tracce):
        ingressi += ["-i", src]
        filtri.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim={ms:.3f}:{ms + dur:.3f},"
                      f"asetpts=PTS-STARTPTS,volume={vol},adelay={int(da * 1000)}|{int(da * 1000)}[a{i}]")
        i_voce = i if id_ == "voce" else i_voce
        i_musica = i if id_ == "musica" else i_musica
        nomi.append(f"[a{i}]")
    if i_voce is not None and i_musica is not None:
        # ducking: la musica si abbassa da sola quando la persona parla e risale nelle pause
        filtri.append(f"[a{i_voce}]asplit=2[voce][chiave]")
        filtri.append(f"[a{i_musica}][chiave]sidechaincompress=threshold=0.015:ratio=8:attack=30:release=350[musica]")
        nomi[i_voce], nomi[i_musica] = "[voce]", "[musica]"
    n = len(tracce)
    filtri.append("".join(nomi) + f"amix=inputs={n}:normalize=0:duration=longest[mix]")
    misto = finito + ".wav"
    esegui([FFMPEG, "-v", "error", "-y", *ingressi, "-filter_complex", ";".join(filtri), "-map", "[mix]", misto])
    esegui([FFMPEG, "-v", "error", "-y", "-i", video_prima, "-i", misto, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-c:a", "pcm_s16le", "-shortest", finito + ".mov"])
    volume_giusto(finito + ".mov", finito)
    os.remove(misto)
    os.remove(finito + ".mov")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    nome = args[0]
    cart = cartella_lavoro(nome)
    reel = os.path.join(cart, "reel")
    if not os.path.exists(os.path.join(reel, "index.html")):
        sys.exit("Prima lancia costruisci.py")
    fin = os.path.join(cart, "finale")
    os.makedirs(fin, exist_ok=True)
    v = 1
    while os.path.exists(os.path.join(fin, f"{nome}-v{v}.mp4")):
        v += 1
    grezzo = os.path.join(fin, f"_grezzo-v{v}.mp4")
    finito = os.path.join(fin, f"{nome}-v{v}.mp4")
    if "--solo-audio" in sys.argv:
        if v == 1:
            sys.exit("Non c'è ancora un video da cui partire: lancia rendi.py senza --solo-audio.")
        solo_audio(reel, os.path.join(fin, f"{nome}-v{v - 1}.mp4"), finito)
        print(f"Fatto (solo audio): {finito}")
        return

    qualita = "draft" if "--bozza" in sys.argv else "high"
    print(f"Creo il video (qualità {qualita}): qualche minuto...")
    # a volte il browser che crea i fotogrammi si inceppa: si riprova una volta, con meno lavoro in parallelo
    for workers in ("4", "2"):
        r = subprocess.run([NPX, "--yes", HYPERFRAMES, "render", reel, "-o", grezzo, "-q", qualita, "-f", "30",
                            "-w", workers], capture_output=True, text=True, env=env_node())
        if r.returncode == 0 and os.path.exists(grezzo):
            break
        print("Il video si è bloccato a metà: riprovo...")
    if r.returncode != 0 or not os.path.exists(grezzo):
        sys.exit("Errore nella creazione del video:\n" + (r.stderr or r.stdout)[-2500:])
    # l'audio lo rifacciamo noi (serve per il ducking della musica): del video creato si tengono solo le immagini
    solo_audio(reel, grezzo, finito)
    os.remove(grezzo)
    print(f"Fatto: {finito}")


if __name__ == "__main__":
    main()
