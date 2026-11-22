"""VSL orizzontale: le grafiche della versione semplice. Ognuna si disegna SOLO per i secondi in cui sta a schermo e
diventa un piccolo video trasparente (grafiche/gN.mov) che vsl_monta.py appoggia sul video con ffmpeg.
Così una VSL di 15 minuti non si disegna fotogramma per fotogramma: si disegnano solo i 4-6 secondi di ogni grafica.

Grafiche (in vsl.json, tempi in secondi del video tagliato, parole da testo.txt):
  {"tipo": "riquadro", "da": 12.4, "a": 16.0, "testo": "Il *metodo* che uso"}
      una scritta in un riquadro scuro sopra la persona; *parola* = nel colore del brand
  {"tipo": "clip", "da": 0.5, "a": 2.7, "file": "pancia-mani-oriz.mp4", "inizio": 1.0, "persona": "piccola"}
      una clip a schermo pieno (DATI/clip, scaricata con clip.py --orizzontale) con la persona in un riquadro piccolo;
      "persona": false = solo la clip
  {"tipo": "numeri", "da": 30.0, "a": 41.5, "titolo": "3 errori", "voci": [["Dieta", 31.2], ["Riposo", 34.0], ...]}
      schermo pieno nel colore del brand; i numeri 1-2-3 compaiono uno alla volta quando vengono detti
      (una voce con il tempo prima di "da" è già lì: così la lista torna più volte e cresce; "totale": 3 tiene
      i posti fissi),
      la persona resta in un riquadro a destra (lo mette vsl_monta.py nel buco lasciato dalla grafica); "persona":
      "grande" / "media" / "piccola" / false, se manca si sceglie da sola (grande fino a 3 numeri)

Il disegno è nostro (Pillow), ispirato solo ai video finiti di riferimento.
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, STUDIO  # noqa: E402

LARGO, ALTO, FPS = 1920, 1080, 30
ENTRA, ESCE = 0.35, 0.3
FONT = os.path.join(STUDIO, "font", "Poppins-Bold.ttf")
FONT_2 = os.path.join(STUDIO, "font", "Poppins-SemiBold.ttf")
# riquadro della persona (x, y, larghezza, altezza), 3:4. La grandezza si adatta: grande quando la grafica ha poco da
# mostrare (fino a 3 numeri), più piccola quando serve spazio; sopra le clip è piccolo, in basso a destra.
PERSONA = {"grande": (1340, 230, 450, 600), "media": (1420, 290, 360, 480), "piccola": (1480, 330, 300, 400)}
PERSONA_CLIP = {"grande": (1400, 470, 390, 520), "media": (1480, 540, 330, 440), "piccola": (1570, 610, 270, 360)}
RAGGIO = 28


def _font(p, s):
    return ImageFont.truetype(p, s)


def esce_morbido(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def rimbalzo(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def rgb(hexa):
    return tuple(int(hexa[i:i + 2], 16) for i in (1, 3, 5))


def luce(c):
    """Il colore del brand schiarito: per le parole accese, che su fondo scuro o sul video si devono leggere."""
    return mescola(c, (255, 255, 255), 0.45)


def mescola(a, b, k):
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def parti_testo(testo):
    """'Il *metodo* giusto' -> [('Il', False), ('metodo', True), ('giusto', False)]"""
    out, acceso = [], False
    for pezzo in testo.split("*"):
        for w in pezzo.split():
            if out and all(c in ".,;:!?" for c in w):   # la punteggiatura resta attaccata alla parola prima
                out[-1] = (out[-1][0] + w, out[-1][1])
            else:
                out.append((w, acceso))
        acceso = not acceso
    return out


def righe(parole, font, larghezza):
    out, cur = [], []
    for w in parole:
        prova = " ".join(x[0] for x in cur + [w])
        if cur and font.getlength(prova) > larghezza:
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def entrata_uscita(t, dur):
    """0 → 1 entrando, 1 fermo, 1 → 0 uscendo."""
    return min(esce_morbido(t / ENTRA), esce_morbido((dur - t) / ESCE))


# ------------------------------------------------------------------ riquadro
class Riquadro:
    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.font = _font(FONT, 66)
        self.parole = [(w.upper(), on) for w, on in parti_testo(g["testo"])]
        self.righe = righe(self.parole, self.font, 1300)
        self.alto_riga = 86
        self.cx = g.get("x", LARGO / 2)
        self.cy = g.get("y", ALTO * 0.64)   # sopra i sottotitoli
        self.buco = None
        self.copre = False

    def __call__(self, t):
        im = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        k = entrata_uscita(t, self.dur)
        if k <= 0:
            return im
        largh = max(self.font.getlength(" ".join(w for w, _ in r)) for r in self.righe)
        bw, bh = largh + 2 * 46 + 12, len(self.righe) * self.alto_riga + 2 * 26
        # il riquadro si apre dal centro, il testo sale e compare
        apri = esce_morbido(t / 0.3) if t < self.dur - ESCE else 1.0
        w_now = max(bw * apri, 20)
        x0, y0 = self.cx - w_now / 2, self.cy - bh / 2
        lay = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        ombra = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        ImageDraw.Draw(ombra).rounded_rectangle([x0 + 6, y0 + 12, x0 + w_now + 6, y0 + bh + 12], 18, fill=(0, 0, 0, 120))
        lay.alpha_composite(ombra.filter(ImageFilter.GaussianBlur(14)))
        d.rounded_rectangle([x0, y0, x0 + w_now, y0 + bh], 18, fill=(14, 14, 18, 230))
        d.rounded_rectangle([x0, y0, x0 + 12, y0 + bh], 6, fill=self.acc + (255,))
        testo_k = esce_morbido((t - 0.12) / 0.3)
        if testo_k > 0:
            txt = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
            dt = ImageDraw.Draw(txt)
            sale = (1 - testo_k) * 22
            for i, r in enumerate(self.righe):
                lr = self.font.getlength(" ".join(w for w, _ in r))
                x = self.cx - lr / 2 + 6
                y = self.cy - bh / 2 + 26 + i * self.alto_riga + sale - 6
                for w, on in r:
                    dt.text((x, y), w, font=self.font, fill=(luce(self.acc) if on else (255, 255, 255)) + (255,))
                    x += self.font.getlength(w + " ")
            a = txt.getchannel("A").point(lambda v: int(v * testo_k))
            txt.putalpha(a)
            # il testo non esce dal riquadro mentre si apre
            maschera = Image.new("L", (LARGO, ALTO), 0)
            ImageDraw.Draw(maschera).rectangle([x0 + 12, y0, x0 + w_now, y0 + bh], fill=255)
            txt.putalpha(Image.fromarray(np.minimum(np.array(txt.getchannel("A")), np.array(maschera))))
            lay.alpha_composite(txt)
        if k < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
        im.alpha_composite(lay)
        return im


# ------------------------------------------------------------------ numeri
class Numeri:
    def __init__(self, g, acc):
        self.g = g
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.voci = [(v, t - g["da"]) for v, t in g["voci"]]
        self.f_num = _font(FONT, 110)
        self.f_voce = _font(FONT_2, 46)
        self.f_tit = _font(FONT, 64)
        n = max(g.get("totale", 0), len(g["voci"]))
        scelta = g.get("persona", "grande" if n <= 3 else "media" if n <= 5 else "piccola")
        self.buco = PERSONA[scelta] if scelta else None   # qui sotto vsl_monta.py mette la persona
        self.copre = True              # schermo pieno: niente sottotitoli sopra
        self.fondo = self._fondo()

    def _fondo(self):
        """Fondo scuro tinto col colore del brand, con una luce morbida e una griglia leggera."""
        scuro = np.array(mescola((10, 11, 16), self.acc, 0.22), dtype=np.float32)
        yy, xx = np.mgrid[0:ALTO, 0:LARGO].astype(np.float32)
        luce = np.exp(-(((xx - 520) / 900) ** 2 + ((yy - 380) / 600) ** 2))[..., None]
        img = scuro + luce * (np.array(self.acc, np.float32) - scuro) * 0.22
        im = Image.fromarray(img.clip(0, 255).astype("uint8"), "RGB").convert("RGBA")
        lin = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(lin)
        for x in range(0, LARGO, 80):
            dl.line([x, 0, x, ALTO], fill=(255, 255, 255, 10))
        for y in range(0, ALTO, 80):
            dl.line([0, y, LARGO, y], fill=(255, 255, 255, 10))
        im.alpha_composite(lin)
        if not self.buco:
            return im
        # cornice del riquadro della persona: ombra e bordo nel colore del brand
        x, y, w, h = self.buco
        om = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(om).rounded_rectangle([x + 8, y + 16, x + w + 8, y + h + 16], RAGGIO, fill=(0, 0, 0, 150))
        im.alpha_composite(om.filter(ImageFilter.GaussianBlur(18)))
        ImageDraw.Draw(im).rounded_rectangle([x - 5, y - 5, x + w + 5, y + h + 5], RAGGIO + 5, fill=self.acc + (255,))
        return im

    def __call__(self, t):
        im = self.fondo.copy()
        x, y, w, h = self.buco or (0, 0, 0, 0)
        # il buco della persona si apre dopo l'entrata e si chiude prima dell'uscita
        if not self.buco:
            pass
        elif ENTRA <= t <= self.dur - ESCE:
            buco = Image.new("L", im.size, 255)
            ImageDraw.Draw(buco).rounded_rectangle([x, y, x + w, y + h], RAGGIO, fill=0)
            im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(buco))))
        else:
            ImageDraw.Draw(im).rounded_rectangle([x, y, x + w, y + h], RAGGIO, fill=(20, 20, 26, 255))
        d = ImageDraw.Draw(im)
        if self.g.get("titolo"):
            kt = esce_morbido((t - 0.15) / 0.4)
            if kt > 0:
                tit = self.g["titolo"].upper()
                d.text((150, 175 + (1 - kt) * 30), tit, font=self.f_tit, fill=(255, 255, 255, int(255 * kt)))
                d.rectangle([150, 270, 150 + 140 * kt, 278], fill=self.acc + (int(255 * kt),))
        # posti fissi per tutti i passi ("totale"): quando la lista torna, il numero 1 è sempre nello stesso punto
        n = max(self.g.get("totale", 0), len(self.voci))
        lato, passo = 210, min(380, 1060 // max(n, 1))
        x0 = 150 + (1060 - passo * (n - 1) - lato) / 2
        attivo = max([i for i, (_, tv) in enumerate(self.voci) if t >= tv] or [-1])
        for i, (voce, tv) in enumerate(self.voci):
            dt = t - tv
            if dt < 0:
                continue
            s = rimbalzo(dt / 0.4)
            cx, cy = x0 + i * passo + lato / 2, 540
            lt = lato * s
            acceso = i == attivo
            fondo = self.acc if acceso else (255, 255, 255)
            colore_num = (255, 255, 255) if acceso else mescola((10, 11, 16), self.acc, 0.1)
            om = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(om).rounded_rectangle([cx - lt / 2 + 6, cy - lt / 2 + 14, cx + lt / 2 + 6, cy + lt / 2 + 14],
                                                 26 * s, fill=(0, 0, 0, 110))
            im.alpha_composite(om.filter(ImageFilter.GaussianBlur(12)))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([cx - lt / 2, cy - lt / 2, cx + lt / 2, cy + lt / 2], 26 * s, fill=fondo + (255,))
            if s > 0.5:
                f = _font(FONT, max(10, int(110 * s)))
                d.text((cx, cy + 4), str(i + 1), font=f, fill=colore_num + (255,), anchor="mm")
            kv = esce_morbido((dt - 0.15) / 0.35)
            if kv > 0:
                for j, riga in enumerate(righe([(w, False) for w in voce.split()], self.f_voce, passo - 20)):
                    d.text((cx, cy + lato / 2 + 60 + j * 52 + (1 - kv) * 18), " ".join(w for w, _ in riga),
                           font=self.f_voce, fill=(255, 255, 255, int(255 * kv)), anchor="mm")
        k = entrata_uscita(t, self.dur)
        if k < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * k)))
        return im


# ------------------------------------------------------------------ clip
class Clip:
    """Una clip a schermo pieno (materiale del cliente o Pexels orizzontale, fino a 8 s) con la persona in un
    riquadro piccolo. La clip e la persona le mette vsl_monta.py con ffmpeg; qui si disegna solo la cornice del
    riquadro (ombra e bordo nel colore del brand), che compare e sparisce con la persona."""
    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        scelta = g.get("persona", "piccola")
        self.buco = PERSONA_CLIP[scelta] if scelta else None
        self.copre = False             # i sottotitoli restano sopra le clip
        self.clip = g["file"]
        self.cornice = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        if self.buco:
            x, y, w, h = self.buco
            om = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
            ImageDraw.Draw(om).rounded_rectangle([x + 6, y + 12, x + w + 6, y + h + 12], RAGGIO, fill=(0, 0, 0, 140))
            self.cornice.alpha_composite(om.filter(ImageFilter.GaussianBlur(16)))
            ImageDraw.Draw(self.cornice).rounded_rectangle([x - 5, y - 5, x + w + 5, y + h + 5], RAGGIO + 5,
                                                           fill=self.acc + (255,))
            buco = Image.new("L", (LARGO, ALTO), 255)
            ImageDraw.Draw(buco).rounded_rectangle([x, y, x + w, y + h], RAGGIO, fill=0)
            self.cornice.putalpha(Image.fromarray(np.minimum(np.array(self.cornice.getchannel("A")), np.array(buco))))

    def __call__(self, t):
        return self.cornice

    def maschera(self, dest):
        """Angoli arrotondati per la persona: bianco dentro, nero fuori (la usa ffmpeg con alphamerge)."""
        x, y, w, h = self.buco
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], RAGGIO, fill=255)
        m.save(dest)


TIPI = {"riquadro": Riquadro, "numeri": Numeri, "clip": Clip}


def grafica(g, acc):
    if g["tipo"] not in TIPI:
        sys.exit(f"Grafica sconosciuta: {g['tipo']} (ci sono: {', '.join(TIPI)})")
    return TIPI[g["tipo"]](g, acc)


def crea(g, acc, dest):
    """Disegna la grafica per la sua durata e la salva come video trasparente (qtrle: veloce e senza perdite)."""
    disegno = grafica(g, acc)
    n = round(disegno.dur * FPS)
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{LARGO}x{ALTO}",
                          "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", dest], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(disegno(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(f"Errore nel creare la grafica {dest}")
    return disegno
