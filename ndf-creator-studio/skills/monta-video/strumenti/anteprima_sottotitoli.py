"""Anteprime dei sottotitoli: lo stesso pezzo di un video, una volta per ogni stile di sottotitoli.

    PY anteprima_sottotitoli.py <lavoro> <da> <a> [stile ...] [--chiave parola,parola]

Prende i secondi da-a del video tagliato del lavoro, ci mette sopra i sottotitoli e crea
STUDIO/sottotitoli/anteprime/<stile>.mp4 (540 px di larghezza, con la voce). Senza stili li fa tutti.
"""
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, HYPERFRAMES, NPX, STUDIO, cartella_lavoro, env_node, esegui, leggi  # noqa: E402
import sottotitoli  # noqa: E402

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
USCITA = os.path.join(STUDIO, "sottotitoli", "anteprime")
COLORI_NDF = {"accento": "#E86530", "accento_luce": "#FF8A4C"}


def pagina(nome, parole, chiave, y, D):
    css, corpo, tl, font = sottotitoli.parti(nome, parole, chiave, y, [], COLORI_NDF)
    return font, f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#bg{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
{css}
</style><script src="{GSAP}"></script></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1080" data-height="1920">
<video id="bg" src="assets/clip.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{D:.3f}"></video>
{chr(10).join(corpo)}
</div>
<script>
const tl = gsap.timeline({{paused: true}});
{sottotitoli.JS}
{chr(10).join(tl)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script></body></html>"""


def main():
    argv = sys.argv[1:]
    if "--chiave" in argv:  # il valore dopo --chiave non è uno stile
        del argv[argv.index("--chiave") + 1]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 3:
        sys.exit(__doc__)
    cart, da, a = cartella_lavoro(args[0]), float(args[1]), float(args[2])
    stili = args[3:] or list(sottotitoli.CATALOGO)
    chiave = set()
    if "--chiave" in sys.argv:
        chiave = set(sys.argv[sys.argv.index("--chiave") + 1].lower().split(","))
    else:
        chiave = {p.lower() for p in leggi(os.path.join(cart, "piano.json")).get("parole_chiave", [])}
    parole = [dict(w, da=w["da"] - da, a=w["a"] - da) for w in leggi(os.path.join(cart, "parole.json"))
              if w["da"] >= da and w["a"] <= a + 0.05]
    for w in parole:  # le correzioni del piano valgono anche qui
        for sbagliato, giusto in leggi(os.path.join(cart, "piano.json")).get("correzioni", {}).items():
            w["testo"] = w["testo"].replace(sbagliato, giusto)
    y = min(leggi(os.path.join(cart, "faccia.json"))["mento"] + 190, 1300)
    D = a - da
    os.makedirs(USCITA, exist_ok=True)
    lavoro = os.path.join(cart, "anteprime-sottotitoli")
    shutil.rmtree(lavoro, ignore_errors=True)
    os.makedirs(os.path.join(lavoro, "assets"))
    clip = os.path.join(lavoro, "assets", "clip.mp4")
    esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{da:.3f}", "-t", f"{D:.3f}", "-i", os.path.join(cart, "tagliato.mp4"),
            "-c:v", "libx264", "-crf", "16", "-c:a", "aac", clip])
    for nome in stili:
        reel = os.path.join(lavoro, nome)
        os.makedirs(os.path.join(reel, "assets"), exist_ok=True)
        shutil.copy2(clip, os.path.join(reel, "assets", "clip.mp4"))
        font, html_ = pagina(nome, parole, chiave, y, D)
        for f in font:
            shutil.copy2(os.path.join(STUDIO, "font", f), os.path.join(reel, "assets", f))
        with open(os.path.join(reel, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_)
        with open(os.path.join(reel, "hyperframes.json"), "w", encoding="utf-8") as f:
            json.dump({"paths": {"assets": "assets"}}, f)
        grezzo = os.path.join(lavoro, f"{nome}-grezzo.mp4")
        r = subprocess.run([NPX, "--yes", HYPERFRAMES, "render", reel, "-o", grezzo, "-q", "high", "-f", "30", "-w", "4"],
                           capture_output=True, text=True, env=env_node())
        if r.returncode != 0 or not os.path.exists(grezzo):
            print(f"ERRORE {nome}:\n" + (r.stderr or r.stdout)[-1500:])
            continue
        dest = os.path.join(USCITA, f"{nome}.mp4")
        esegui([FFMPEG, "-v", "error", "-y", "-i", grezzo, "-i", clip, "-map", "0:v", "-map", "1:a", "-vf", "scale=540:-2",
                "-c:v", "libx264", "-crf", "26", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", dest])
        print(f"FATTO {nome}: {dest}", flush=True)
    shutil.rmtree(lavoro, ignore_errors=True)


if __name__ == "__main__":
    main()
