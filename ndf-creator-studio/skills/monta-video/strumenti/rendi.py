"""Passo 7: crea il video finito dalla pagina del reel e sistema il volume.

Uso:  python3 strumenti/rendi.py <nome-lavoro> [--bozza]
      --bozza: qualità più bassa, più veloce, per le prove
      --solo-audio: cambiati solo suoni o musica? rifà solo l'audio sopra l'ultima versione (secondi, non minuti).
                    Prima rilancia costruisci.py, che aggiorna l'elenco dei suoni.

Scrive lavori/<nome>/finale/<nome>-vN.mp4 (ogni versione resta, non si sovrascrive mai).
Volume: -14 LUFS come vuole Instagram, picchi mai sopra -1 dB. L'immagine non si tocca.
Velocità: il reel finito va un po' più veloce del girato (VELOCITA in comune.py, 1.12 = +12%; "velocita" nel piano
la cambia per un reel, 1 = com'è). La voce accelera senza cambiare tono.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, HYPERFRAMES, NPX, VELOCITA, cartella_lavoro, codec_video, durata, env_node, esegui, leggi  # noqa: E402

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


def solo_audio(reel, video_prima, finito, vel=1.0, gia_veloce=False):
    """Rifà solo l'audio (voce + suoni + musica, letti dalla pagina del reel) sopra un video già creato.
    Si usa quando sono cambiati solo suoni o musica: pochi secondi invece di 4-5 minuti.
    vel: velocità del reel finito; gia_veloce: il video di partenza è già accelerato (versione precedente)."""
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
    filtri.append("".join(nomi) + f"amix=inputs={n}:normalize=0:duration=longest" + (f",atempo={vel:.3f}" if vel != 1 else "") + "[mix]")
    misto = finito + ".wav"
    esegui([FFMPEG, "-v", "error", "-y", *ingressi, "-filter_complex", ";".join(filtri), "-map", "[mix]", misto])
    immagine = ["-c:v", "copy"] if vel == 1 or gia_veloce else ["-vf", f"setpts=PTS/{vel:.3f},fps=30", *codec_video()]
    esegui([FFMPEG, "-v", "error", "-y", "-i", video_prima, "-i", misto, "-map", "0:v", "-map", "1:a", *immagine,
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
    piano = os.path.join(cart, "piano.json")
    vel = float((leggi(piano) if os.path.exists(piano) else {}).get("velocita", VELOCITA))
    v = 1
    while os.path.exists(os.path.join(fin, f"{nome}-v{v}.mp4")):
        v += 1
    grezzo = os.path.join(fin, f"_grezzo-v{v}.mp4")
    finito = os.path.join(fin, f"{nome}-v{v}.mp4")
    if "--solo-audio" in sys.argv:
        if v == 1:
            sys.exit("Non c'è ancora un video da cui partire: lancia rendi.py senza --solo-audio.")
        solo_audio(reel, os.path.join(fin, f"{nome}-v{v - 1}.mp4"), finito, vel, gia_veloce=True)
        print(f"Fatto (solo audio): {finito}")
        return

    qualita = "draft" if "--bozza" in sys.argv else "high"
    print(f"Creo il video (qualità {qualita}): qualche minuto...")
    # i fotogrammi in attesa occupano circa 8.5 MB l'uno sul disco: se lo spazio è poco, li manda via uno alla volta
    import shutil
    fotogrammi = durata(os.path.join(reel, "assets", "tagliato.mp4")) * 30 if os.path.exists(os.path.join(reel, "assets", "tagliato.mp4")) else 0
    poco_spazio = shutil.disk_usage(fin).free < fotogrammi * 8.5e6 * 1.3
    if poco_spazio:
        print("Poco spazio libero sul disco: creo il video un fotogramma alla volta (un po' più lento).")
    # a volte il browser che crea i fotogrammi si inceppa: si riprova una volta, con meno lavoro in parallelo
    for workers in ("4", "2"):
        r = subprocess.run([NPX, "--yes", HYPERFRAMES, "render", reel, "-o", grezzo, "-q", qualita, "-f", "30",
                            "-w", "1" if poco_spazio else workers], capture_output=True, text=True,
                           env=env_node() | ({"PRODUCER_ENABLE_STREAMING_ENCODE": "true",
                                             "PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS": "900"} if poco_spazio else {}))
        if r.returncode != 0 and "temporary frame storage" in (r.stderr or r.stdout) and not poco_spazio:
            poco_spazio = True  # la stima era bassa: si riprova senza tenere i fotogrammi sul disco
            print("Poco spazio libero sul disco: creo il video un fotogramma alla volta (un po' più lento).")
            continue
        if r.returncode == 0 and os.path.exists(grezzo):
            break
        print("Il video si è bloccato a metà: riprovo...")
    if r.returncode != 0 or not os.path.exists(grezzo):
        sys.exit("Errore nella creazione del video:\n" + (r.stderr or r.stdout)[-2500:])
    # l'audio lo rifacciamo noi (serve per il ducking della musica): del video creato si tengono solo le immagini
    solo_audio(reel, grezzo, finito, vel)
    os.remove(grezzo)
    print(f"Fatto: {finito}")


if __name__ == "__main__":
    main()
