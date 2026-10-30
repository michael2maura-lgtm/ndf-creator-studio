"""Colore del girato: un "look" da cinema applicato al video, con la pelle protetta (la faccia resta naturale).

    PY colore.py proposte <lavoro>          controllo/look.jpg: lo stesso fotogramma in tutti i look, da far scegliere
    PY colore.py applica <lavoro> <look>    tagliato-colore.mp4 (il montaggio lo usa da solo); "originale" lo toglie
    PY colore.py anteprime <lavoro>         le immagini dei look per la pagina (STUDIO/colore/anteprime)

Ogni look è una tabella di colori (LUT .cube) calcolata qui: contrasto, toni nelle ombre e nelle luci, saturazione.
La pelle si protegge per tinta: i colori della pelle restano quasi quelli veri, con la luminosità del look.
Il resto (grana, vignettatura) lo aggiunge ffmpeg.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, STUDIO, cartella_lavoro, codec_video, durata, esegui  # noqa: E402

N = 33  # punti per lato della tabella dei colori

# nome -> (nome da mostrare, a cosa serve, regolazioni, grana, vignettatura)
LOOK = {
    "originale": ("Originale", "I colori veri del video", None, 0, 0),
    "pellicola": ("Pellicola", "Caldo e morbido, come una pellicola Kodak",
                  dict(contrasto=1.08, solleva=0.035, sat=0.92, ombre=(-0.02, 0.01, 0.035), luci=(0.04, 0.015, -0.03)), 5, 0.25),
    "ambra": ("Ambra", "Luce calda del tramonto, racconti e ricordi",
              dict(contrasto=1.06, solleva=0.025, sat=1.04, ombre=(0.06, 0.015, -0.06), luci=(0.11, 0.05, -0.09)), 3, 0.2),
    "argento": ("Argento", "Desaturato e contrastato, serio e deciso",
                dict(contrasto=1.22, solleva=0.0, sat=0.55, ombre=(-0.015, 0.0, 0.02), luci=(0.0, 0.0, 0.0)), 6, 0.3),
    "smeraldo": ("Smeraldo", "Ombre verde petrolio, moderno e pulito",
                 dict(contrasto=1.1, solleva=0.02, sat=0.88, ombre=(-0.04, 0.03, 0.02), luci=(0.03, 0.02, -0.02)), 3, 0.2),
    "notte": ("Notte", "Freddo e scuro, tensione e mistero",
              dict(contrasto=1.16, solleva=-0.01, sat=0.72, ombre=(-0.03, 0.0, 0.05), luci=(-0.02, 0.0, 0.03)), 4, 0.35),
}


def tabella(r):
    """La LUT del look: array N*N*N*3 (indice blu, verde, rosso come vuole il formato .cube)."""
    import numpy as np
    v = np.linspace(0, 1, N, dtype=np.float32)
    b, g, rr = np.meshgrid(v, v, v, indexing="ij")
    rgb = np.stack([rr, g, b], -1)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    # saturazione
    out = lum[..., None] + (rgb - lum[..., None]) * r["sat"]
    # contrasto a S attorno al grigio medio, poi neri sollevati o schiacciati
    out = 0.5 + (out - 0.5) * r["contrasto"]
    out = out * (1 - r["solleva"]) + r["solleva"]
    # tono nelle ombre e nelle luci (split toning)
    l2 = np.clip(lum, 0, 1)[..., None]
    out = out + np.array(r["ombre"], np.float32) * (1 - l2) ** 2 + np.array(r["luci"], np.float32) * l2 ** 2
    out = np.clip(out, 0, 1)
    # pelle protetta: tinta arancio-rosata, saturazione media, non troppo scura
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    tinta = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * rr - g - b)) % 360
    vicino = np.minimum(np.abs(tinta - 22), 360 - np.abs(tinta - 22))
    pelle = np.exp(-(vicino / 16) ** 2) * np.clip((sat - 0.1) / 0.12, 0, 1) * np.clip((0.75 - sat) / 0.15, 0, 1) \
        * np.clip((mx - 0.18) / 0.15, 0, 1)
    lum_out = out @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    vera = np.clip(rgb * (lum_out / np.maximum(lum, 1e-4))[..., None], 0, 1)  # colore vero, luce del look
    out = out + (vera - out) * (pelle * 0.75)[..., None]
    return out


def scrivi_cube(look, percorso):
    import numpy as np
    t = tabella(LOOK[look][2])
    with open(percorso, "w") as f:
        f.write(f"TITLE \"{look}\"\nLUT_3D_SIZE {N}\n")
        np.savetxt(f, t.reshape(-1, 3), fmt="%.6f")
    return percorso


def filtro(look, cube):
    _, _, _, grana, vign = LOOK[look]
    f = f"lut3d=file='{cube}':interp=tetrahedral"
    if grana:
        f += f",noise=c0s={grana}:c0f=t"
    if vign:
        f += f",vignette=angle={0.35 + vign:.2f}"
    return f


def fotogramma(cart, t=None):
    from io import BytesIO
    from PIL import Image
    v = os.path.join(cart, "tagliato.mp4")
    t = durata(v) * 0.3 if t is None else t
    b = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(BytesIO(b)).convert("RGB")


def con_look(im, look, cart):
    """Il fotogramma con il look applicato (passa da ffmpeg, così è identico al video)."""
    from io import BytesIO
    from PIL import Image
    if look == "originale":
        return im
    cube = scrivi_cube(look, os.path.join(cart, f"look-{look}.cube"))
    buf = BytesIO()
    im.save(buf, "PNG")
    out = subprocess.run([FFMPEG, "-v", "error", "-f", "image2pipe", "-i", "-", "-vf", filtro(look, cube), "-f", "image2pipe",
                          "-vcodec", "png", "-"], input=buf.getvalue(), capture_output=True).stdout
    os.remove(cube)
    return Image.open(BytesIO(out)).convert("RGB")


def proposte(cart):
    from PIL import Image, ImageDraw, ImageFont
    im = fotogramma(cart).resize((360, 640))
    foglio = Image.new("RGB", (360 * 3, 700 * 2), (20, 14, 10))
    try:
        f = ImageFont.truetype(os.path.join(STUDIO, "font", "PlusJakartaSans.ttf"), 30)
    except OSError:
        f = ImageFont.load_default()
    for i, look in enumerate(LOOK):
        x, y = (i % 3) * 360, (i // 3) * 700
        foglio.paste(con_look(im, look, cart), (x, y))
        ImageDraw.Draw(foglio).text((x + 180, y + 670), f"{i + 1}. {LOOK[look][0]}", font=f, fill=(255, 255, 255), anchor="mm")
    os.makedirs(os.path.join(cart, "controllo"), exist_ok=True)
    p = os.path.join(cart, "controllo", "look.jpg")
    foglio.save(p, quality=88)
    print("FATTO", p)


def applica(cart, look):
    """tagliato-colore.mp4 con il look (o niente, se "originale"). Se c'è già con lo stesso look, non lo rifà."""
    dest, info = os.path.join(cart, "tagliato-colore.mp4"), os.path.join(cart, "colore.json")
    src = os.path.join(cart, "tagliato.mp4")
    if look in (None, "", "originale"):
        for p in (dest, info):
            if os.path.exists(p):
                os.remove(p)
        return src
    if look not in LOOK:
        sys.exit(f"Non conosco il look '{look}'. Ci sono: {', '.join(LOOK)}")
    if os.path.exists(dest) and os.path.exists(info) and os.path.getmtime(dest) > os.path.getmtime(src):
        with open(info, encoding="utf-8") as fh:
            if json.load(fh).get("look") == look:
                return dest
    print(f"Colore: look {LOOK[look][0]} su tutto il video...", flush=True)
    cube = scrivi_cube(look, os.path.join(cart, "look.cube"))
    esegui([FFMPEG, "-v", "error", "-y", "-i", src, "-vf", filtro(look, cube), *codec_video(), "-c:a", "copy", dest])
    os.remove(cube)
    with open(info, "w", encoding="utf-8") as fh:
        json.dump({"look": look}, fh)
    return dest


def anteprime(cart):
    out = os.path.join(STUDIO, "colore", "anteprime")
    os.makedirs(out, exist_ok=True)
    im = fotogramma(cart).resize((540, 960))
    for look in LOOK:
        con_look(im, look, cart).save(os.path.join(out, f"{look}.jpg"), quality=86)
    print("FATTO", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "proposte":
        proposte(cartella_lavoro(a[1]))
    elif len(a) >= 3 and a[0] == "applica":
        print("FATTO", applica(cartella_lavoro(a[1]), a[2]))
    elif len(a) >= 2 and a[0] == "anteprime":
        anteprime(cartella_lavoro(a[1]))
    else:
        sys.exit(__doc__)
