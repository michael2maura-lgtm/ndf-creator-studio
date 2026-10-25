"""Passo 4: trascrive il video TAGLIATO. Serve a due cose: controllare che il taglio non abbia
mangiato una parola, e dare i tempi giusti ai sottotitoli.

Uso:  ~/.studio-video/venv/bin/python strumenti/parole.py <nome-lavoro> [--nomi "Claude, NDF"]

Scrive in lavori/<nome>/:
  parole.json        [{"testo": "Sento", "da": 0.06, "a": 0.24}, ...]  (da correggere a mano: nomi, errori di ascolto)
  parole_testo.txt   il testo intero, da confrontare con le righe di tagli.json
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, MODELLI, cartella_lavoro, esegui, scrivi  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("nome")
    p.add_argument("--nomi", default="")
    a = p.parse_args()
    cart = cartella_lavoro(a.nome)
    audio = os.path.join(cart, "audio_tagliato.wav")
    esegui([FFMPEG, "-v", "error", "-y", "-i", os.path.join(cart, "tagliato.mp4"), "-vn", "-ac", "1", "-ar", "16000", audio])

    from faster_whisper import WhisperModel
    modello = WhisperModel("medium", device="cpu", compute_type="int8", download_root=MODELLI)
    segmenti, _ = modello.transcribe(audio, language="it", word_timestamps=True, vad_filter=False,
                                     condition_on_previous_text=False, initial_prompt=a.nomi or None)
    parole, righe = [], []
    for s in segmenti:
        righe.append(s.text.strip())
        for w in s.words or []:
            parole.append({"testo": w.word.strip(), "da": round(w.start, 2), "a": round(w.end, 2)})
    # Whisper spezza l'apostrofo ("l" + "'amicizia"): li riunisco in una parola sola
    unite = []
    for w in parole:
        if unite and w["testo"].startswith("'"):
            unite[-1]["testo"] += w["testo"]
            unite[-1]["a"] = w["a"]
        else:
            unite.append(w)
    scrivi(os.path.join(cart, "parole.json"), unite)
    with open(os.path.join(cart, "parole_testo.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe))
    print(f"\nFatto: {len(unite)} parole in parole.json")


if __name__ == "__main__":
    main()
