"""Modello Testimonianza: mette in testa al video tagliato un pezzetto della videochiamata con la cliente.

Uso:  PY strumenti/testa.py <nome-lavoro> "<videochiamata>" --da 12.4 --a 14.0
      Va lanciato subito dopo taglia.py (prima di parole.py e faccia.py), così le parole della cliente diventano
      sottotitoli. Si può rilanciare: riparte sempre dal video tagliato senza testa.

La videochiamata (di solito orizzontale, le due persone affiancate) va al centro di un fotogramma 1080x1920, con
la sua voce. Nel piano l'elemento "intervista" (effetti_testimonianza.py) la mostra in due finestre: la metà
sinistra sopra, la destra sotto. Scegli 1-2 secondi forti detti dalla cliente (il prima: "non avevo clienti").
segmenti.json viene spostato in avanti, così lo zoom ai tagli resta giusto.
"""
import argparse
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, cartella_lavoro, codec_video, durata, esegui, leggi, scrivi  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nome")
    ap.add_argument("chiamata")
    ap.add_argument("--da", type=float, required=True)
    ap.add_argument("--a", type=float, required=True)
    x = ap.parse_args()
    cart = cartella_lavoro(x.nome)
    if not os.path.isfile(x.chiamata):
        sys.exit(f"Non trovo la videochiamata: {x.chiamata}")
    base = os.path.join(cart, "tagliato-senza-testa.mp4")
    dest = os.path.join(cart, "tagliato.mp4")
    seg_base = os.path.join(cart, "segmenti-senza-testa.json")
    if not os.path.exists(base):
        shutil.copy2(dest, base)
        if os.path.exists(os.path.join(cart, "segmenti.json")):
            shutil.copy2(os.path.join(cart, "segmenti.json"), seg_base)
    d = round(x.a - x.da, 3)
    filtri = (f"[0:v]trim={x.da}:{x.a},setpts=PTS-STARTPTS,scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:color=0x0F3D3E,"
              f"fps=30,setsar=1,format=yuv420p[v0];"
              f"[0:a]atrim={x.da}:{x.a},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
              f"afade=t=in:d=0.03,afade=t=out:st={d - 0.05}:d=0.05[a0];"
              f"[1:v]fps=30,setsar=1,format=yuv420p[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
              f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[vc][a];[vc]fps=30,setpts=N/30/TB[v]")
    print(f"Metto in testa {d:.1f} s di videochiamata...")
    esegui([FFMPEG, "-v", "error", "-y", "-i", x.chiamata, "-i", base, "-filter_complex", filtri,
            "-map", "[v]", "-map", "[a]", *codec_video(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", dest])
    if os.path.exists(seg_base):
        seg = leggi(seg_base)
        for s in seg:
            for k in ("inizio",):
                if k in s:
                    s[k] = round(s[k] + d, 3)
            if "fotogramma" in s:
                s["fotogramma"] = s["fotogramma"] + round(d * 30)
        scrivi(os.path.join(cart, "segmenti.json"), [{"id": "testa", "inizio": 0.0, "fotogramma": 0, "durata": d}] + seg)
    print(f"Fatto: {durata(dest):.1f} s. Nel piano: intervista da 0 a {d:.2f}.")


if __name__ == "__main__":
    main()
