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

LARGO, ALTO = 1920, 1080
FPS, FPS_TESTO = 30.0, "30"   # quelli del girato: li fissa vsl_monta.py prima di disegnare
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


def fondo_brand(acc, buco=None):
    """Fondo scuro tinto col colore del brand, con una luce morbida e una griglia leggera; se c'è il riquadro della
    persona, la sua cornice (ombra e bordo nel colore del brand)."""
    scuro = np.array(mescola((10, 11, 16), acc, 0.22), dtype=np.float32)
    yy, xx = np.mgrid[0:ALTO, 0:LARGO].astype(np.float32)
    chiaro = np.exp(-(((xx - 520) / 900) ** 2 + ((yy - 380) / 600) ** 2))[..., None]
    img = scuro + chiaro * (np.array(acc, np.float32) - scuro) * 0.22
    im = Image.fromarray(img.clip(0, 255).astype("uint8"), "RGB").convert("RGBA")
    lin = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lin)
    for x in range(0, LARGO, 80):
        dl.line([x, 0, x, ALTO], fill=(255, 255, 255, 10))
    for y in range(0, ALTO, 80):
        dl.line([0, y, LARGO, y], fill=(255, 255, 255, 10))
    im.alpha_composite(lin)
    if buco:
        x, y, w, h = buco
        om = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(om).rounded_rectangle([x + 8, y + 16, x + w + 8, y + h + 16], RAGGIO, fill=(0, 0, 0, 150))
        im.alpha_composite(om.filter(ImageFilter.GaussianBlur(18)))
        ImageDraw.Draw(im).rounded_rectangle([x - 5, y - 5, x + w + 5, y + h + 5], RAGGIO + 5, fill=acc + (255,))
    return im


def apri_buco(im, buco, t, dur):
    """Il buco della persona si apre dopo l'entrata e si chiude prima dell'uscita (lì sotto c'è la persona)."""
    if not buco:
        return
    x, y, w, h = buco
    if ENTRA <= t <= dur - ESCE:
        m = Image.new("L", im.size, 255)
        ImageDraw.Draw(m).rounded_rectangle([x, y, x + w, y + h], RAGGIO, fill=0)
        im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(m))))
    else:
        ImageDraw.Draw(im).rounded_rectangle([x, y, x + w, y + h], RAGGIO, fill=(20, 20, 26, 255))


def sfuma(im, k):
    if k < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * max(k, 0))))
    return im


def scritto(testo, k):
    """Il testo scritto lettera per lettera: k da 0 a 1."""
    return testo[:round(len(testo) * min(max(k, 0), 1))]


class Grafica:
    area = (0, 0, LARGO, ALTO)   # dove si appoggia sul video (le grafiche lunghe e basse sono una striscia sola)
    buco = None
    copre = False                # True = schermo pieno: niente sottotitoli sopra

    def suoni(self, g):
        """[(secondo del video, file del kit)]: pochi suoni, solo dove compare qualcosa da notare (numeri, pulsante). "suono": false nella grafica li toglie,
        "suono": "file.wav" cambia il suono."""
        return []


# ------------------------------------------------------------------ riquadro
class Riquadro(Grafica):
    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.font = _font(FONT, 66)
        self.parole = [(w.upper(), on) for w, on in parti_testo(g["testo"])]
        self.righe = righe(self.parole, self.font, 1300)
        self.alto_riga = 86
        self.cx = g.get("x", LARGO / 2)
        self.cy = g.get("y", ALTO * 0.64)   # sopra i sottotitoli
        # "stile": "scuro" (di serie), "chiaro" (riquadro bianco, testo scuro), "forte" (riquadro nel colore del brand)
        self.stile = g.get("stile", "scuro")
        bianco, nero = (255, 255, 255), (18, 18, 22)
        self.fondo, self.testo, self.acceso = {
            "scuro": ((14, 14, 18, 230), bianco, luce(self.acc)),
            "chiaro": ((250, 250, 250, 245), nero, self.acc),
            "forte": (self.acc + (245,), bianco, nero),
        }.get(self.stile, ((14, 14, 18, 230), bianco, luce(self.acc)))

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
        d.rounded_rectangle([x0, y0, x0 + w_now, y0 + bh], 18, fill=self.fondo)
        if self.stile != "forte":
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
                    dt.text((x, y), w, font=self.font, fill=(self.acceso if on else self.testo) + (255,))
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
class Numeri(Grafica):
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
        self.fondo = fondo_brand(self.acc, self.buco)

    def suoni(self, g):
        return [(t, "pop.wav") for _, t in g["voci"] if t > g["da"]]

    def __call__(self, t):
        im = self.fondo.copy()
        apri_buco(im, self.buco, t, self.dur)
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
            # l'etichetta si scrive lettera per lettera
            kv = (dt - 0.2) / max(0.25, 0.035 * len(voce))
            if kv > 0:
                fatto = 0
                for j, riga in enumerate(righe([(w, False) for w in voce.split()], self.f_voce, passo - 20)):
                    testo = " ".join(w for w, _ in riga)
                    vis = scritto(voce, kv)[fatto:fatto + len(testo)]
                    fatto += len(testo) + 1
                    if vis:
                        x_r = cx - self.f_voce.getlength(testo) / 2
                        d.text((x_r, cy + lato / 2 + 60 + j * 52), vis, font=self.f_voce, fill=(255, 255, 255, 255), anchor="lm")
        k = entrata_uscita(t, self.dur)
        if k < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * k)))
        return im


# ------------------------------------------------------------------ clip
class Clip(Grafica):
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
        if g.get("nome"):   # chi si vede nella clip (cliente, testimonianza): etichetta in basso a sinistra
            f = _font(FONT, 36)
            w = f.getlength(g["nome"])
            d = ImageDraw.Draw(self.cornice)
            d.rounded_rectangle([60, 940, 60 + w + 44, 1004], 12, fill=(250, 250, 250, 240))
            d.rectangle([60, 940, 68, 1004], fill=self.acc + (255,))
            d.text((60 + 22 + 4, 972), g["nome"], font=f, fill=(18, 18, 22, 255), anchor="lm")

    def __call__(self, t):
        return self.cornice

    def maschera(self, dest):
        """Angoli arrotondati per la persona: bianco dentro, nero fuori (la usa ffmpeg con alphamerge)."""
        x, y, w, h = self.buco
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], RAGGIO, fill=255)
        m.save(dest)


# ------------------------------------------------------------------ barra dei passaggi
class Barra(Grafica):
    """La barra dei passaggi in basso: "1. ... · 2. ... · 3. ...", il passaggio di cui si parla acceso nel colore del
    brand. Resta per tutto il capitolo. È una striscia sola (non lo schermo intero): leggera anche per minuti."""
    ALTA = 104

    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.passi = [f"{i + 1}. {p.upper()}" for i, p in enumerate(g["passi"])]
        self.attivo = sorted((t - g["da"], i) for t, i in g["attivo"])
        self.font = _font(FONT, 36)
        self.area = (0, ALTO - self.ALTA - 18, LARGO, self.ALTA + 18)
        self.larghi = [self.font.getlength(p) + 56 for p in self.passi]
        self.spazio = 34
        tot = sum(self.larghi) + self.spazio * (len(self.passi) - 1)
        self.x0 = (LARGO - tot) / 2

    def stato(self, t):
        prima, ora, da = -1, -1, -9.0
        for ta, i in self.attivo:
            if t >= ta:
                prima, ora, da = ora, i, ta
        return prima, ora, min(max((t - da) / 0.3, 0), 1)

    def chiave(self, t):
        k = entrata_uscita(t, self.dur)
        p, o, c = self.stato(t)
        return (round(k, 2), p, o, round(c, 2))

    def __call__(self, t):
        w_, h_ = self.area[2], self.area[3]
        im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
        k = entrata_uscita(t, self.dur)
        if k <= 0:
            return im
        giu = (1 - k) * 60
        d = ImageDraw.Draw(im)
        tot = sum(self.larghi) + self.spazio * (len(self.passi) - 1)
        y0 = 8 + giu
        d.rounded_rectangle([self.x0 - 18, y0, self.x0 + tot + 18, y0 + self.ALTA - 10], 22, fill=(12, 12, 16, 200))
        prima, ora, c = self.stato(t)
        x = self.x0
        for i, (p, w) in enumerate(zip(self.passi, self.larghi)):
            acc_k = c if i == ora else (1 - c) if i == prima else 0
            if acc_k > 0:
                d.rounded_rectangle([x, y0 + 12, x + w, y0 + self.ALTA - 22], 16,
                                    fill=self.acc + (int(255 * acc_k),))
            alfa = int(150 + 105 * acc_k)
            d.text((x + w / 2, y0 + (self.ALTA - 10) / 2), p, font=self.font, fill=(255, 255, 255, alfa), anchor="mm")
            x += w + self.spazio
        return sfuma(im, k)


# ------------------------------------------------------------------ frase a schermo pieno
class Frase(Grafica):
    """Una frase forte, bianca e centrata sul fondo del brand; le parole entrano una dopo l'altra, *parola* accesa."""
    copre = True

    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.font = _font(FONT, 78)
        self.righe = righe(parti_testo(g["testo"]), self.font, 1400)
        self.fondo = fondo_brand(self.acc)

    def __call__(self, t):
        im = self.fondo.copy()
        d = ImageDraw.Draw(im)
        alto = 104
        y0 = ALTO / 2 - len(self.righe) * alto / 2
        n = 0
        for i, r in enumerate(self.righe):
            lr = self.font.getlength(" ".join(w for w, _ in r))
            x = LARGO / 2 - lr / 2
            for w, on in r:
                kw = esce_morbido((t - 0.15 - n * 0.09) / 0.3)
                if kw > 0:
                    d.text((x, y0 + i * alto + (1 - kw) * 26), w, font=self.font,
                           fill=(luce(self.acc) if on else (255, 255, 255)) + (int(255 * kw),))
                    if on:
                        d.rectangle([x, y0 + i * alto + 92, x + self.font.getlength(w) * kw, y0 + i * alto + 99],
                                    fill=self.acc + (int(255 * kw),))
                x += self.font.getlength(w + " ")
                n += 1
        return sfuma(im, entrata_uscita(t, self.dur))


# ------------------------------------------------------------------ contatore sopra la persona
class Contatore(Grafica):
    """Un numero che sale da 0 al valore detto, accanto alla persona, con la scritta sotto che si scrive e tante
    piccole figure che si moltiplicano (le persone aiutate, i clienti, i contatti)."""

    def __init__(self, g, acc):
        self.g = g
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.cx = g.get("x", 1460)
        self.cy = g.get("y", 380)
        self.f_num = _font(FONT, 190)
        self.f_txt = _font(FONT, 54)
        self.alone = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        ImageDraw.Draw(self.alone).ellipse([self.cx - 420, self.cy - 300, self.cx + 420, self.cy + 420], fill=(0, 0, 0, 120))
        self.alone = self.alone.filter(ImageFilter.GaussianBlur(70))

    def suoni(self, g):
        return [(g["da"] + 0.05, "pop.wav")]   # il numero che compare

    def __call__(self, t):
        im = Image.new("RGBA", (LARGO, ALTO), (0, 0, 0, 0))
        k = entrata_uscita(t, self.dur)
        if k <= 0:
            return im
        im.alpha_composite(self.alone)
        d = ImageDraw.Draw(im)
        sale = esce_morbido(t / 1.0)
        valore = round(self.g["numero"] * sale)
        s = rimbalzo(min(t / 0.35, 1))
        f = _font(FONT, max(10, int(190 * s)))
        ombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(ombra).text((self.cx + 6, self.cy + 10), str(valore), font=f, fill=(0, 0, 0, 160), anchor="mm")
        im.alpha_composite(ombra.filter(ImageFilter.GaussianBlur(10)))
        d.text((self.cx, self.cy), str(valore), font=f, fill=luce(self.acc) + (255,), anchor="mm")
        testo = self.g.get("testo", "").upper()
        vis = scritto(testo, (t - 0.5) / max(0.3, 0.04 * len(testo)))
        if vis:
            x = self.cx - self.f_txt.getlength(testo) / 2
            d.text((x, self.cy + 140), vis, font=self.f_txt, fill=(255, 255, 255, 255), anchor="lm")
        # figure: testa e spalle, una griglia che si riempie mentre il numero sale
        quante = round(14 * sale)
        for i in range(quante):
            col, riga = i % 7, i // 7
            fx, fy = self.cx - 270 + col * 90, self.cy + 260 + riga * 100
            c = luce(self.acc) + (235,)
            d.ellipse([fx - 15, fy - 40, fx + 15, fy - 10], fill=c)
            d.rounded_rectangle([fx - 27, fy - 4, fx + 27, fy + 36], 18, fill=c)
        return sfuma(im, k)


# ------------------------------------------------------------------ chiusura
class Chiusura(Grafica):
    """La chiamata finale: la persona rimpicciolita in una cornice del brand al centro e la frase che dice
    ("Clicca il pulsante qui sotto") in un riquadro bianco sotto, con una freccia che indica giù."""
    copre = True

    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.acc = rgb(acc)
        self.buco = (510, 90, 900, 506)
        self.testo = g["testo"].upper()
        self.font = _font(FONT, 64)
        self.fondo = fondo_brand(self.acc, self.buco)

    def suoni(self, g):
        return [(g["da"] + 0.3, "pop.wav")]    # il pulsante che compare

    def __call__(self, t):
        im = self.fondo.copy()
        apri_buco(im, self.buco, t, self.dur)
        d = ImageDraw.Draw(im)
        kt = esce_morbido((t - 0.3) / 0.35)
        if kt > 0:
            w = self.font.getlength(self.testo)
            pulsa = 1 + 0.025 * math.sin(max(t - 0.8, 0) * 5)
            bw, bh = (w + 100) * pulsa, 120 * pulsa
            cy = 720 + (1 - kt) * 30
            d.rounded_rectangle([LARGO / 2 - bw / 2, cy - bh / 2, LARGO / 2 + bw / 2, cy + bh / 2], 22,
                                fill=(250, 250, 250, int(250 * kt)))
            d.text((LARGO / 2, cy), self.testo, font=self.font, fill=(18, 18, 22, int(255 * kt)), anchor="mm")
            fy = 860 + 18 * abs(math.sin(max(t - 0.6, 0) * 4))
            c = self.acc + (int(255 * kt),)
            d.rectangle([LARGO / 2 - 9, fy, LARGO / 2 + 9, fy + 70], fill=c)
            d.polygon([(LARGO / 2 - 42, fy + 62), (LARGO / 2 + 42, fy + 62), (LARGO / 2, fy + 112)], fill=c)
        return sfuma(im, entrata_uscita(t, self.dur))


# ------------------------------------------------------------------ lampo
class Lampo(Grafica):
    """Un lampo di luce calda nel colore del brand che fa da passaggio (apertura, cambio di capitolo)."""

    def __init__(self, g, acc):
        self.dur = g["a"] - g["da"]
        self.col = luce(rgb(acc))

    def __call__(self, t):
        x = t / self.dur
        a = (x / 0.3) if x < 0.3 else max(0.0, 1 - (x - 0.3) / 0.7)
        yy, xx = np.mgrid[0:ALTO:4, 0:LARGO:4].astype(np.float32)
        r = np.exp(-(((xx - LARGO * 0.3) / 700) ** 2 + ((yy - ALTO * 0.4) / 500) ** 2))
        alfa = (np.clip(0.55 + 0.45 * r, 0, 1) * 255 * a).astype("uint8")
        piccola = Image.new("RGBA", (LARGO // 4, ALTO // 4), self.col + (0,))
        piccola.putalpha(Image.fromarray(alfa))
        im = piccola.resize((LARGO, ALTO))
        return im


TIPI = {"riquadro": Riquadro, "numeri": Numeri, "clip": Clip, "barra": Barra, "frase": Frase,
        "contatore": Contatore, "chiusura": Chiusura, "lampo": Lampo}


def grafica(g, acc):
    if g["tipo"] not in TIPI:
        sys.exit(f"Grafica sconosciuta: {g['tipo']} (ci sono: {', '.join(TIPI)})")
    return TIPI[g["tipo"]](g, acc)


def crea(g, acc, dest):
    """Disegna la grafica per la sua durata e la salva come video trasparente (qtrle: veloce e senza perdite)."""
    disegno = grafica(g, acc)
    n = round(disegno.dur * FPS)
    w, h = disegno.area[2], disegno.area[3]
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
                          "-r", FPS_TESTO, "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", dest], stdin=subprocess.PIPE)
    ultima, dati = None, None
    for i in range(n):
        chiave = disegno.chiave(i / FPS) if hasattr(disegno, "chiave") else i
        if chiave != ultima:   # fotogramma uguale al precedente (barra ferma): non si ridisegna
            dati, ultima = disegno(i / FPS).tobytes(), chiave
        p.stdin.write(dati)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(f"Errore nel creare la grafica {dest}")
    return disegno
