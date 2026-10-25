"""Passo 2: taglia il video direttamente dall'originale, seguendo lavori/<nome>/tagli.json.

Uso:  python3 strumenti/taglia.py <nome-lavoro> [--voce-originale]
      La voce viene pulita (fruscio, rumori bassi, volume uniforme) e i video in HDR corretti nei colori, da soli.
      --voce-originale: lascia la voce com'è registrata.

tagli.json lo scrive Claude dopo aver letto trascrizione.txt: l'ultima ripresa buona di ogni frase,
via fuori onda e pause morte. Tempi in secondi del video ORIGINALE.
  [{"id": "gancio", "da": 9.44, "a": 13.07, "riga": "Sento spesso dire..."}, ...]

Scrive:
  tagliato.mp4    1080x1920, 30 fotogrammi al secondo esatti, audio con dissolvenze di 30 ms ai tagli
  segmenti.json   dove inizia ogni pezzo nel video tagliato (secondi e fotogramma)
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, cartella_lavoro, codec_video, durata, esegui, leggi, scrivi  # noqa: E402

FPS = 30
DISSOLVENZA = 0.03  # 30 ms: niente "click" sui tagli
# ripresi dal kit "Monta le tue Ads":
# video girati in HDR (iPhone con HDR acceso): senza correzione i colori escono slavati
COLORE_HDR = "eq=contrast=1.12:saturation=1.3:gamma=0.95,colorbalance=rm=0.04:bm=-0.03"
# voce pulita: via i rumori bassi e il fruscio, volume più uniforme (il volume finale lo fa rendi.py)
VOCE = "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=80"


def e_hdr(video):
    from comune import FFPROBE
    out = esegui([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                  "-of", "csv=p=0", video]).stdout
    return any(k in out for k in ("smpte2084", "arib-std-b67"))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cart = cartella_lavoro(sys.argv[1])
    sorgente = leggi(os.path.join(cart, "sorgente.json"))
    tagli = leggi(os.path.join(cart, "tagli.json"))
    if not tagli:
        sys.exit("tagli.json è vuoto")
    for t in tagli:
        if not 0 <= t["da"] < t["a"] <= sorgente["durata"] + 0.01:
            sys.exit(f"Tempi sbagliati nel pezzo '{t['id']}': {t['da']} → {t['a']}")

    hdr = e_hdr(sorgente["video"])
    if hdr:
        print("Il video è in HDR: correggo i colori.")
    colore = f",{COLORE_HDR}" if hdr else ""
    filtri, segmenti, inizio = [], [], 0.0
    for i, t in enumerate(tagli):
        d = t["a"] - t["da"]
        filtri.append(f"[0:v]trim={t['da']}:{t['a']},setpts=PTS-STARTPTS,"
                      f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1{colore}[v{i}]")
        filtri.append(f"[0:a]atrim={t['da']}:{t['a']},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={DISSOLVENZA},afade=t=out:st={d - DISSOLVENZA:.3f}:d={DISSOLVENZA}[a{i}]")
        segmenti.append({"id": t["id"], "inizio": round(inizio, 3), "fotogramma": round(inizio * FPS),
                         "durata": round(d, 3), "da_originale": t["da"], "a_originale": t["a"]})
        inizio += d
    n = len(tagli)
    filtri.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    # fotogrammi regolari dal tempo zero: le scritte e gli effetti dopo restano a tempo fino alla fine
    filtri.append(f"[vc]fps={FPS},setpts=N/{FPS}/TB[v]")
    voce = "anull" if "--voce-originale" in sys.argv else VOCE
    filtri.append(f"[ac]{voce}[a]")

    dest = os.path.join(cart, "tagliato.mp4")
    print(f"Taglio {n} pezzi dall'originale...")
    esegui([FFMPEG, "-v", "error", "-y", "-i", sorgente["video"], "-filter_complex", ";".join(filtri),
            "-map", "[v]", "-map", "[a]", *codec_video(), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", dest])
    scrivi(os.path.join(cart, "segmenti.json"), segmenti)
    finale = durata(dest)
    print(f"Fatto: {sorgente['durata']:.1f} s → {finale:.1f} s (attesi {inizio:.1f} s)")
    for s in segmenti:
        print(f"  {s['inizio']:6.2f} s  {s['id']:<10} ({s['durata']:.1f} s)")


if __name__ == "__main__":
    main()
