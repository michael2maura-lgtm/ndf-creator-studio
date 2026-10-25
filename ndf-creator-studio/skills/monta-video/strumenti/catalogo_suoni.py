"""Crea un video da guardare per scegliere i suoni: ogni suono con numero, nome e provenienza, uno dopo l'altro.

Uso:  ~/.studio-video/venv/bin/python strumenti/catalogo_suoni.py [cartella-esempi]

Legge suoni/kit, suoni/mixkit, suoni/hyperframes (e, se indicata, una cartella di esempi da mettere per primi).
Scrive suoni/catalogo-suoni.mp4 e suoni/catalogo-suoni.txt (l'elenco numerato, per ritrovare i nomi).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, STUDIO, durata  # noqa: E402

SUONI = os.path.join(DATI, "suoni")
FONT = os.path.join(STUDIO, "font", "PlusJakartaSans.ttf")
FONTI = {"kit": "vecchio kit", "mixkit": "Mixkit", "hyperframes": "Creator Studio (Pixabay)", "esempi": "esempio"}
# gruppo -> parole nel nome del file (il primo che corrisponde vince)
GRUPPI = [
    ("TRANSIZIONI", r"^(tr\d|t\d|w-|whoosh|swish|swoosh|riser)"),
    ("COLPI", r"(boom|impact|impatto)"),
    ("POP E CLICK", r"(pop|click|interruttore|key-press|scatto)"),
    ("GLITCH", r"(glitch|error)"),
    ("MAGIA E SCINTILLE", r"(scintill|glitter|sparkle|luce-magica|bacchetta|chime|ding|ping|campanell|notifica-magica)"),
    ("SOLDI E VITTORIA", r"(monete|moneta|cassa|traguardo|vittoria|fanfara|livello|sblocco)"),
    ("NOTIFICHE", r"(notifica|notification)"),
    ("UFFICIO E CARTA", r"(tastiera|typing|macchina|matita|foglio|pagina|carta|tictac|fabbrica|porta)"),
    ("FESTA E PERSONE", r"(festa|applaus|folla)"),
    ("EMOZIONI", r"(triste)"),
    ("MUSICA", r"(musica)"),
]


def gruppo(nome):
    for g, schema in GRUPPI:
        if re.search(schema, nome):
            return g
    return "ALTRI"


def main():
    from PIL import Image, ImageDraw, ImageFont
    voci = []
    if len(sys.argv) > 1:
        es = sys.argv[1]
        voci += [("ESEMPI DA IMITARE", os.path.join(es, f), "esempi") for f in sorted(os.listdir(es))]
    tutti = []
    for cart in ("kit", "mixkit", "hyperframes"):
        d = next((os.path.join(base, "suoni", cart) for base in (DATI, STUDIO)
                  if os.path.isdir(os.path.join(base, "suoni", cart))), "")
        if os.path.isdir(d):
            tutti += [(gruppo(os.path.splitext(f)[0]), os.path.join(d, f), cart)
                      for f in sorted(os.listdir(d)) if f.endswith((".wav", ".mp3"))]
    ordine = [g for g, _ in GRUPPI] + ["ALTRI"]
    voci += sorted(tutti, key=lambda v: (ordine.index(v[0]), os.path.basename(v[1])))

    tmp = tempfile.mkdtemp()
    lista, righe = [], []
    f_g, f_n, f_nome, f_fonte = (ImageFont.truetype(FONT, s) for s in (40, 220, 60, 34))
    for n, (g, p, cart) in enumerate(voci, 1):
        nome = os.path.splitext(os.path.basename(p))[0]
        im = Image.new("RGB", (720, 1280), "#140E0A")
        d = ImageDraw.Draw(im)
        d.text((360, 380), g, font=f_g, fill="#FF8A4C", anchor="mm")
        d.text((360, 600), str(n), font=f_n, fill="#E86530", anchor="mm")
        d.text((360, 800), nome, font=f_nome, fill="#F9F7F4", anchor="mm")
        d.text((360, 875), FONTI[cart], font=f_fonte, fill="#b9a796", anchor="mm")
        img = os.path.join(tmp, f"{n:03d}.png")
        im.save(img)
        dd = min(durata(p), 8 if g == "MUSICA" else 3.5)
        tot = dd + 0.9
        clip = os.path.join(tmp, f"{n:03d}.mp4")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-loop", "1", "-t", f"{tot:.2f}", "-i", img, "-i", p, "-filter_complex",
                        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dd:.2f},"
                        f"afade=t=out:st={max(dd - 0.2, 0):.2f}:d=0.2,adelay=400|400,apad=whole_dur={tot:.2f}[a]",
                        "-map", "0:v", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", "-t", f"{tot:.2f}", clip], check=True)
        lista.append(f"file '{clip}'")
        righe.append(f"{n}. {nome} · {g.lower()} · {FONTI[cart]}")
    with open(os.path.join(tmp, "lista.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lista) + "\n")
    dest = os.path.join(SUONI, "catalogo-suoni.mp4")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "lista.txt"),
                    "-c", "copy", "-movflags", "+faststart", dest], check=True)
    with open(os.path.join(SUONI, "catalogo-suoni.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")
    shutil.rmtree(tmp)
    print(f"Catalogo: {len(voci)} suoni, {durata(dest) / 60:.1f} minuti → {dest}")


if __name__ == "__main__":
    main()
