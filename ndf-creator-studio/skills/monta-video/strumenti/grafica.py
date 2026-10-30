"""Motore "grafica": reel con motion graphics sopra la persona (stili con "motore": "grafica" nello stile.json).
Scritte che si decodificano, targhette che entrano in lista, parola gigante su targa inclinata, bande di transizione,
la persona dentro una cornice luminosa o un telefono, contatore, messaggio scritto lettera per lettera, barra di
passi con spunte, mirino REC in apertura, finale scuro con bottone. Colori, font e suoni vengono dallo stile.

piano.json (lo scrive Claude, tempi in secondi del video TAGLIATO):
{"stile": "ndf-grafica",
 "correzioni": {...}, "aggiungi": [...],                  come nel motore normale (costruisci.py)
 "parole_chiave": ["domande", "15", "info"],              nei sottotitoli finiscono su una targhetta col colore d'accento
 "musica": true,
 "apertura": {"sopra": "PUBBLICHI", "targa": "A CASO?", "a": 2.0},     titolo d'apertura sul petto + mirino REC
 "elementi": [
   {"tipo": "titolo", "da": 45.3, "a": 50.1, "sopra": "LE STESSE", "targa": "DOMANDE", "sotto": "PRIMA DI DECIDERE", "sotto_da": 48.6},
   {"tipo": "gigante", "da": 6.6, "a": 9.6, "testo": "PIÙ SEMPLICE.", "sotto": "C'È UN MODO MIGLIORE"},
   {"tipo": "targhette", "a": 29.25, "voci": [["①", "STORIE INSTAGRAM", 23.0], ["?", "ADESIVO DOMANDE", 28.1]]},
   {"tipo": "contatore", "da": 17.3, "a": 20.8, "numero": 15, "conta": 17.66, "prima": ["TI DARÀ", "DOMANDE"],
    "dopo": ["I TUOI PROSSIMI", "CONTENUTI"], "dopo_da": 19.8},
   {"tipo": "cornice", "da": 9.65, "a": 17.1, "titoli": [["APRI", "CHATGPT", 9.75]],
    "chat": {"etichetta": "CHATGPT", "testo": "Quali sono...", "da": 11.76, "a": 15.2},
    "passi": [["DOMANDE", 57.24], ["CONTENUTI", 61.84]]},           chat e passi: facoltativi, uno dei due
   {"tipo": "telefono", "da": 29.3, "a": 37.9, "titoli": [["SECONDA COSA", "UN REEL", 29.4], ["ALMENO", "60 SECONDI", 33.0]]},
   con il ritaglio della persona (lento: mezzo minuto per secondo, solo sul pezzo che serve):
   {"tipo": "dietro", "da": 6.54, "parola": "SEMPLICE", "quando": 8.08, "a": 9.6},     parola dietro la testa
   {"tipo": "adesivo", "quando": 19.85, "a": 23.0, "note": [["15 contenuti", 20.3], ["*in 5 minuti*", 21.0]]},
   {"tipo": "schermo", "da": 9.75, "a": 15.3, "file": "ragazza-computer.mp4", "lato": "destra"},
   {"tipo": "luce", "da": 15.5, "a": 19.6, "parole": [["Il tuo settore", 16.16], ["15 domande", 17.66]]},
   senza ritaglio:
   {"tipo": "commento", "da": 64.6, "parola": "INFO", "scrivi": 65.24, "risposta": "Te lo invio in direct",
    "risposta_da": 66.5, "chip": "Il metodo"},                                      il commento che si scrive
   {"tipo": "numero", "da": 17.66, "a": 20.8, "numero": "15", "righe": [["DOMANDE", 18.1], ["CONTENUTI", 19.8]]},
   {"tipo": "etichette", "quando": 43.5, "a": 45.3, "voci": [["solo contenuti?", 43.78], ["solo post?", 44.72]]},
   {"tipo": "neon", "da": 7.0, "quando": 8.08, "a": 9.6, "testo": "più semplice"},  insegna sul muro (con ritaglio)
   {"tipo": "percorso", "da": 55.9, "a": 64.6, "etichetta": "IL MIO METODO", "titolo": "dalle domande ai contatti",
    "passi": [["domande", 57.24], ["contenuti", 61.84], ["+ contatti", 62.58, "stessa riga"]]},
   {"tipo": "checklist", "da": 22.6, "a": 37.9, "titolo": "Tutto quello che serve",
    "voci": [["Domande nelle storie", 23.5], ["Un reel per domanda", 30.9], ["Risposta semplice", 35.3]]},
   {"tipo": "contachilometri", "da": 17.4, "a": 21.8, "numeri": [{"valore": "15", "etichetta": "DOMANDE", "da": 17.66},
    {"valore": "15", "etichetta": "CONTENUTI", "sotto": "pronti", "da": 19.8}]},
   {"tipo": "pillole", "a": 47.2, "voci": [["contenuti", 43.78], ["post", 44.72]]},
   {"tipo": "prompt", "da": 58.0, "a": 63.6, "testo": "trasforma i contenuti in contatti", "scrivi_da": 61.0, "scrivi_a": 63.0},
   {"tipo": "telefono3d", "da": 9.6, "a": 17.1, "app": "ChatGPT", "messaggi": [["Quali sono le domande...", 11.76, "io"]],
    "scheda": {"etichetta": "Risposta", "titolo": "15 domande pronte", "bottone": "Copia", "da": 14.5}, "tocco": 16.2, "fatto": "Copiato"},
   {"tipo": "orbita", "da": 50.0, "a": 55.8},                     con ritaglio: copertine dei reel già montati
   {"tipo": "zoom", "mosse": [[0.3, 2.4, 1.12, "lento"], [3.6, 3.9, 1.3, "scatto"], [4.9, 5.2, 1.0, "fuori"]]}],
 "finale_da": 64.75, "finale_sopra": "TE LO INVIO IN DIRECT", "finale_testo": "COMMENTA", "finale_bottone": "INFO"}

 "transizioni": [14.6, 40.7],     cambi di argomento: la transizione dello stile (sfumatura, bande o niente)
 "apertura": {"box": "Il format che fa crescere i profili", "a": 4.0},   in alternativa al titolo NDF: riquadro bianco
stile.json può avere "mirino": false, "finale": false, "transizione": "sfumatura" | "bande" | "taglio".

Regole: un "gigante" porta da solo le bande all'entrata e all'uscita; cornice e telefono entrano con un vortice.
I sottotitoli (1-3 parole) spariscono da soli sotto titoli, targhette, contatore, scene scure e finale.
Testi dei titoli: 1-3 parole, quelle dette. "titoli" di cornice e telefono: [sopra, targa, da], ognuno fino al successivo.
"""
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess

import effetti
import sottotitoli
from comune import DATI, FFMPEG, STUDIO, durata, girato, trova

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
MIRINO_FINO = 6.2  # il mirino REC solo in apertura: per tutto il reel stanca


class Reel:
    def __init__(self, stile, cart_stile, reel, D):
        self.stile, self.cart_stile, self.reel, self.D = stile, cart_stile, reel, D
        self.assets = os.path.join(reel, "assets")
        self.corpo, self.tl, self.audio, self.nascondi, self.transizioni = [], [], [], [], []
        self.camera = []  # cose dentro l'inquadratura (#cam), sopra il video: si muovono con zoom e cornici

    # ---------- suoni ----------
    def suono(self, nome, da, vol=0.45, dur=None, se_manca=None):
        """Un suono dello stile al secondo `da`, a -16 LUFS come tutti gli altri (i suoni scelti nella pagina sono già
        dentro lo stile: comune.con_le_scelte). Se lo stile non ha `nome`, suona `se_manca` (o niente)."""
        cart, rel = self.cart_stile, self.stile["suoni"].get(nome)
        if rel == "":  # "nessun suono" scelto nella pagina: niente, nemmeno il ripiego
            return
        if not rel:
            if se_manca:
                self.suono(se_manca, da, vol, dur)
            return
        if nome == "transizione":  # un solo suono per cambio di scena, mai due attaccati
            if any(abs(da - t) < 0.4 for t in self.transizioni):
                return
            self.transizioni.append(da)
        src = os.path.join(cart, rel)  # rel può essere un percorso intero (suono scelto nella pagina)
        dest = os.path.join(self.assets, f"sfx-{hashlib.md5(src.encode()).hexdigest()[:6]}-{os.path.splitext(os.path.basename(rel))[0]}.m4a")
        if not os.path.exists(dest):
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-af",
                            "loudnorm=I=-16:TP=-1.5,aresample=48000", "-c:a", "aac", dest], check=True)
        n = len(self.audio)
        self.audio.append(f'<audio id="s{n}" src="assets/{os.path.basename(dest)}" data-start="{da:.3f}" data-media-start="0" '
                          f'data-duration="{min(dur or 99, durata(dest), self.D - da):.3f}" data-volume="{vol}"></audio>')

    def musica(self, vol=0.2):
        rel = self.stile["suoni"].get("musica")
        if not rel:
            return
        dest = os.path.join(self.assets, "musica.m4a")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-stream_loop", "-1", "-i", os.path.join(self.cart_stile, rel),
                        "-t", f"{self.D:.2f}", "-af", f"afade=t=out:st={self.D - 1.5:.2f}:d=1.5", "-c:a", "aac", dest], check=True)
        self.audio.append(f'<audio id="musica" src="assets/musica.m4a" data-start="0" data-media-start="0" '
                          f'data-duration="{self.D:.3f}" data-volume="{vol}"></audio>')

    # ---------- pezzi grafici ----------
    def decodifica(self, sel, testo, da, dur=0.45):
        """Lettere a caso che diventano la parola (sempre le stesse lettere: il video si rifà uguale)."""
        self.tl.append(f'decodifica("{sel}",{json.dumps(testo)},{da:.3f},{dur});')

    def bande(self, da):
        """Transizione: bande colorate che attraversano lo schermo; sotto avviene il cambio di scena."""
        c = self.stile["colori"]
        n = len(self.corpo)
        righe = []
        for k, (y, h, col, dx) in enumerate([(140, 60, c["banda"], 1), (330, 26, c["accento"], -1), (520, 90, c["accento_luce"], 1),
                                             (760, 40, c["accento"], -1), (930, 120, c["banda"], 1), (1180, 30, c["accento_luce"], -1),
                                             (1330, 80, c["accento"], 1), (1560, 50, c["banda"], -1), (1720, 110, c["accento_luce"], 1)]):
            righe.append(f'<div class="banda" id="b{n}_{k}" style="top:{y}px;height:{h}px;background:{col}"></div>')
            self.tl.append(f'tl.fromTo("#b{n}_{k}",{{x:{dx * 1300}}},{{x:{-dx * 1300},duration:0.55,ease:"power2.inOut"}},'
                           f'{da - 0.25 + k * 0.012:.3f});')
        self.corpo.append(f'<div class="bande">{"".join(righe)}</div>')
        self.suono("transizione", da - 0.2)

    def scuro(self, da, a):
        """Sfondo scuro con la griglia in prospettiva: copre la persona da `da` ad `a`."""
        n = len(self.corpo)
        self.corpo.append(f'<div class="scuro" id="sc{n}"><div class="griglia"></div><div class="alone"></div></div>')
        self.tl.append(f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});tl.set("#sc{n}",{{opacity:0}},{a:.3f});')
        self.nascondi.append((da, a))

    def gigante(self, e):
        """La parola gigante su una targa inclinata, con scintille, su fondo scuro (bande all'entrata e all'uscita)."""
        da, a, testo = e["da"], e["a"], e["testo"]
        self.bande(da - 0.1)
        self.scuro(da - 0.1, a)
        n = len(self.corpo)
        size = min(112, int(860 / (0.86 * len(testo))))  # la parola entra sempre nella targa
        scintille = "".join(f'<i class="sc" id="g{n}s{k}"></i>' for k in range(14))
        self.corpo.append(f'<div class="gigante" id="g{n}"><div class="targa-g" id="g{n}t" style="font-size:{size}px">'
                          f'{html.escape(testo)}</div>{scintille}'
                          + (f'<div class="mono-sotto" id="g{n}m"></div>' if e.get("sotto") else "") + '</div>')
        self.tl.append(f'tl.set("#g{n}",{{opacity:1}},{da:.3f});'
                       f'tl.fromTo("#g{n}t",{{scale:2.6,rotate:-14,opacity:0}},{{scale:1,rotate:-7,opacity:1,duration:0.35,ease:"back.out(1.6)"}},{da:.3f});'
                       f'tl.to("#g{n}t",{{scale:1.06,duration:{max(a - da - 0.6, 0.1):.2f},ease:"none"}},{da + 0.4:.3f});'
                       f'tl.set("#g{n}",{{opacity:0}},{a:.3f});')
        for k in range(14):  # scintille in fuori, sempre negli stessi punti
            ang, dist = k * 2.4, 260 + (k * 53) % 220
            self.tl.append(f'tl.fromTo("#g{n}s{k}",{{x:0,y:0,opacity:1,scale:1}},{{x:{dist * math.cos(ang):.0f},'
                           f'y:{dist * math.sin(ang) * 0.7:.0f},opacity:0,scale:0.3,duration:0.9,ease:"power2.out"}},{da + 0.12:.3f});')
        if e.get("sotto"):
            self.decodifica(f"#g{n}m", e["sotto"], da + 0.6)
        self.suono("attesa", max(da - 1.7, 0), 0.3)
        self.suono("impatto", da, 0.5)

    def titolo(self, sopra, targa, da, a, y):
        """Riga bianca + riga su targa d'accento, che si decodificano."""
        n = len(self.corpo)
        self.corpo.append(f'<div class="titolo" id="t{n}" style="top:{y}px"><div class="riga-b" id="t{n}a"></div>'
                          f'<div class="targa" id="t{n}b"></div></div>')
        self.tl.append(f'tl.set("#t{n}",{{opacity:1}},{da:.3f});'
                       f'tl.fromTo("#t{n}b",{{scaleX:0}},{{scaleX:1,duration:0.25,ease:"power3.out"}},{da + 0.15:.3f});'
                       f'tl.to("#t{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
        self.decodifica(f"#t{n}a", sopra, da)
        self.decodifica(f"#t{n}b", targa, da + 0.15)
        self.suono("glitch", da, 0.3)

    def sotto_mono(self, testo, da, a, y):
        n = len(self.corpo)
        self.corpo.append(f'<div class="mono-sotto fisso" id="m{n}" style="top:{y}px"></div>')
        self.tl.append(f'tl.set("#m{n}",{{opacity:1}},{da:.3f});tl.to("#m{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
        self.decodifica(f"#m{n}", testo, da)

    def targhette(self, voci, a, y0):
        """Targhette con icona che entrano da sinistra una sotto l'altra. voci: [[icona, testo, quando]]."""
        for k, (icona, testo, da) in enumerate(voci):
            n = len(self.corpo)
            self.corpo.append(f'<div class="chip" id="c{n}" style="top:{y0 + k * 104}px"><span class="ico">{html.escape(icona)}</span>'
                              f'<span id="c{n}t"></span></div>')
            self.tl.append(f'tl.fromTo("#c{n}",{{x:-1100,opacity:1}},{{x:0,duration:0.35,ease:"power3.out"}},{da:.3f});'
                           f'tl.to("#c{n}",{{x:-1100,duration:0.3,ease:"power3.in"}},{a - 0.3 + k * 0.04:.3f});'
                           f'tl.set("#c{n}",{{opacity:0}},{a + 0.1:.3f});')
            self.decodifica(f"#c{n}t", testo, da + 0.1, 0.4)
            self.suono("pop", da, 0.4)
        self.nascondi.append((voci[0][2], a))

    def contatore(self, e, y):
        """Targhetta con un numero grande che conta (0 -> numero); le scritte ai lati possono cambiare."""
        n = len(self.corpo)
        prima = e.get("prima", ["", ""])
        self.corpo.append(f'<div class="prezzo" id="pz{n}" style="top:{y}px"><span class="pz-lab" id="pzl{n}">{html.escape(prima[0])}</span>'
                          f'<span class="pz-num" id="pzn{n}">0</span><span class="pz-sotto" id="pzs{n}">{html.escape(prima[1])}</span></div>')
        conta = e.get("conta", e["da"] + 0.3)
        self.tl.append(f'tl.fromTo("#pz{n}",{{scaleX:0,opacity:1}},{{scaleX:1,duration:0.3,ease:"power3.out"}},{e["da"]:.3f});'
                       f'conta("#pzn{n}",0,{e["numero"]},{conta:.3f},0.6);'
                       f'tl.fromTo("#pzn{n}",{{scale:1.4}},{{scale:1,duration:0.25,ease:"back.out(2)"}},{conta + 0.6:.3f});'
                       f'tl.to("#pz{n}",{{opacity:0,duration:0.2}},{e["a"]:.3f});')
        self.suono("livello", conta + 0.6, 0.45)
        if e.get("dopo"):
            t = e.get("dopo_da", conta + 1.5)
            self.decodifica(f"#pzl{n}", e["dopo"][0], t - 0.5, 0.35)
            self.decodifica(f"#pzs{n}", e["dopo"][1], t, 0.35)
            self.suono("ding", t, 0.35)
        self.nascondi.append((e["da"], e["a"] + 0.2))

    def cornice(self, e, telefono=False):
        """La persona rimpicciolita dentro una cornice luminosa (o un telefono) su sfondo scuro, titoli sopra."""
        da, a = e["da"], e["a"]
        n = len(self.corpo)
        s, y, raggio = (0.5, 70, 70) if telefono else (0.56, 110, 36)
        self.scuro(da, a)
        classe = "cam tel" if telefono else "cam cor"
        self.tl.append(f'tl.fromTo("#cam",{{scale:1,y:0,borderRadius:0}},{{scale:{s},y:{y},borderRadius:{raggio / s:.0f},duration:0.45,ease:"power3.inOut"}},{da:.3f});'
                       f'tl.set("#cam",{{attr:{{class:"{classe}"}},zIndex:7}},{da:.3f});'
                       f'tl.to("#cam",{{scale:1,y:0,borderRadius:0,duration:0.4,ease:"power3.inOut"}},{a - 0.4:.3f});'
                       f'tl.set("#cam",{{attr:{{class:"cam"}},zIndex:5}},{a:.3f});')
        if telefono:
            self.corpo.append(f'<div class="rec-tel" id="r{n}"><b></b></div><div class="rec-lab" id="rl{n}">● REC <span id="rt{n}">00:00:00</span></div>')
            self.tl.append(f'tl.fromTo("#r{n},#rl{n}",{{opacity:0}},{{opacity:1,duration:0.2}},{da + 0.4:.3f});'
                           f'tl.to("#r{n},#rl{n}",{{opacity:0,duration:0.15}},{a - 0.45:.3f});'
                           f'cronometro("#rt{n}",{da:.3f},{a:.3f});')
        self.suono("zoom", da - 0.05, 0.4, se_manca="transizione")
        self.suono("zoom", a - 0.45, 0.4)
        titoli = e.get("titoli", [])
        for k, (sopra, targa, t) in enumerate(titoli):
            fine = titoli[k + 1][2] if k + 1 < len(titoli) else a
            self.titolo(sopra, targa, t, fine, 240)
        if e.get("chat"):
            ch = e["chat"]
            self.corpo.append(f'<div class="prompt" id="pr{n}"><div class="pr-lab">● {html.escape(ch.get("etichetta", ""))}</div>'
                              f'<div id="prt{n}"></div><div class="invia" id="inv{n}">↑</div></div>')
            self.tl.append(f'tl.fromTo("#pr{n}",{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.3,ease:"power3.out"}},{ch["da"] - 0.26:.3f});'
                           f'scrivi("#prt{n}",{json.dumps(ch["testo"])},{ch["da"]:.3f},{ch["a"]:.3f});'
                           f'tl.fromTo("#inv{n}",{{scale:1}},{{scale:1.35,duration:0.12,yoyo:true,repeat:1}},{ch["a"] + 0.4:.3f});'
                           f'tl.to("#pr{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
            self.suono("tastiera", ch["da"], 0.35, dur=ch["a"] - ch["da"])  # solo mentre scrive
            self.suono("click", ch["a"] + 0.4, 0.4)
        if e.get("passi"):
            barra = "".join(f'<div class="passo"><div class="riemp" id="pb{n}_{k}"><span id="pk{n}_{k}">✓</span></div>'
                            f'<div class="pl">{html.escape(p)}</div></div>' for k, (p, _) in enumerate(e["passi"]))
            self.corpo.append(f'<div class="barra" id="bar{n}">{barra}</div>')
            self.tl.append(f'tl.fromTo("#bar{n}",{{y:80,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:"power3.out"}},{da + 0.4:.3f});'
                           f'tl.to("#bar{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
            for k, (_, t) in enumerate(e["passi"]):
                self.tl.append(f'tl.fromTo("#pb{n}_{k}",{{scaleX:0}},{{scaleX:1,duration:0.4,ease:"power2.out"}},{t:.3f});'
                               f'tl.fromTo("#pk{n}_{k}",{{scale:0}},{{scale:1,duration:0.25,ease:"back.out(3)"}},{t + 0.35:.3f});')
                self.suono("click", t + 0.35, 0.4)

    # ---------- effetti con il ritaglio della persona ----------
    def ritaglio(self, da, a):
        """La persona ritagliata dai secondi da-a (strumenti/ritaglio.py), come video trasparente nella pagina."""
        import ritaglio as rit
        p = rit.ritaglia(os.path.dirname(self.reel), da, a, f"rit-{da:.2f}-{a:.2f}")
        dest = os.path.join(self.assets, os.path.basename(p))
        if not os.path.exists(dest):
            shutil.copy2(p, dest)
        n = len(self.camera)
        self.camera.append(f'<video id="r{n}" class="rit" src="assets/{os.path.basename(p)}" muted playsinline '
                           f'data-start="{da:.3f}" data-media-start="0" data-duration="{a - da:.3f}"></video>')
        return f"#r{n}"

    def font_extra(self, nome):
        dest = os.path.join(self.assets, nome)
        if not os.path.exists(dest):
            shutil.copy2(os.path.join(STUDIO, "font", nome), dest)

    def suono_libreria(self, rel, da, vol=0.45):
        """Un suono della libreria (DATI/suoni/<rel>), per i momenti che lo stile non ha."""
        self.stile["suoni"].setdefault("_" + rel, trova(rel))
        self.suono("_" + rel, da, vol)

    def adesivo(self, e, faccia):
        """Adesivo: sulla parola l'immagine si ferma e diventi un adesivo fustellato (bordo bianco, ombra, un po'
        storto) attaccato su una pagina colorata, con le note scritte a mano attorno. La voce continua sotto.
        e = {"quando": secondo del fermo, "a": quando torna il video (facoltativo: senza, resta fino alla fine),
        "note": [["testo", secondo], ...] (al massimo 2, parole dette o scelte dall'utente), "pagina": "#colore"}."""
        import numpy as np
        from PIL import Image, ImageFilter
        from scipy import ndimage
        import ritaglio as rit
        c = self.stile["colori"]
        t, fine = e["quando"], e.get("a", self.D)
        im = rit.fotogramma(os.path.dirname(self.reel), t)
        taglio = int(min(faccia["mento"] + 380, 1919))   # taglio dritto sotto il petto: niente scrivania o mani in basso
        a_px = np.array(im.getchannel("A"))
        a_px[taglio:] = 0
        im.putalpha(Image.fromarray(a_px))
        al = a_px > 127
        bordo = ndimage.binary_dilation(al, iterations=22)          # il bordo bianco della fustella
        x0, y0, x1, y1 = Image.fromarray(bordo.astype(np.uint8) * 255).getbbox()
        bianco = Image.new("RGBA", im.size, (255, 255, 255, 0))
        bianco.putalpha(Image.fromarray((bordo * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
        bianco.alpha_composite(im)
        adesivo = bianco.crop((x0, y0, x1, y1))
        shutil.copy2(os.path.join(STUDIO, "font", "Caveat.ttf"), os.path.join(self.assets, "Caveat.ttf"))
        n = len(self.corpo)
        nome = f"adesivo-{n}.png"
        adesivo.save(os.path.join(self.assets, nome))
        w, h = adesivo.size
        k = min(1.0, 1150 / h, 900 / w)                              # grande, ma lascia posto alle note
        w, h = w * k, h * k
        sx, sy = 540 - w / 2, 960 - h / 2 + 90
        pagina = e.get("pagina", "#2346B8")
        timbro = e.get("timbro", "")
        tx, ty = sx + (faccia["sinistra"] - x0) * k, sy + (faccia["occhi"] - 230 - y0) * k  # vicino alla testa
        segni = (f'<div class="segni" id="a{len(self.corpo)}g" style="left:{tx - 90:.0f}px;top:{ty:.0f}px">'
                 '<i style="transform:rotate(-30deg)"></i><i style="transform:rotate(0deg);top:40px"></i>'
                 '<i style="transform:rotate(30deg);top:80px"></i></div>')
        note = []
        for j, (testo, quando) in enumerate((e.get("note") or [])[:2]):
            ny = 300 if j == 0 else 1520
            testo = re.sub(r"\*(.+?)\*", lambda m: f'<span style="color:{c["accento_luce"]};text-decoration:underline">{m[1]}</span>',
                           html.escape(testo))  # *parola* = colore d'accento
            note.append(f'<div class="nota" id="a{n}n{j}" style="top:{ny}px;transform:rotate({-5 if j == 0 else 3}deg)">'
                        f'{testo}</div>')
            self.tl.append(f'tl.fromTo("#a{n}n{j}",{{opacity:1,clipPath:"inset(0 100% 0 0)"}},{{opacity:1,clipPath:"inset(0 0% 0 0)",'
                           f'duration:0.5,ease:"none",immediateRender:false}},{max(quando, t + 0.35):.3f});')
            self.suono_libreria("mixkit/matita.mp3", max(quando, t + 0.35), 0.35)
        self.corpo.append(f'<div class="pagina" id="a{n}" style="background-color:{pagina}"><div class="raggi"></div>'
                          f'<img class="adesivo" id="a{n}s" src="assets/{nome}" style="left:{sx:.0f}px;top:{sy:.0f}px;'
                          f'width:{w:.0f}px;height:{h:.0f}px">{segni}'
                          + (f'<div class="timbro" id="a{n}t" style="color:{c["accento_luce"]};border-color:{c["accento_luce"]}">'
                             f'{html.escape(timbro.upper())}</div>' if timbro else "")
                          + f'{"".join(note)}</div>')
        self.tl.append(f'tl.fromTo("#a{n}g i",{{scaleX:0}},{{scaleX:1,duration:0.15,stagger:0.06,ease:"power2.out",immediateRender:false}},{t + 0.3:.3f});')
        if timbro:
            self.tl.append(f'tl.fromTo("#a{n}t",{{opacity:0,scale:2.2,rotation:-14}},{{opacity:1,scale:1,rotation:-8,duration:0.18,'
                           f'ease:"power4.in",immediateRender:false}},{t + 0.25:.3f});')
            self.suono("impatto", t + 0.43, 0.35)
        self.tl.append(f'tl.set("#a{n}",{{opacity:1}},{t:.3f});'
                       f'tl.fromTo("#a{n}s",{{scale:1.25,rotation:-12}},{{scale:1,rotation:-4,duration:0.28,ease:"back.out(2)",immediateRender:false}},{t:.3f});')
        self.flash(t, 0.6, "#FFFFFF")
        self.suono_libreria("mixkit/scatto-foto.mp3", t - 0.05, 0.45)
        self.suono("pop", t + 0.12, 0.45)
        if fine < self.D - 0.1:
            self.tl.append(f'tl.to("#a{n}s",{{y:-1500,rotation:-25,duration:0.35,ease:"power3.in"}},{fine - 0.35:.3f});'
                           f'tl.set("#a{n}",{{opacity:0}},{fine:.3f});')
            self.suono("transizione", fine - 0.35, 0.35)
        self.nascondi.append((t, fine))

    def viso(self, faccia, t):
        """Il centro degli occhi al secondo t (dai campioni di faccia.json), per mirare zoom e luce."""
        cs = faccia.get("campioni") or []
        if not cs:
            return 540, faccia["occhi"]
        c = min(cs, key=lambda x: abs(x["t"] - t))
        return c["x"] + c["l"] / 2, c["y"] + c["h"] * 0.42

    def zoom(self, e, faccia):
        """Zoom sul viso, non sul centro: "lento" entra piano, "scatto" entra di colpo con la scia, "fuori" torna
        indietro di scatto. e = {"mosse": [[da, arrivo, scala, "lento" | "scatto" | "fuori"], ...]}."""
        for da, arrivo, scala, tipo in e["mosse"]:
            x, y = self.viso(faccia, arrivo)
            self.tl.append(f'tl.set("#cam",{{transformOrigin:"{x:.0f}px {y:.0f}px"}},{max(da - 0.01, 0):.3f});')
            if tipo == "lento":
                self.tl.append(f'tl.to("#cam",{{scale:{scala},duration:{arrivo - da:.3f},ease:"sine.inOut"}},{da:.3f});')
            else:
                dur = 0.12 if tipo == "scatto" else 0.28
                self.tl.append(f'tl.to("#cam",{{scale:{scala},duration:{dur},ease:"{"power4.out" if tipo == "scatto" else "expo.out"}"}},{arrivo - dur:.3f});'
                               f'tl.fromTo("#bg",{{filter:"blur(7px)"}},{{filter:"blur(0px)",duration:{dur + 0.1:.2f},ease:"power2.out",immediateRender:false}},{arrivo - dur:.3f});')
                self.suono("transizione", arrivo - dur, 0.3)

    def schermo(self, e, faccia):
        """Schermo dietro di te: diventi piccolo in basso e dietro di te, a tutto schermo, c'è la cosa di cui parli
        (un video o una foto). e = {"da", "a", "file": video o foto (in DATI/clip, DATI/immagini o del lavoro),
        "lato": "destra" | "sinistra" | "centro"}."""
        da, a = e["da"], e["a"]
        cart = os.path.dirname(self.reel)
        p = next((q for q in (e["file"], os.path.join(cart, e["file"]), os.path.join(DATI, "clip", e["file"]),
                              os.path.join(DATI, "immagini", e["file"])) if os.path.isfile(q)), None)
        if not p:
            print(f'NOTA: non trovo {e["file"]} per lo schermo, lo salto')
            return
        n = len(self.camera)
        dest = f"schermo-{n}{os.path.splitext(p)[1]}"
        shutil.copy2(p, os.path.join(self.assets, dest))
        if p.lower().endswith((".mp4", ".mov", ".webm")):
            dentro = (f'<video id="sc{n}" class="schermo" src="assets/{dest}" muted playsinline data-start="{da:.3f}" '
                      f'data-media-start="0" data-duration="{a - da:.3f}"></video>')
        else:
            dentro = f'<img id="sc{n}" class="schermo" src="assets/{dest}">'
        self.camera.insert(0, dentro)
        sel = self.ritaglio(da - 0.1, a + 0.1)
        taglio = min(faccia["mento"] + 380, 1919)  # la persona finisce con un taglio dritto, appoggiata al bordo
        x = {"sinistra": 300, "centro": 540}.get(e.get("lato"), 780)
        k = 0.56
        self.tl.append(f'tl.set("{sel}",{{opacity:1,clipPath:"inset(0 0 {1920 - taglio:.0f}px 0)",transformOrigin:"540px {taglio:.0f}px"}},{da:.3f});'
                       f'tl.to("{sel}",{{scale:{k},x:{x - 540},y:{1920 - taglio},duration:0.45,ease:"power3.inOut"}},{da:.3f});'
                       f'tl.fromTo("#sc{n}",{{opacity:0,scale:1.08}},{{opacity:1,scale:1,duration:0.45,ease:"power2.out",immediateRender:false}},{da:.3f});'
                       f'tl.to("{sel}",{{scale:1,x:0,y:0,duration:0.4,ease:"power3.inOut"}},{a - 0.4:.3f});'
                       f'tl.to("#sc{n}",{{opacity:0,duration:0.4}},{a - 0.4:.3f});'
                       f'tl.set("{sel}",{{opacity:0}},{a:.3f});')
        self.suono("transizione", da, 0.35)
        self.suono("transizione", a - 0.4, 0.3)
        self.nascondi.append((da, a))

    def luce(self, e, faccia):
        """Luce: la stanza va quasi al buio e fuori fuoco, resti tu in un cerchio di luce, e fino a tre parole
        compaiono quando le dici. e = {"da", "a", "parole": [["TESTO", secondo], ...]}."""
        c = self.stile["colori"]
        da, a = e["da"], e["a"]
        sel = self.ritaglio(da - 0.1, a + 0.1)
        x, y = self.viso(faccia, da)
        n = len(self.camera)
        self.camera.insert(0, f'<div class="pozza" id="lz{n}" style="background:radial-gradient(520px 620px at {x:.0f}px {y + 120:.0f}px,'
                              f'rgba(160,190,255,.30),rgba(120,150,230,.10) 55%,rgba(120,150,230,0) 78%)"></div>')
        m = len(self.corpo)
        cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
        posti = [max(cima - 260, 230), faccia["mento"] + 140, faccia["mento"] + 330]  # sopra la testa, poi sul petto
        parole = "".join(f'<div class="lparola" id="l{m}p{j}" style="top:{posti[j]:.0f}px;'
                         f'{"color:" + c["accento_luce"] if j % 2 else ""};font-size:{min(170, int(980 / (max(len(t), 3) * 0.62)))}px">'
                         f'{html.escape(t.lower())}</div>' for j, (t, _) in enumerate(e.get("parole", [])[:3]))
        self.corpo.append(f'<div class="lbuio" id="l{m}"></div>{parole}')
        self.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});'
                       f'tl.fromTo("#bg",{{filter:"brightness(1) blur(0px) saturate(1) hue-rotate(0deg)"}},{{filter:"brightness(0.16) blur(10px) saturate(0.5) hue-rotate(-12deg)",duration:0.6,ease:"power2.inOut",immediateRender:false}},{da:.3f});'
                       f'tl.to(["#lz{n}","#l{m}"],{{opacity:1,duration:0.6}},{da:.3f});'
                       f'tl.to("#bg",{{filter:"brightness(1) blur(0px) saturate(1)",duration:0.5,ease:"power2.inOut"}},{a - 0.5:.3f});'
                       f'tl.to(["#lz{n}","#l{m}","#l{m}p0","#l{m}p1","#l{m}p2"],{{opacity:0,duration:0.5}},{a - 0.5:.3f});'
                       f'tl.set("{sel}",{{opacity:0}},{a:.3f});tl.set("#bg",{{filter:"none"}},{a:.3f});')
        for j, (t, quando) in enumerate(e.get("parole", [])[:3]):
            self.tl.append(f'tl.fromTo("#l{m}p{j}",{{opacity:0,y:30,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power3.out",immediateRender:false}},{quando:.3f});')
            self.suono("pop", quando, 0.3)
        self.suono("attesa", da, 0.25)
        self.nascondi.append((da, a))

    def flash(self, da, forza, colore="#FFF4E8"):
        n = len(self.corpo)
        self.corpo.append(f'<div class="lampo" id="f{n}" style="background:{colore}"></div>')
        self.tl.append(f'tl.fromTo("#f{n}",{{opacity:{forza}}},{{opacity:0,duration:0.28,ease:"power2.out",immediateRender:false}},{da:.3f});')

    def dietro(self, e, faccia):
        """Parola dietro la testa: la stanza si spegne mentre tu resti illuminato, la parola forte sbatte dietro la
        tua testa con un lampo e un colpo di camera, le luci tornano di scatto. e = {"da": inizio della frase,
        "parola": "SEMPLICE", "quando": secondo in cui la dici, "a": quando le luci tornano}."""
        c = self.stile["colori"]
        da, quando, a = e["da"], e["quando"], e["a"]
        sel = self.ritaglio(da - 0.1, a + 0.1)
        testo = e["parola"].upper()
        dim = min(320, int(980 / (max(len(testo), 3) * 0.88)))
        cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95  # dove finisce la testa
        y = max(cima - dim * 0.3, 230)  # la testa copre la parte bassa della parola
        n = len(self.camera)
        self.camera.insert(0, f'<div class="pdietro" id="p{n}" style="top:{y:.0f}px;font-size:{dim}px;color:{c["accento"]};'
                              f'text-shadow:0 0 50px {c["accento_luce"]}99">{html.escape(testo)}</div>')
        m = len(self.corpo)
        self.corpo.append(f'<div class="buio" id="v{m}"></div>')
        stanza = "brightness(0.46) contrast(1.1) saturate(0.62)"
        self.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});'
                       f'tl.fromTo("#bg",{{filter:"brightness(1) contrast(1) saturate(1)"}},{{filter:"{stanza}",duration:{min(0.8, quando - da):.3f},ease:"power2.inOut",immediateRender:false}},{da:.3f});'
                       f'tl.to("#v{m}",{{opacity:1,duration:{min(0.8, quando - da):.3f}}},{da:.3f});'
                       f'tl.fromTo("#cam",{{scale:1}},{{scale:1.05,duration:{quando - da:.3f},ease:"power1.in",immediateRender:false}},{da:.3f});'
                       f'tl.set("#p{n}",{{opacity:1}},{quando:.3f});'
                       f'tl.fromTo("#p{n}",{{scale:1.9,filter:"blur(14px)"}},{{scale:1,filter:"blur(0px)",duration:0.2,ease:"expo.out",immediateRender:false}},{quando:.3f});'
                       f'tl.fromTo("#cam",{{scale:1.1}},{{scale:1.065,duration:0.34,ease:"power3.out",immediateRender:false}},{quando:.3f});'
                       f'tl.fromTo("#cam",{{x:0,y:0}},{{keyframes:[{{x:-6,y:4,duration:.033}},{{x:5,y:-4,duration:.033}},{{x:-3,y:2,duration:.033}},{{x:0,y:0,duration:.033}}],immediateRender:false}},{quando:.3f});'
                       f'tl.to("#p{n}",{{scale:1.035,duration:{max(a - quando - 0.22, 0.05):.3f},ease:"none"}},{quando + 0.21:.3f});'
                       f'tl.set("#bg",{{filter:"none"}},{a:.3f});tl.set(["{sel}","#p{n}","#v{m}"],{{opacity:0}},{a:.3f});'
                       f'tl.fromTo("#cam",{{scale:1.065}},{{scale:1,duration:0.34,ease:"power2.out",immediateRender:false}},{a:.3f});')
        self.flash(quando, 0.28)
        self.flash(a, 0.5, "#FFFFFF")
        self.suono("attesa", max(da, quando - 1.6), 0.3)
        self.suono("impatto", quando, 0.5)
        self.suono("transizione", a, 0.35)
        self.nascondi.append((quando, a))

    def commento(self, e, faccia):
        """Commento: sotto il mento sale il campo dei commenti, la parola si scrive da sola, parte il commento con il
        cuore, poi arriva la tua risposta con il bottone giallo. e = {"da": quando sale il campo, "parola": "INFO",
        "scrivi": quando dici la parola, "invia": (facoltativo), "risposta": "Te l'ho mandato in direct",
        "risposta_da": secondo, "chip": "Apri il link" (facoltativo), "a": quando sparisce}."""
        da, a, parola = e["da"], e.get("a", self.D), e["parola"].upper()
        scrivi = e.get("scrivi", da + 0.4)
        fine_scrivi = scrivi + 0.11 * len(parola)
        invia = e.get("invia", fine_scrivi + 0.3)
        risp = e.get("risposta_da", invia + 0.9)
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        volto = f"volto-{n}.jpg"   # la tua faccia nel tondo della risposta, dal fotogramma del video
        lato = faccia["destra"] - faccia["sinistra"]
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{da:.2f}", "-i", os.path.join(self.assets, "tagliato.mp4"),
                        "-frames:v", "1", "-vf", f"crop={lato}:{lato}:{faccia['sinistra']}:{max(faccia['occhi'] - lato // 2, 0)},scale=120:120",
                        os.path.join(self.assets, volto)], check=True)
        y = min(faccia["mento"] + 60, 1300)
        chip = f'<span class="cm-chip" id="cm{n}k"><b>⛓</b>{html.escape(e["chip"])}</span>' if e.get("chip") else ""
        omino = '<span class="cm-av"><i></i></span>'
        self.corpo.append(
            f'<div class="cm" id="cm{n}" style="top:{y}px">'
            f'<div class="cm-campo" id="cm{n}f">{omino}<span class="cm-ph" id="cm{n}h">Aggiungi un commento...</span>'
            f'<span class="cm-tx" id="cm{n}t"></span><span class="cm-car" id="cm{n}c"></span><span class="cm-in" id="cm{n}i">↑</span></div>'
            f'<div class="cm-riga" id="cm{n}p">{omino}<div class="cm-bol"><small>tu</small><b>{html.escape(parola)}</b>'
            f'<i class="cm-cuore" id="cm{n}u">♥</i></div></div>'
            f'<div class="cm-filo" id="cm{n}l"></div>'
            f'<div class="cm-riga cm-r" id="cm{n}r"><img class="cm-av piccolo" src="assets/{volto}"><div class="cm-scura" id="cm{n}s">'
            f'<span class="cm-attesa" id="cm{n}d"></span><span id="cm{n}rt" class="cm-rt">{html.escape(e["risposta"])}</span>{chip}</div></div></div>')
        T = self.tl.append
        T(f'tl.set("#cm{n}",{{opacity:1}},{da:.3f});'
          f'tl.fromTo("#cm{n}f",{{y:40,opacity:0}},{{y:0,opacity:1,duration:0.3,ease:"power3.out",immediateRender:false}},{da:.3f});'
          f'tl.set("#cm{n}h",{{display:"none"}},{scrivi:.3f});'
          f'tl.set("#cm{n}f",{{borderColor:"#F4E06D",boxShadow:"0 0 0 2px rgba(244,224,109,.35),0 10px 30px rgba(0,0,0,.35)"}},{scrivi - 0.05:.3f});'
          f'tl.set("#cm{n}i",{{backgroundColor:"#F4E06D",color:"#141414"}},{fine_scrivi:.3f});'
          f'tl.fromTo("#cm{n}c",{{opacity:1}},{{opacity:0,duration:0.22,repeat:{max(int((invia - scrivi + 0.2) / 0.22), 1)},yoyo:true,immediateRender:false}},{scrivi - 0.05:.3f});'
          f'tl.fromTo("#cm{n}i",{{scale:1}},{{keyframes:[{{scale:0.82,duration:0.07}},{{scale:1.1,duration:0.09}},{{scale:1,duration:0.08}}],immediateRender:false}},{invia - 0.1:.3f});'
          f'tl.set("#cm{n}f",{{opacity:0}},{invia + 0.06:.3f});'
          f'tl.fromTo("#cm{n}p",{{opacity:0,scale:0.85,y:12}},{{opacity:1,scale:1,y:0,duration:0.26,ease:"back.out(2)",immediateRender:false}},{invia + 0.06:.3f});'
          f'tl.fromTo("#cm{n}u",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.28,ease:"back.out(3)",immediateRender:false}},{invia + 0.4:.3f});'
          f'tl.fromTo("#cm{n}l",{{scaleY:0,opacity:1}},{{scaleY:1,opacity:1,duration:0.2,ease:"power2.out",immediateRender:false}},{invia + 0.55:.3f});'
          f'tl.fromTo("#cm{n}r",{{opacity:0,x:-14}},{{opacity:1,x:0,duration:0.22,ease:"power3.out",immediateRender:false}},{min(invia + 0.7, risp - 0.3):.3f});'
          f'tl.set("#cm{n}d",{{display:"none"}},{risp:.3f});tl.set("#cm{n}rt",{{display:"inline"}},{risp:.3f});'
          f'tl.to("#cm{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
        if e.get("chip"):
            T(f'tl.fromTo("#cm{n}k",{{scale:0.4,opacity:0}},{{scale:1,opacity:1,duration:0.26,ease:"back.out(2.5)",immediateRender:false}},{risp + 0.3:.3f});')
            self.suono("pop", risp + 0.3, 0.3)
        self.tl.append(f'scrivi("#cm{n}t",{json.dumps(parola)},{scrivi:.3f},{fine_scrivi:.3f});')
        self.suono("tastiera", scrivi, 0.3, dur=fine_scrivi - scrivi + 0.05)
        self.suono("click", invia - 0.1, 0.45)
        self.suono("pop", invia + 0.06, 0.4)
        self.suono("ding", risp, 0.3)
        self.nascondi.append((da, a))

    def numero(self, e, faccia):
        """Numero gigante: il numero che dici compare enorme sul petto, color crema, e sotto una riga piccola in
        maiuscolo che cambia con le parole dopo. e = {"da": quando lo dici, "a": fine, "numero": "14,000",
        "righe": [["FOLLOWER", secondo], ["IN 7 GIORNI", secondo]]}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        testo = str(e["numero"])
        dim = min(250, int(1500 / max(len(testo) * 0.62 + 0.4, 2.5)))
        y = min(faccia["mento"] + 120, 1240)
        righe = e.get("righe", [])[:3]
        self.corpo.append(f'<div class="nm" id="nm{n}" style="top:{y}px"><div class="nm-n" style="font-size:{dim}px">{html.escape(testo)}</div>'
                          + "".join(f'<div class="nm-r" id="nm{n}r{j}">{html.escape(r.upper())}</div>' for j, (r, _) in enumerate(righe))
                          + '</div>')
        self.tl.append(f'tl.fromTo("#nm{n}",{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:0.12,ease:"power2.out",immediateRender:false}},{da:.3f});'
                       f'tl.to("#nm{n}",{{opacity:0,duration:0.1}},{a - 0.1:.3f});')
        for j, (_, quando) in enumerate(righe):
            fine = righe[j + 1][1] if j + 1 < len(righe) else a
            self.tl.append(f'tl.set("#nm{n}r{j}",{{opacity:1}},{quando:.3f});tl.set("#nm{n}r{j}",{{opacity:0}},{fine:.3f});')
        self.suono("impatto", da, 0.35)
        self.nascondi.append((da, a))

    def etichette(self, e, faccia):
        """Fermo con etichette: con un lampo morbido l'immagine si ferma e si scurisce (la voce continua), e delle
        etichette crema numerate ti indicano con una linea sottile: le parole si scrivono una alla volta.
        e = {"quando": secondo del fermo, "a": quando riparte, "voci": [["testo", secondo], ...] (al massimo 3)}."""
        t, a = e["quando"], e["a"]
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        nome = f"fermo-{n}.jpg"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", os.path.join(self.assets, "tagliato.mp4"), "-frames:v", "1",
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-q:v", "3",
                        os.path.join(self.assets, nome)], check=True)
        self.camera.append(f'<img class="fermo" id="fe{n}c" src="assets/{nome}"><div class="fe-buio" id="fe{n}b"></div>')
        cx = (faccia["sinistra"] + faccia["destra"]) / 2
        cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
        # punto indicato -> etichetta: in cima alla testa (carta in alto a sinistra), sul petto (carta in basso a destra),
        # sulla spalla (carta in basso a sinistra). La linea parte dal bordo della carta più vicino al punto.
        posti = [((cx - 20, cima + 25), (50, max(cima - 330, 150)), "giu"),
                 ((cx + 90, faccia["mento"] + 160), (min(cx - 20, 1080 - 520), faccia["mento"] + 330), "su"),
                 ((faccia["sinistra"] + 30, faccia["mento"] + 110), (50, faccia["mento"] + 470), "su")]
        linee, carte = [], []
        for j, (testo, quando) in enumerate(e["voci"][:3]):
            (px, py), (lx, ly), lato = posti[j]
            ax = min(max(px, lx + 120), lx + 380)
            ay = ly + 96 if lato == "giu" else ly
            lung = math.hypot(px - ax, py - ay)
            linee.append(f'<line id="fe{n}l{j}" x1="{ax:.0f}" y1="{ay:.0f}" x2="{px:.0f}" y2="{py:.0f}" stroke-dasharray="{lung:.0f}" '
                         f'stroke-dashoffset="{lung:.0f}"/><g id="fe{n}o{j}" opacity="0"><circle cx="{px:.0f}" cy="{py:.0f}" r="17" class="anello"/>'
                         f'<circle cx="{px:.0f}" cy="{py:.0f}" r="9" class="punto"/></g>')
            parole = testo.split()
            carte.append(f'<div class="et" id="fe{n}k{j}" style="left:{lx}px;top:{ly}px"><span class="et-n">0{j + 1}</span>'
                         + "".join(f'<span class="et-p" id="fe{n}k{j}w{w}">{html.escape(p)}</span>' for w, p in enumerate(parole)) + '</div>')
            self.tl.append(f'tl.fromTo("#fe{n}k{j}",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.18,ease:"power2.out",immediateRender:false}},{quando:.3f});'
                           f'tl.fromTo("#fe{n}l{j}",{{strokeDashoffset:{lung:.0f}}},{{strokeDashoffset:0,duration:0.3,ease:"power2.out",immediateRender:false}},{quando + 0.08:.3f});'
                           f'tl.fromTo("#fe{n}o{j}",{{opacity:0,scale:0.3,transformOrigin:"50% 50%"}},{{opacity:1,scale:1,duration:0.2,ease:"back.out(3)",immediateRender:false}},{quando + 0.32:.3f});')
            for w in range(len(parole)):   # le parole della carta arrivano una alla volta
                self.tl.append(f'tl.fromTo("#fe{n}k{j}w{w}",{{opacity:0}},{{opacity:1,duration:0.08,immediateRender:false}},{quando + 0.05 + w * 0.16:.3f});')
            self.suono("pop", quando, 0.35)
        self.corpo.append(f'<div class="fe" id="fe{n}"><svg width="1080" height="1920" class="fe-svg">{"".join(linee)}</svg>{"".join(carte)}</div>')
        self.tl.append(f'tl.set(["#fe{n}","#fe{n}c"],{{opacity:1}},{t:.3f});'
                       f'tl.fromTo("#fe{n}b",{{opacity:0}},{{opacity:1,duration:0.35,ease:"power2.out",immediateRender:false}},{t:.3f});'
                       f'tl.set(["#fe{n}","#fe{n}c","#fe{n}b"],{{opacity:0}},{a:.3f});')
        self.flash(t, 0.45, "#FFFFFF")
        self.suono("click", t, 0.5)
        self.nascondi.append((t, a))

    def neon(self, e, faccia):
        """Insegna al neon: la frase, scritta a mano come un tubo di vetro, è appesa al muro accanto alla tua testa.
        All'inizio è spenta, poi si accende sfarfallando, la stanza si abbassa e il muro attorno prende la sua luce.
        Tu resti davanti (ritaglio): se muovi le mani passano sopra la scritta.
        e = {"da": quando compare spenta, "quando": quando si accende (facoltativo), "a": quando si spegne,
        "testo": "più semplice" (2-3 parole: l'ultima va sulla seconda riga, sottolineata), "colore": "#FFD84A"}."""
        da, a, testo = e["da"], e["a"], e["testo"].strip()
        quando = e.get("quando", da + 0.8)
        col = e.get("colore", "#FFD84A")
        shutil.copy2(os.path.join(STUDIO, "font", "IndieFlower.ttf"), os.path.join(self.assets, "IndieFlower.ttf"))
        sel = self.ritaglio(da, a)
        parole = testo.split()
        righe = [" ".join(parole[:-1]), parole[-1]] if len(parole) > 1 else [testo]
        # dalla parte del muro con più spazio, accanto alla testa: grande quanto c'è posto (al massimo 60 px dietro la testa)
        sinistra = faccia["sinistra"] > 1080 - faccia["destra"]
        posto = (faccia["sinistra"] if sinistra else 1080 - faccia["destra"]) - 40 + 60
        lungo = max(max(len(r) for r in righe), 3)
        dim = max(min(118, int(posto / (lungo * 0.46 + 0.6))), 64)
        larg = lungo * dim * 0.46 + dim * 0.6
        x = max(faccia["sinistra"] + 60 - larg - 10, 30) if sinistra else min(faccia["destra"] - 60 + 10, 1080 - larg - 30)
        cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
        y = cima + 10
        def insegna(classe, stile=""):
            r2 = (f'<br><span class="ne-r2">{html.escape(righe[1])}<i class="ne-sott"></i></span>' if len(righe) > 1 else "")
            return f'<div class="{classe}"{stile}>{html.escape(righe[0])}{r2}</div>'
        luce = f' style="color:#FFF6CF;text-shadow:0 0 3px #FFF8DC,0 0 9px {col},0 0 22px {col},0 0 46px {col}cc,0 0 90px {col}88"'
        n = len(self.camera)
        self.camera.insert(0,
            f'<div class="ne-alone" id="ne{n}a" style="left:{x + larg / 2 - 420:.0f}px;top:{y + dim - 380:.0f}px;'
            f'background:radial-gradient(closest-side,{col}99,{col}33 55%,{col}00)"></div>'
            f'<div class="neon" id="ne{n}" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{dim}px">'
            + insegna("ne-spento") + f'<div class="ne-acceso" id="ne{n}o">' + insegna("", luce) + '</div></div>')
        stanza = "brightness(0.74) saturate(0.92)"
        T = self.tl.append
        T(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
          f'tl.fromTo("#ne{n}",{{opacity:0}},{{opacity:1,duration:0.2,immediateRender:false}},{da:.3f});'
          f'tl.fromTo("#ne{n}o",{{opacity:0}},{{keyframes:[{{opacity:0.85,duration:0.04}},{{opacity:0.2,duration:0.07}},{{opacity:0.95,duration:0.05}},'
          f'{{opacity:0.4,duration:0.1}},{{opacity:1,duration:0.06}},{{opacity:0.75,duration:0.06}},{{opacity:1,duration:0.1}}],immediateRender:false}},{quando:.3f});'
          f'tl.fromTo("#ne{n}a",{{opacity:0}},{{opacity:0.6,duration:0.5,immediateRender:false}},{quando + 0.1:.3f});'
          f'tl.fromTo(["#bg","{sel}"],{{filter:"brightness(1) saturate(1)"}},{{filter:"{stanza}",duration:0.55,ease:"power1.inOut",immediateRender:false}},{quando + 0.2:.3f});'
          f'tl.to(["#ne{n}","#ne{n}a"],{{opacity:0,duration:0.25}},{a - 0.25:.3f});'
          f'tl.to(["#bg","{sel}"],{{filter:"brightness(1) saturate(1)",duration:0.25}},{a - 0.25:.3f});')
        self.suono("glitch", quando, 0.25)

    def percorso(self, e):
        """Percorso su carta: taglio netto su un fondo verde scurissimo e il metodo si costruisce dall'alto in basso:
        un'etichetta piccola tra parentesi, un titolo in corsivo che entra lettera per lettera, poi i passi uniti da
        linee sottili (uno in grassetto, uno in corsivo, alternati). Un passo può crescere: "edits" -> "edits + posts".
        e = {"da", "a", "etichetta": "IL MIO METODO", "titolo": "dalle domande ai contatti",
        "passi": [["domande", secondo], ["+ contenuti", secondo, "stessa riga"], ["contatti", secondo]]}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        shutil.copy2(os.path.join(STUDIO, "font", "InstrumentSerif-Italic.ttf"), os.path.join(self.assets, "InstrumentSerif-Italic.ttf"))
        n = len(self.corpo)
        titolo = e.get("titolo", "")
        lettere = "".join(f'<span class="pc-l" id="pc{n}t{k}">{html.escape(c)}</span>' if c != " " else " " for k, c in enumerate(titolo))
        righe_tit = 1 if len(titolo) <= 16 else 2
        alto = 640 - (righe_tit - 1) * 50
        pezzi = [f'<div class="pc-lab" style="top:{alto}px">[{html.escape(e.get("etichetta", "IL METODO").upper())}]</div>',
                 f'<div class="pc-tit" style="top:{alto + 40}px">{lettere}</div>']
        k_lettera = 0
        for k, c in enumerate(titolo):   # il titolo entra lettera per lettera, sfocato
            if c != " ":
                self.tl.append(f'tl.fromTo("#pc{n}t{k}",{{opacity:0,filter:"blur(10px)"}},{{opacity:1,filter:"blur(0px)",duration:0.35,ease:"power2.out",immediateRender:false}},{da + 0.15 + k_lettera * 0.035:.3f});')
                k_lettera += 1
        y = alto + 40 + righe_tit * 100 + 20
        riga, j_riga = -1, 0
        for j, passo in enumerate(e.get("passi", [])[:5]):
            testo, quando = passo[0], passo[1]
            if len(passo) > 2 and riga >= 0:   # "stessa riga": si aggiunge al passo sopra
                pezzi.append(f'<span class="pc-agg" id="pc{n}p{j}"> {html.escape(testo)}</span>')
                pezzi[riga] = pezzi[riga].replace("</div>", pezzi.pop() + "</div>", 1)
            else:
                stile = "pc-passo" if j_riga % 2 == 0 else "pc-passo serif"
                pezzi.append(f'<div class="pc-filo" id="pc{n}f{j}" style="top:{y}px"></div>')
                pezzi.append(f'<div class="{stile}" style="top:{y + 84}px"><span id="pc{n}p{j}">{html.escape(testo)}</span></div>')
                riga = len(pezzi) - 1
                self.tl.append(f'tl.fromTo("#pc{n}f{j}",{{scaleY:0}},{{scaleY:1,duration:0.3,ease:"power2.out",immediateRender:false}},{quando - 0.3:.3f});')
                y += 170
                j_riga += 1
            self.tl.append(f'tl.fromTo("#pc{n}p{j}",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:0.3,ease:"power2.out",immediateRender:false}},{quando:.3f});')
            self.suono("pop", quando, 0.3)
        self.corpo.append(f'<div class="pc" id="pc{n}">{"".join(pezzi)}</div>')
        self.tl.append(f'tl.set("#pc{n}",{{opacity:1}},{da:.3f});tl.set("#pc{n}",{{opacity:0}},{a:.3f});')
        self.suono("transizione", da - 0.1, 0.3)
        self.nascondi.append((da, a))

    def checklist(self, e, faccia):
        """Checklist: una scheda di vetro scuro si costruisce sul muro (o sotto il mento, se sopra la testa non c'è
        posto): titolo piccolo, contatore "0 di 3", barra a segmenti, e ogni passo si spunta in giallo quando lo dici.
        Alla fine il bordo si accende e brillano due stelline. e = {"da", "a", "titolo": "TUTTO QUELLO CHE SERVE",
        "voci": [["Domande nelle storie", secondo], ...] (al massimo 4)}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        voci = e["voci"][:4]
        n = len(self.corpo)
        cima = faccia["occhi"] - (faccia["mento"] - faccia["occhi"]) * 0.95
        alt = 190 + len(voci) * 112
        sopra = cima - 60 >= alt + 150
        y = 150 if sopra else min(faccia["mento"] + 50, 1900 - alt - 260)
        segmenti = "".join(f'<i><b id="ck{n}s{j}"></b></i>' for j in range(len(voci)))
        righe = "".join(f'<div class="ck-riga" id="ck{n}r{j}"><span class="ck-tondo" id="ck{n}o{j}"><svg viewBox="0 0 24 24"><path d="M6 12.5l4 4 8-9"/></svg></span>'
                        f'<span class="ck-vuoto" id="ck{n}v{j}"></span><span class="ck-tx" id="ck{n}t{j}">{html.escape(t)}</span></div>'
                        for j, (t, _) in enumerate(voci))
        self.corpo.append(f'<div class="ck" id="ck{n}" style="top:{y}px"><div class="ck-testa"><span class="ck-lab"><i></i>'
                          f'{html.escape(e.get("titolo", "TUTTO QUELLO CHE SERVE").upper())}</span><span class="ck-conta" id="ck{n}c">0 di {len(voci)}</span></div>'
                          f'<div class="ck-barra">{segmenti}</div>{righe}<em class="ck-stella" id="ck{n}x">✦</em><em class="ck-stella b" id="ck{n}y">✦</em></div>')
        T = self.tl.append
        T(f'tl.fromTo("#ck{n}",{{opacity:0,scale:0.94,filter:"blur(12px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.45,ease:"power3.out",immediateRender:false}},{da:.3f});'
          f'tl.to("#ck{n}",{{opacity:0,scale:0.97,duration:0.25}},{a - 0.25:.3f});')
        for j, (_, quando) in enumerate(voci):
            spunta = quando + 0.35
            T(f'tl.set("#ck{n}v{j}",{{display:"none"}},{quando:.3f});'
              f'tl.fromTo("#ck{n}t{j}",{{opacity:0,filter:"blur(8px)",x:-10}},{{opacity:1,filter:"blur(0px)",x:0,duration:0.3,ease:"power2.out",immediateRender:false}},{quando:.3f});'
              f'tl.set("#ck{n}r{j}",{{backgroundColor:"rgba(255,255,255,0.07)"}},{quando:.3f});'
              f'tl.set("#ck{n}t{j}",{{color:"#F4E06D"}},{spunta:.3f});'
              f'tl.set("#ck{n}o{j}",{{backgroundColor:"#F4E06D",borderColor:"#F4E06D"}},{spunta:.3f});tl.set("#ck{n}o{j} svg",{{opacity:1}},{spunta:.3f});'
              f'tl.fromTo("#ck{n}o{j}",{{scale:0.6}},{{scale:1,duration:0.3,ease:"back.out(3)",immediateRender:false}},{spunta:.3f});'
              f'tl.fromTo("#ck{n}s{j}",{{scaleX:0}},{{scaleX:1,duration:0.35,ease:"power2.out",immediateRender:false}},{spunta:.3f});'
              f'tl.set("#ck{n}c",{{textContent:"{j + 1} di {len(voci)}"}},{spunta:.3f});'
              f'tl.set("#ck{n}t{j}",{{color:"#FFFFFF"}},{spunta + 0.7:.3f});tl.set("#ck{n}r{j}",{{backgroundColor:"rgba(255,255,255,0)"}},{spunta + 0.7:.3f});')
            self.suono("pop", spunta, 0.35)
        fine = voci[-1][1] + 0.5
        T(f'tl.set("#ck{n}",{{borderColor:"rgba(244,224,109,0.85)",boxShadow:"0 0 0 2px rgba(244,224,109,0.25),0 20px 60px rgba(0,0,0,0.45)"}},{fine:.3f});'
          f'tl.set("#ck{n}c",{{backgroundColor:"#F4E06D",color:"#141414"}},{fine:.3f});'
          f'tl.fromTo(["#ck{n}x","#ck{n}y"],{{opacity:0,scale:0.2,rotate:0}},{{opacity:1,scale:1,rotate:90,duration:0.5,ease:"back.out(2)",immediateRender:false}},{fine:.3f});')
        self.suono("ding", fine, 0.3)
        if not sopra:
            self.nascondi.append((da, a))

    def contachilometri(self, e, faccia):
        """Contachilometri: in alto un pannello scuro con le cifre in caselle che girano come un contachilometri fino al
        numero detto (una lettera dopo, tipo la "s" di 100s, resta gialla), sotto una riga gialla e l'etichetta.
        Il numero dopo arriva grande e quello prima si fa piccolo a sinistra.
        e = {"da", "a", "numeri": [{"valore": "15", "etichetta": "DOMANDE", "sotto": "ogni mese", "da": secondo}, ...]}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        numeri = e["numeri"][:2]
        pezzi = []
        for k, nu in enumerate(numeri):
            celle = []
            for c, ch in enumerate(str(nu["valore"])):
                if ch.isdigit():
                    striscia = "".join(f"<b>{d % 10}</b>" for d in range(20 + int(ch) + 1))
                    celle.append(f'<span class="od-cella"><span class="od-str" id="od{n}k{k}c{c}">{striscia}</span></span>')
                else:
                    celle.append(f'<span class="od-segno">{html.escape(ch)}</span>')
            sotto = f'<div class="od-sotto" id="od{n}k{k}u">{html.escape(nu.get("sotto", "").upper())}</div>' if nu.get("sotto") else ""
            pezzi.append(f'<div class="od" id="od{n}k{k}"><div class="od-pann">{"".join(celle)}</div>'
                         f'<div class="od-lab"><span>{html.escape(nu.get("etichetta", "").upper())}</span></div>{sotto}</div>')
        self.corpo.append(f'<div class="ods" id="od{n}">{"".join(pezzi)}</div>')
        T = self.tl.append
        T(f'tl.set("#od{n}",{{opacity:1}},{da:.3f});tl.to("#od{n}",{{opacity:0,duration:0.25}},{a - 0.25:.3f});')
        for k, nu in enumerate(numeri):
            t = nu.get("da", da)
            T(f'tl.fromTo("#od{n}k{k}",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:0.3,ease:"power3.out",immediateRender:false}},{t - 0.3:.3f});')
            for c, ch in enumerate(str(nu["valore"])):
                if ch.isdigit():
                    passi = 20 + int(ch)
                    T(f'tl.fromTo("#od{n}k{k}c{c}",{{y:0,filter:"blur(5px)"}},{{y:{-passi * 150},filter:"blur(0px)",duration:{0.9 + c * 0.12:.2f},ease:"power3.out",immediateRender:false}},{t:.3f});')
            if nu.get("sotto"):
                T(f'tl.fromTo("#od{n}k{k}u",{{opacity:0}},{{opacity:1,duration:0.25,immediateRender:false}},{nu.get("sotto_da", t + 1.2):.3f});')
            if k > 0:   # quello prima si fa piccolo e va a sinistra
                T(f'tl.to("#od{n}k{k - 1}",{{scale:0.48,x:-420,y:-40,duration:0.4,ease:"power3.inOut"}},{t - 0.35:.3f});')
            self.suono("livello", t + 0.8, 0.35)

    def pillole(self, e, faccia):
        """Pillole in fila: mentre fai un elenco, sotto i sottotitoli compare una pillola con il bordo bianco per ogni
        cosa che nomini, una accanto all'altra. I sottotitoli restano. e = {"a": fine, "voci": [["brand", secondo], ...]}."""
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        voci = e["voci"][:5]
        y = min(faccia["mento"] + 300, 1400)
        self.corpo.append(f'<div class="pl" id="pl{n}" style="top:{y}px">'
                          + "".join(f'<span class="pl-p" id="pl{n}p{j}">{html.escape(t)}</span>' for j, (t, _) in enumerate(voci)) + '</div>')
        self.tl.append(f'tl.set("#pl{n}",{{opacity:1}},{voci[0][1]:.3f});tl.to("#pl{n}",{{opacity:0,duration:0.25}},{e["a"] - 0.25:.3f});')
        for j, (_, quando) in enumerate(voci):
            self.tl.append(f'tl.fromTo("#pl{n}p{j}",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.28,ease:"back.out(2.4)",immediateRender:false}},{quando:.3f});')
            self.suono("pop", quando, 0.3)

    def prompt(self, e, faccia):
        """Prompt che si scrive: sul petto un riquadro di vetro con la scritta "prompt" sul bordo, e dentro si scrive da
        solo quello che dici di scrivere, con il cursore. e = {"da", "a", "testo": "...", "scrivi_da": secondo,
        "scrivi_a": secondo, "etichetta": "prompt"}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        testo = e["testo"]
        scrivi_da = e.get("scrivi_da", da + 0.3)
        scrivi_a = e.get("scrivi_a", min(scrivi_da + 0.06 * len(testo), a - 0.6))
        y = min(faccia["mento"] + 150, 1280)
        dim = 58 if len(testo) <= 22 else 46 if len(testo) <= 44 else 38
        self.corpo.append(f'<div class="pr2" id="pr{n}" style="top:{y}px"><span class="pr2-lab">{html.escape(e.get("etichetta", "prompt"))}</span>'
                          f'<div class="pr2-tx" style="font-size:{dim}px"><span id="pr{n}t"></span><span class="pr2-car" id="pr{n}c"></span></div></div>')
        self.tl.append(f'tl.fromTo("#pr{n}",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.25,ease:"power2.out",immediateRender:false}},{da:.3f});'
                       f'scrivi("#pr{n}t",{json.dumps(testo)},{scrivi_da:.3f},{scrivi_a:.3f});'
                       f'tl.fromTo("#pr{n}c",{{opacity:1}},{{opacity:0,duration:0.25,repeat:{max(int((a - da) / 0.25), 1)},yoyo:true,immediateRender:false}},{da:.3f});'
                       f'tl.to("#pr{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')
        self.suono("tastiera", scrivi_da, 0.3, dur=scrivi_a - scrivi_da)
        self.nascondi.append((da, a))

    def telefono3d(self, e, faccia):
        """Telefono 3D: un telefono vero, inclinato, vola accanto a te e mostra una chat: l'intestazione dell'app, i
        messaggi che arrivano e una scheda con un bottone giallo che viene toccato sulla parola giusta.
        e = {"da", "a", "app": "ChatGPT", "messaggi": [["testo", secondo, "io"|"app"], ...],
        "scheda": {"etichetta": "RISPOSTA", "titolo": "15 domande pronte", "bottone": "Copia", "da": secondo},
        "tocco": secondo (facoltativo), "fatto": "Copiato" (facoltativo)}."""
        da, a = e["da"], e["a"]
        self.font_extra("InterTight.ttf")
        n = len(self.corpo)
        destra = 1080 - faccia["destra"] >= faccia["sinistra"]
        # grande quanto il posto accanto alla testa (tra 0.7 e 1 volte il telefono intero da 400 px)
        posto = (1080 - faccia["destra"]) if destra else faccia["sinistra"]
        scala = max(0.7, min(1.0, (posto - 10) / 400))
        larg = 400 * scala
        x = (1080 - larg - 16) if destra else 16
        y = max(faccia["occhi"] - 420 * scala, 120)
        msg = "".join(f'<div class="tf-m {"io" if (m[2] if len(m) > 2 else "io") == "io" else "app"}" id="tf{n}m{j}">{html.escape(m[0])}</div>'
                      for j, m in enumerate(e.get("messaggi", [])[:3]))
        sc = e.get("scheda")
        scheda = ""
        if sc:
            scheda = (f'<div class="tf-sch" id="tf{n}k"><div class="tf-sl">✦ {html.escape(sc.get("etichetta", "RISPOSTA").upper())}</div>'
                      f'<div class="tf-st">{html.escape(sc["titolo"])}</div>'
                      f'<div class="tf-bot" id="tf{n}b"><span id="tf{n}bt">{html.escape(sc.get("bottone", "Approva"))}</span></div>'
                      f'<i class="tf-onda" id="tf{n}o"></i></div>')
        self.corpo.append(
            f'<div class="tf-scena" style="left:{x:.0f}px;top:{y:.0f}px;transform:scale({scala:.2f});transform-origin:0 0"><div class="tf" id="tf{n}" style="transform-origin:{"0" if destra else "100%"} 50%">'
            f'<div class="tf-isola"></div><div class="tf-stato"><b>9:41</b><span>▮▮▮ ◠ ▭</span></div>'
            f'<div class="tf-testa"><span class="tf-av">✦</span><div><b>{html.escape(e.get("app", "Assistente"))}</b><small><i></i>Online</small></div></div>'
            f'<div class="tf-chat">{msg}{scheda}</div><div class="tf-scrivi">Messaggio<span>↑</span></div><i class="tf-riflesso"></i></div></div>')
        giro = -14 if destra else 14
        T = self.tl.append
        T(f'tl.fromTo("#tf{n}",{{opacity:0,x:{300 if destra else -300},rotationY:{giro * 3},rotationX:6,scale:0.85}},'
          f'{{opacity:1,x:0,rotationY:{giro},rotationX:4,scale:1,duration:0.6,ease:"power3.out",immediateRender:false}},{da:.3f});'
          f'tl.to("#tf{n}",{{y:-14,duration:{max((a - da - 1) / 2, 0.3):.2f},ease:"sine.inOut",yoyo:true,repeat:1}},{da + 0.6:.3f});'
          f'tl.to("#tf{n}",{{opacity:0,x:{260 if destra else -260},rotationY:{giro * 3},duration:0.4,ease:"power3.in"}},{a - 0.4:.3f});')
        for j, m in enumerate(e.get("messaggi", [])[:3]):
            T(f'tl.fromTo("#tf{n}m{j}",{{opacity:0,y:14,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.25,ease:"power2.out",immediateRender:false}},{m[1]:.3f});')
            self.suono("pop", m[1], 0.25)
        if sc:
            T(f'tl.fromTo("#tf{n}k",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,ease:"power3.out",immediateRender:false}},{sc["da"]:.3f});')
            self.suono("ding", sc["da"], 0.25)
            if e.get("tocco"):
                t = e["tocco"]
                T(f'tl.fromTo("#tf{n}o",{{opacity:0.8,scale:0.2}},{{opacity:0,scale:2.4,duration:0.6,ease:"power2.out",immediateRender:false}},{t:.3f});'
                  f'tl.fromTo("#tf{n}b",{{scale:1}},{{keyframes:[{{scale:0.92,duration:0.08}},{{scale:1,duration:0.12}}],immediateRender:false}},{t:.3f});'
                  f'tl.set("#tf{n}b",{{backgroundColor:"#F4E06D",color:"#141414"}},{t + 0.08:.3f});'
                  f'tl.set("#tf{n}bt",{{textContent:"✓ {e.get("fatto", "Fatto")}"}},{t + 0.08:.3f});')
                self.suono("click", t, 0.45)
        self.suono("transizione", da, 0.3)

    def orbita(self, e, faccia):
        """Orbita: le copertine dei tuoi reel ti girano attorno su un'ellisse, passano dietro di te (ritaglio) e davanti,
        più piccole e scure quando sono dietro. e = {"da", "a", "immagini": ["file.jpg", ...] (facoltativo: senza,
        prende un fotogramma dai tuoi reel già montati), "giri": 1}."""
        da, a = e["da"], e["a"]
        sel = self.ritaglio(da, a)
        cart = os.path.dirname(self.reel)
        copertine = []
        for k, f in enumerate(e.get("immagini", [])[:7]):
            src = trova(f) if not os.path.isabs(f) else f
            if src and os.path.exists(src):
                dest = f"orbita-{k}.jpg"
                subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-vf", "scale=300:534:force_original_aspect_ratio=increase,crop=300:534",
                                "-frames:v", "1", os.path.join(self.assets, dest)], check=True)
                copertine.append(dest)
        if len(copertine) < 5:   # i reel già montati, uno per lavoro, un fotogramma a un terzo
            import glob
            lavori = sorted({os.path.dirname(os.path.dirname(v)) for v in glob.glob(os.path.join(os.path.dirname(cart), "*", "finale", "*.mp4"))
                             if os.path.dirname(os.path.dirname(v)) != cart})
            for k, lav in enumerate(lavori):
                if len(copertine) >= 7:
                    break
                v = sorted(glob.glob(os.path.join(lav, "finale", "*.mp4")))[-1]
                for quota in (0.3, 0.6):
                    if len(copertine) >= 7:
                        break
                    dest = f"orbita-r{k}-{int(quota * 10)}.jpg"
                    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{durata(v) * quota:.2f}", "-i", v, "-vf",
                                    "scale=300:534:force_original_aspect_ratio=increase,crop=300:534", "-frames:v", "1",
                                    os.path.join(self.assets, dest)], check=True)
                    copertine.append(dest)
        n = len(self.camera)
        self.camera.append(f'<div class="ob" id="ob{n}">' + "".join(f'<img class="ob-c" src="assets/{c}">' for c in copertine) + '</div>')
        cx = (faccia["sinistra"] + faccia["destra"]) / 2
        cy = faccia["mento"] + 120
        giri = e.get("giri", 1)
        self.tl.append(f'tl.set("{sel}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});'
                       f'tl.set("#ob{n}",{{opacity:1}},{da:.3f});tl.set("#ob{n}",{{opacity:0}},{a:.3f});'
                       f'orbita("#ob{n}",{cx:.0f},{cy:.0f},{da:.3f},{a:.3f},{giri});')
        self.suono("transizione", da, 0.3)

    def sfumatura(self, t, dur=1.3):
        """Transizione "sfumatura di luce": una luce calda arancio cresce sull'immagine, diventa bianca piena sul
        cambio (t) e poi si ritira lasciando un velo caldo che svanisce. Sotto il bianco l'immagine si sfoca appena."""
        n = len(self.corpo)
        self.corpo.append(f'<div class="sfu" id="sf{n}"><i class="sfu-calda" id="sf{n}c"></i><i class="sfu-bianca" id="sf{n}b"></i></div>')
        su, giu = dur * 0.4, dur * 0.6
        self.tl.append(f'tl.set("#sf{n}",{{opacity:1}},{t - su:.3f});'
                       f'tl.fromTo("#sf{n}c",{{opacity:0,scale:0.6}},{{opacity:1,scale:1.15,duration:{su:.3f},ease:"power1.in",immediateRender:false}},{t - su:.3f});'
                       f'tl.fromTo("#sf{n}b",{{opacity:0}},{{opacity:1,duration:{su * 0.45:.3f},ease:"power2.in",immediateRender:false}},{t - su * 0.45:.3f});'
                       f'tl.to("#sf{n}b",{{opacity:0,duration:{giu * 0.5:.3f},ease:"power2.out"}},{t + 0.04:.3f});'
                       f'tl.to("#sf{n}c",{{opacity:0,scale:1.3,duration:{giu:.3f},ease:"power1.out"}},{t + 0.04:.3f});'
                       f'tl.fromTo("#bg",{{filter:"blur(0px) brightness(1) saturate(1)"}},{{filter:"blur(6px) brightness(1.55) saturate(1.25)",duration:{su:.3f},ease:"power1.in",immediateRender:false}},{t - su:.3f});'
                       f'tl.fromTo("#bg",{{filter:"blur(3px) brightness(1.3) saturate(1.2)"}},{{filter:"blur(0px) brightness(1) saturate(1)",duration:{giu * 0.8:.3f},immediateRender:false}},{t + 0.04:.3f});'
                       f'tl.set("#sf{n}",{{opacity:0}},{t + giu + 0.05:.3f});')
        self.suono("transizione", t - su * 0.6, 0.3)

    def transizione(self, t):
        """La transizione dello stile (o scelta nella pagina) su un cambio di argomento."""
        tipo = self.stile.get("transizione_scelta") or self.stile.get("transizione", "bande")
        if tipo == "sfumatura":
            self.sfumatura(t)
        elif tipo == "bande":
            self.bande(t)

    def titolo_box(self, testo, da, a, y):
        """Titolo d'apertura semplice: un riquadro bianco con il testo nero, due righe al massimo."""
        n = len(self.corpo)
        self.corpo.append(f'<div class="tbox" id="tb{n}" style="top:{y}px"><span>{html.escape(testo)}</span></div>')
        self.tl.append(f'tl.fromTo("#tb{n}",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.25,ease:"power2.out",immediateRender:false}},{da:.3f});'
                       f'tl.to("#tb{n}",{{opacity:0,duration:0.2}},{a - 0.2:.3f});')

    # ---------- scene a tutto schermo (stile dal reel di esempio 04) ----------
    def scena(self, e, faccia):
        """Scena a tutto schermo: fondo scuro o carta, in alto un'etichetta piccola e un titolo che arriva riga per riga
        (una riga può stare su una targa d'accento), al centro un pezzo animato (e["modulo"]). La persona non si vede.
        e = {"da", "a", "fondo": "scuro"|"carta", "etichetta": "NEL PRIMO MESE",
             "titolo": [{"testo": "PER MONTARE", "da": s}, {"testo": "UN REEL", "da": s, "targa": true}],
             "modulo": {...} (riempi, esplodi, righe, play, pellicola: vedi i metodi m_*)}."""
        da, a = e["da"], e["a"]
        n = len(self.corpo)
        carta = e.get("fondo", "scuro") == "carta"
        righe_t = []
        for j, r in enumerate(e.get("titolo", [])):
            righe_t.append(f'<div class="sc-r{" targa-sc" if r.get("targa") else ""}" id="sc{n}t{j}">{html.escape(r["testo"])}</div>')
            self.tl.append(f'tl.fromTo("#sc{n}t{j}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.18,ease:"power2.out",immediateRender:false}},{r.get("da", da):.3f});')
        lab = f'<div class="sc-lab">{html.escape(e["etichetta"].upper())}</div>' if e.get("etichetta") else ""
        mod = e.get("modulo", {})
        dentro = getattr(self, "m_" + mod["tipo"])(mod, n, da, a, carta) if mod else ""
        self.corpo.append(f'<div class="scn{" carta" if carta else ""}" id="sc{n}">{lab}<div class="sc-tit">{"".join(righe_t)}</div>{dentro}</div>')
        self.tl.append(f'tl.set("#sc{n}",{{opacity:1}},{da:.3f});tl.set("#sc{n}",{{opacity:0}},{a:.3f});')
        self.suono("transizione", da - 0.05, 0.25)
        self.nascondi.append((da, a))

    def _barretta(self, id_, x, y, w=40, h=120, rot=0, spenta=False):
        """Una barretta arancio. Spenta = grigia, con dentro quella accesa nascosta: si accende con tl.set(id + " b", opacity 1)."""
        dentro = '<b class="bar-on"></b>' if spenta else ""
        return (f'<i class="bar{" spenta" if spenta else ""}" id="{id_}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w}px;height:{h}px;'
                f'transform:rotate({rot:.0f}deg)">{dentro}</i>')

    def m_riempi(self, m, n, da, a, carta):
        """Barrette che riempiono un telefono vuoto (cadono e si ammucchiano) o una griglia (cella dopo cella), con il
        contatore sotto; alla fine può sbattere un timbro. m = {"tipo": "riempi", "contenitore": "telefono"|"griglia",
        "unita": "MINUTI", "passi": [[15, s], [39, s]], "timbro": ["1 ORA", s], "segno": "+"}."""
        passi, unita = m["passi"], m.get("unita", "")
        totale = passi[-1][0]
        pezzi, T = [], self.tl.append
        if m.get("contenitore", "griglia") == "telefono":
            pezzi.append('<div class="sc-tel"></div>')
            k_max = min(totale, 36)
            prima, t0 = 0, da + 0.3
            for valore, quando in passi:
                quanti = round(k_max * valore / totale)
                for k in range(prima, quanti):   # cadono nell'intervallo prima del numero detto
                    riga, col = divmod(k, 3)
                    x = 420 + col * 120 + (riga % 2) * 30
                    y = 1300 - riga * 34
                    rot = 86 + ((k * 37) % 17) - 8
                    pezzi.append(self._barretta(f"sc{n}b{k}", x, y - 40, 34, 110, rot))
                    t = t0 + (quando - t0) * (k - prima + 1) / max(quanti - prima, 1)
                    T(f'tl.fromTo("#sc{n}b{k}",{{y:-760,opacity:1,rotate:{rot - 40}}},{{y:0,rotate:{rot},duration:0.35,ease:"bounce.out",immediateRender:false}},{t - 0.35:.3f});')
                prima, t0 = quanti, quando
            y_conta = 1450
        else:
            cols, rows = 10, 6
            celle = cols * rows
            for k in range(celle):
                riga, col = divmod(k, cols)
                pezzi.append(self._barretta(f"sc{n}b{k}", 150 + col * 80, 560 + riga * 150, 42, 120, 0, True))
            prima, t0 = 0, da + 0.2
            for valore, quando in passi:
                quante = round(celle * valore / totale) if not m.get("celle_per_unita") else valore
                for k in range(prima, min(quante, celle)):
                    t = t0 + (quando - t0) * (k - prima + 1) / max(quante - prima, 1)
                    T(f'tl.set("#sc{n}b{k} b",{{opacity:1}},{t:.3f});')
                prima, t0 = quante, quando
            y_conta = 1540
        segno = m.get("segno", "")
        pezzi.append(f'<div class="sc-conta" style="top:{y_conta}px"><b id="sc{n}c">{segno}0</b><span>{html.escape(unita.upper())}</span></div>')
        prec = 0
        for valore, quando in passi:
            T(f'contaCon("#sc{n}c",{json.dumps(segno)},{prec},{valore},{max(quando - 0.6, da):.3f},0.6);')
            prec = valore
        self.suono("livello", passi[-1][1], 0.3)
        if m.get("timbro"):
            testo, quando = m["timbro"]
            pezzi.append(f'<div class="sc-timbro" id="sc{n}x">{html.escape(testo)}</div>')
            T(f'tl.fromTo("#sc{n}x",{{opacity:0,scale:2.4,rotate:-4}},{{opacity:1,scale:1,rotate:-12,duration:0.22,ease:"power4.in",immediateRender:false}},{quando - 0.2:.3f});')
            self.suono("impatto", quando, 0.45)
        return "".join(pezzi)

    def m_esplodi(self, m, n, da, a, carta):
        """Tante barrette in griglia: sul secondo detto volano via tutte tranne poche, che si mettono in fila al centro;
        poi arriva un numero grande con l'unità. m = {"tipo": "esplodi", "quando": s, "resta": 5, "numero": "5",
        "unita": "MINUTI", "numero_da": s}."""
        resta, q = m.get("resta", 5), m["quando"]
        pezzi, T = [], self.tl.append
        cols, rows = 10, 6
        for k in range(cols * rows):
            riga, col = divmod(k, cols)
            x, y = 150 + col * 80, 560 + riga * 150
            pezzi.append(self._barretta(f"sc{n}b{k}", x, y))
            if k < resta:   # quelle che restano vanno in fila al centro
                fx = 540 - (resta * 90) / 2 + k * 90 + 25 - x
                T(f'tl.to("#sc{n}b{k}",{{x:{fx:.0f},y:{760 - y:.0f},duration:0.45,ease:"power3.inOut"}},{q + 0.15:.3f});')
            else:
                ang = (k * 2.399) % (2 * math.pi)
                d = 700 + (k * 53) % 500
                T(f'tl.to("#sc{n}b{k}",{{x:{math.cos(ang) * d:.0f},y:{math.sin(ang) * d + 300:.0f},rotate:{(k * 77) % 540 - 270},opacity:0,'
                  f'duration:0.7,ease:"power2.out"}},{q:.3f});')
        pezzi.append(f'<div class="sc-num" id="sc{n}n"><b>{html.escape(str(m.get("numero", resta)))}</b><span>{html.escape(m.get("unita", "").upper())}</span></div>')
        T(f'tl.fromTo("#sc{n}n",{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)",immediateRender:false}},{m.get("numero_da", q + 0.7):.3f});')
        self.suono("impatto", q, 0.4)
        return "".join(pezzi)

    def m_righe(self, m, n, da, a, carta):
        """Scritta che si costruisce riga per riga, grande, a sinistra; una riga può essere barrata e sotto sbatte un timbro
        con un'etichetta piccola sopra. m = {"tipo": "righe", "righe": [["NON", s], ["L'ABBIAMO", s], ...],
        "barra": [indice_riga, s], "timbro": ["L'AI.", s], "sopra_timbro": "L'HA MONTATO"}."""
        pezzi, T = [], self.tl.append
        for j, (testo, quando) in enumerate(m["righe"]):
            pezzi.append(f'<div class="sc-riga" id="sc{n}r{j}" style="top:{560 + j * 150}px">{html.escape(testo)}<i class="sc-barra" id="sc{n}r{j}b"></i></div>')
            T(f'tl.fromTo("#sc{n}r{j}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.2,ease:"power3.out",immediateRender:false}},{quando:.3f});')
            self.suono("pop", quando, 0.25)
        if m.get("barra"):
            j, quando = m["barra"]
            T(f'tl.fromTo("#sc{n}r{j}b",{{scaleX:0}},{{scaleX:1,duration:0.25,ease:"power2.out",immediateRender:false}},{quando:.3f});'
              f'tl.to("#sc{n}r{j}",{{opacity:0.45,duration:0.2}},{quando + 0.2:.3f});')
        if m.get("timbro"):
            testo, quando = m["timbro"]
            y = 560 + len(m["righe"]) * 150 + 40
            sopra = f'<div class="sc-lab sx" style="top:{y - 50}px">{html.escape(m.get("sopra_timbro", "").upper())}</div>' if m.get("sopra_timbro") else ""
            pezzi.append(f'{sopra}<div class="sc-timbro sx" id="sc{n}x" style="top:{y}px">{html.escape(testo)}</div>')
            T(f'tl.fromTo("#sc{n}x",{{opacity:0,scale:2.4,rotate:-2}},{{opacity:1,scale:1,rotate:-6,duration:0.22,ease:"power4.in",immediateRender:false}},{quando - 0.2:.3f});')
            self.suono("impatto", quando, 0.45)
        return "".join(pezzi)

    def m_play(self, m, n, da, a, carta):
        """Un telefono bianco con il tasto play arancio e un'etichetta in alto; sotto si accendono delle barrette; sul
        secondo "pronto" lo schermo diventa scuro con la spunta e la scritta. m = {"tipo": "play", "etichetta": "IL TUO VIDEO",
        "barre": [s, s, s, s, s], "pronto": s, "scritta": "PRONTO"}."""
        pezzi, T = [], self.tl.append
        pezzi.append(f'<div class="sc-play" id="sc{n}p"><span class="sc-pl">{html.escape(m.get("etichetta", "IL TUO VIDEO").upper())}</span>'
                     f'<i class="sc-tasto"></i><div class="sc-pronto" id="sc{n}k"><b>✓</b>{html.escape(m.get("scritta", "PRONTO").upper())}</div></div>')
        barre = m.get("barre", [])
        for k, quando in enumerate(barre):
            pezzi.append(self._barretta(f"sc{n}b{k}", 540 - len(barre) * 30 + k * 60, 1480, 34, 90, 0, True))
            T(f'tl.set("#sc{n}b{k} b",{{opacity:1}},{quando:.3f});')
            self.suono("pop", quando, 0.2)
        if m.get("pronto"):
            T(f'tl.fromTo("#sc{n}k",{{opacity:0}},{{opacity:1,duration:0.25,immediateRender:false}},{m["pronto"]:.3f});'
              f'tl.fromTo("#sc{n}k b",{{scale:0}},{{scale:1,duration:0.3,ease:"back.out(3)",immediateRender:false}},{m["pronto"] + 0.1:.3f});')
            self.suono("ding", m["pronto"], 0.35)
        return "".join(pezzi)

    def m_pellicola(self, m, n, da, a, carta):
        """Una pellicola con i fotogrammi di questo stesso video scorre verso sinistra; una linea arancio ferma al
        centro è "adesso". m = {"tipo": "pellicola", "adesso": s (quando compare la scritta), "scritta": "ADESSO"}."""
        D = durata(os.path.join(self.assets, "tagliato.mp4"))
        foto = []
        for k in range(10):   # fotogrammi del video, dal primo fino a questo momento
            t = min(da, D - 0.1) * k / 9
            nome = f"pell-{n}-{k}.jpg"
            subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", os.path.join(self.assets, "tagliato.mp4"), "-frames:v", "1",
                            "-vf", "scale=170:302:force_original_aspect_ratio=increase,crop=170:302", "-q:v", "4", os.path.join(self.assets, nome)], check=True)
            foto.append(f'<img src="assets/{nome}">')
        larg = 10 * 200
        self.tl.append(f'tl.fromTo("#sc{n}f",{{x:{200}}},{{x:{540 - larg + 100},duration:{max(a - da, 0.5):.2f},ease:"none",immediateRender:false}},{da:.3f});')
        pez = (f'<div class="sc-pell"><div class="sc-film" id="sc{n}f">{"".join(foto)}</div></div><i class="sc-adesso-l"></i>'
               f'<span class="sc-adesso" id="sc{n}d">{html.escape(m.get("scritta", "ADESSO").upper())}</span>')
        if m.get("adesso"):
            self.tl.append(f'tl.fromTo("#sc{n}d",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(2)",immediateRender:false}},{m["adesso"]:.3f});')
        return pez

    def finale_clicca(self, piano, da):
        """Finale del Reel 04: fondo scuro, il marchio in alto, il titolo con una parola barrata e quella giusta in
        arancio, le barrette, "CLICCA QUI SOTTO" e una freccia tonda che salta. piano["finale_clicca"] = {
        "marchio": "Networker del Futuro", "righe": [["DA", "1 ORA", "barrata"], ["A", "5 MINUTI."]], "barre": 5,
        "scritta": "CLICCA QUI SOTTO"}."""
        f = piano["finale_clicca"]
        n = len(self.corpo)
        righe = []
        lunga = max((len(" ".join(r[:2])) for r in f.get("righe", [])), default=8)
        dim = min(96, int(900 / (lunga * 0.82)))   # ogni riga sta su una riga sola
        for j, r in enumerate(f.get("righe", [])):
            parte2 = f'<span class="{"fc-barrata" if len(r) > 2 and r[2] == "barrata" else "fc-acc"}">{html.escape(r[1])}</span>' if len(r) > 1 else ""
            righe.append(f'<div class="fc-r" style="font-size:{dim}px">{html.escape(r[0])} {parte2}</div>')
        barre = "".join('<i class="bar" style="position:relative;width:30px;height:76px"></i>' for _ in range(f.get("barre", 5)))
        self.corpo.append(f'<div class="scn" id="fc{n}"><div class="fc-marchio"><i>NDF</i>{html.escape(f.get("marchio", ""))}</div>'
                          f'<div class="fc-tit">{"".join(righe)}<div class="fc-barre">{barre}</div></div>'
                          f'<div class="fc-sc">{html.escape(f.get("scritta", "CLICCA QUI SOTTO").upper())}</div><div class="fc-freccia" id="fc{n}a">↓</div></div>')
        self.tl.append(f'tl.set("#fc{n}",{{opacity:1}},{da:.3f});'
                       f'tl.fromTo("#fc{n} .fc-barrata",{{"--b":0}},{{"--b":1,duration:0.3,immediateRender:false}},{da + 0.6:.3f});'
                       f'tl.fromTo("#fc{n}a",{{y:0}},{{y:18,duration:0.4,repeat:{int((self.D - da) / 0.4)},yoyo:true,ease:"sine.inOut",immediateRender:false}},{da + 0.4:.3f});')
        self.nascondi.append((da, self.D + 1))
        self.suono("transizione", da - 0.05, 0.25)

    def finale(self, piano, da):
        self.bande(da)
        self.scuro(da, self.D)
        f = self.stile.get("finale", {})
        testo = piano.get("finale_testo", f.get("testo", "COMMENTA"))
        bottone = piano.get("finale_bottone", f.get("bottone", "INFO"))
        sopra = piano.get("finale_sopra", f.get("sopra", ""))
        self.corpo.append(f'<div class="finale" id="fin"><div class="mono-sotto" style="position:static;opacity:1" id="fm"></div>'
                          f'<div class="fin-g">{html.escape(testo)}</div><div class="bottone" id="bot">{html.escape(bottone)}</div>'
                          f'<div class="freccia" id="fr">↓</div></div>')
        self.tl.append(f'tl.fromTo("#fin",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{da + 0.1:.3f});'
                       f'tl.fromTo("#bot",{{scale:0.6}},{{scale:1,duration:0.35,ease:"back.out(2)"}},{da + 0.35:.3f});'
                       f'tl.fromTo("#fr",{{y:0}},{{y:22,duration:0.4,repeat:{int((self.D - da) / 0.4)},yoyo:true,ease:"sine.inOut"}},{da + 0.5:.3f});')
        if sopra:
            self.decodifica("#fm", sopra, da + 0.3)
        self.suono("impatto", da + 0.35, 0.4)

    def sottotitoli(self, parole, chiave, y):
        """1-3 parole alla volta; la parola chiave su targhetta d'accento. Spariscono prima di ogni grafica."""
        gruppi, g = [], []
        for w in parole:
            g.append(w)
            if re.search(r"[.,?!]$", w["testo"]) or len(g) == 3 or sum(len(x["testo"]) for x in g) > 13:
                gruppi.append(g)
                g = []
        if g:
            gruppi.append(g)
        for i, g in enumerate(gruppi):
            da = g[0]["da"]
            if any(x <= da < z for x, z in self.nascondi):
                continue
            fine = gruppi[i + 1][0]["da"] if i + 1 < len(gruppi) else g[-1]["a"]
            fine = min([fine, g[-1]["a"] + 0.5] + [x for x, _ in self.nascondi if x > da])
            pezzi = []
            for w in g:
                t = re.sub(r"[.,;:!?\"«»]", "", w["testo"]).upper()
                pezzi.append(f'<span class="{"k" if t.lower() in chiave else ""}">{html.escape(t)}</span>')
            self.corpo.append(f'<div class="sub" id="u{i}" style="top:{y}px">{" ".join(pezzi)}</div>')
            self.tl.append(f'tl.set("#u{i}",{{opacity:1}},{da:.3f});'
                           f'tl.fromTo("#u{i}",{{scale:0.8,y:14}},{{scale:1,y:0,duration:0.14,ease:"back.out(2)"}},{da:.3f});'
                           f'tl.set("#u{i}",{{opacity:0}},{fine:.3f});')


def costruisci(cart, piano, stile, cart_stile, parole, faccia, D, zone_html=""):
    reel = os.path.join(cart, "reel")
    r = Reel(stile, cart_stile, reel, D)
    os.makedirs(r.assets, exist_ok=True)
    dest = os.path.join(r.assets, "tagliato.mp4")
    if os.path.exists(dest):
        os.remove(dest)
    try:
        os.link(girato(cart), dest)
    except OSError:
        shutil.copy2(girato(cart), dest)
    ft, fm = stile["font"]["titoli"], stile["font"]["mono"]
    for f in (ft, fm):
        shutil.copy2(os.path.join(cart_stile, f["file"]), os.path.join(r.assets, os.path.basename(f["file"])))

    petto = min(faccia["mento"] + 70, 1180)  # titoli e targhette sul petto, sotto il mento
    y_sub = min(faccia["mento"] + 160, 1300)
    ap = piano.get("apertura")
    # effetti accesi: quelli scelti nella pagina, se no quelli dello stile (stile.json "effetti"), se no tutti
    accesi = stile.get("effetti_scelti", stile.get("effetti"))
    commento = False
    if ap and ap.get("box"):
        r.titolo_box(ap["box"], 0.0, ap.get("a", 4.0), max(faccia["mento"] - 40, 900))
        r.suono("apertura", 0.0, 0.3)
        ap = None
    if ap and accesi is not None and "titolo" not in accesi:
        print('NOTA: "Titolo" non è tra gli effetti scelti, niente titolo d\'apertura')
        ap = None
    if ap:
        r.titolo(ap["sopra"], ap["targa"], 0.0, ap.get("a", 2.0), petto - 20)
        r.nascondi.append((0.0, ap.get("a", 2.0)))
        r.suono("apertura", 0.0, 0.4)
    for e in sorted(piano.get("elementi", []), key=lambda x: x["da"] if "da" in x else x["quando"] if "quando" in x else x["voci"][0][-1] if x.get("voci") else 0):
        tipo = e["tipo"]
        if tipo != "scena" and accesi is not None and effetti.chiave_di(e) not in accesi:   # le scene sono lo stile, non un effetto
            print(f'NOTA: "{effetti.CATALOGO[effetti.chiave_di(e)]["nome"]}" non è tra gli effetti accesi, lo salto')
            continue
        if tipo == "gigante":
            r.gigante(e)
            r.bande(e["a"])
        elif tipo == "titolo":
            r.titolo(e["sopra"], e["targa"], e["da"], e["a"], petto - 20)
            if e.get("sotto"):
                r.sotto_mono(e["sotto"], e.get("sotto_da", e["da"] + 1), e["a"], petto + 230)
            r.nascondi.append((e["da"], e["a"]))
        elif tipo == "targhette":
            r.targhette(e["voci"], e["a"], petto)
        elif tipo == "contatore":
            r.contatore(e, faccia["mento"] + 40)
        elif tipo in ("cornice", "telefono"):
            r.cornice(e, telefono=tipo == "telefono")
        elif tipo == "dietro":
            r.dietro(e, faccia)
        elif tipo == "adesivo":
            r.adesivo(e, faccia)
        elif tipo == "zoom":
            r.zoom(e, faccia)
        elif tipo == "schermo":
            r.schermo(e, faccia)
        elif tipo == "luce":
            r.luce(e, faccia)
        elif tipo == "commento":
            r.commento(e, faccia)
            commento = True
        elif tipo == "numero":
            r.numero(e, faccia)
        elif tipo == "etichette":
            r.etichette(e, faccia)
        elif tipo == "neon":
            r.neon(e, faccia)
        elif tipo == "percorso":
            r.percorso(e)
        elif tipo == "checklist":
            r.checklist(e, faccia)
        elif tipo == "contachilometri":
            r.contachilometri(e, faccia)
        elif tipo == "pillole":
            r.pillole(e, faccia)
        elif tipo == "prompt":
            r.prompt(e, faccia)
        elif tipo == "telefono3d":
            r.telefono3d(e, faccia)
        elif tipo == "orbita":
            r.orbita(e, faccia)
        elif tipo == "scena":
            r.scena(e, faccia)
    for t in piano.get("transizioni", []):   # cambi di argomento scelti da Claude
        r.transizione(t)
    # il commento fa da chiusura: senza "finale_da" nel piano, niente finale scuro sopra
    finale_da = piano.get("finale_da", D + 1 if commento or stile.get("finale") is False else D - 2.3)
    if piano.get("finale_clicca"):
        r.finale_clicca(piano, piano.get("finale_da", D - 3.0))
    elif finale_da < D:
        r.finale(piano, finale_da)
    if piano.get("musica", True):
        r.musica()
    chiave = {p.lower() for p in piano.get("parole_chiave", [])}
    css_sott = ""
    propri = stile.get("sottotitoli_nome") if stile.get("sottotitoli_nome") not in (None, "ndf-targhetta") else None
    if stile.get("sottotitoli_scelti") or propri:  # scelti nella pagina, o quelli dello stile (strumenti/sottotitoli.py)
        css_sott, c_sott, tl_sott, f_sott = sottotitoli.parti(stile.get("sottotitoli_scelti") or propri, parole, chiave, y_sub,
                                                            r.nascondi + [(finale_da, D + 1)], stile["colori"])
        r.corpo += c_sott
        r.tl += tl_sott
        for f in f_sott:
            shutil.copy2(os.path.join(STUDIO, "font", f), os.path.join(r.assets, f))
    else:
        r.sottotitoli(parole, chiave, y_sub)

    c = stile["colori"]
    acc, luce, scuro, testo, banda = c["accento"], c["accento_luce"], c["scuro"], c["testo"], c["banda"]
    rgb = ",".join(str(int(luce[i:i + 2], 16)) for i in (1, 3, 5))  # il colore chiaro, per bordi e aloni trasparenti
    W = f"font-family:'{ft['famiglia']}';font-weight:{ft.get('peso', 900)};font-stretch:{ft.get('larghezza', 100)}%"
    M = f"font-family:'{fm['famiglia']}';font-weight:700"
    pagina = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
@font-face{{font-family:'{ft["famiglia"]}';src:url('assets/{os.path.basename(ft["file"])}');font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:'{fm["famiglia"]}';src:url('assets/{os.path.basename(fm["file"])}');font-weight:100 800}}
html,body{{margin:0;background:{scuro}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:{scuro}}}
#cam{{position:absolute;inset:0;overflow:hidden;z-index:5;transform-origin:540px 960px}}
#cam.cor{{box-shadow:0 0 0 5px {luce},0 0 60px 10px rgba({rgb},.45)}}
#cam.tel{{box-shadow:0 0 0 14px #111,0 0 0 18px {luce},0 0 70px 14px rgba({rgb},.4)}}
#bg{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
.scuro{{position:absolute;inset:0;z-index:6;background:radial-gradient(ellipse at 50% 35%,{banda} 0%,{scuro} 65%);opacity:0;overflow:hidden}}
.griglia{{position:absolute;left:-600px;right:-600px;top:1150px;height:1500px;transform:perspective(700px) rotateX(62deg);
 transform-origin:50% 0;background-image:linear-gradient(rgba({rgb},.22) 2px,transparent 2px),
 linear-gradient(90deg,rgba({rgb},.22) 2px,transparent 2px);background-size:120px 120px}}
.alone{{position:absolute;left:0;right:0;top:1120px;height:90px;background:radial-gradient(ellipse at 50% 50%,rgba({rgb},.35),transparent 70%)}}
.mirino{{position:absolute;inset:0;z-index:20;pointer-events:none}}
.mirino i{{position:absolute;width:70px;height:70px;border-color:rgba(255,255,255,.85);border-style:solid;border-width:0}}
.mirino .a{{left:60px;top:240px;border-left-width:5px;border-top-width:5px}}
.mirino .b{{right:60px;top:240px;border-right-width:5px;border-top-width:5px}}
.mirino .c{{left:60px;top:1380px;border-left-width:5px;border-bottom-width:5px}}
.mirino .d{{right:110px;top:1380px;border-right-width:5px;border-bottom-width:5px}}
.mir-lab{{position:absolute;top:260px;{M};font-size:26px;color:#fff;letter-spacing:1px;text-shadow:0 2px 8px rgba(0,0,0,.6)}}
.mir-lab .rosso{{color:#FF3B30}}
.banda{{position:absolute;left:-60px;width:1200px;z-index:40}}
.bande{{position:absolute;inset:0;z-index:40;pointer-events:none}}
.sub{{position:absolute;left:80px;right:110px;text-align:center;opacity:0;z-index:30;{W};text-transform:uppercase;
 font-size:62px;line-height:1.15;color:{testo};text-shadow:0 4px 16px rgba(0,0,0,.7)}}
.sub .k{{background:{acc};color:#fff;padding:2px 14px;border-radius:10px;text-shadow:none;box-decoration-break:clone}}
.titolo{{position:absolute;left:80px;right:110px;text-align:center;opacity:0;z-index:30}}
.riga-b{{{W};font-size:84px;line-height:1;color:#fff;text-shadow:0 4px 16px rgba(0,0,0,.6)}}
.targa{{display:inline-block;margin-top:10px;background:{acc};color:#fff;{W};font-size:84px;line-height:1;padding:8px 26px 12px;
 border-radius:12px;transform-origin:0 50%;box-shadow:0 8px 30px rgba({rgb},.4)}}
.gigante{{position:absolute;left:0;right:0;top:820px;height:400px;opacity:0;z-index:35}}
.targa-g{{position:absolute;left:50%;top:50%;margin-left:-480px;margin-top:-100px;width:960px;text-align:center;{W};
 line-height:200px;color:{acc};border:8px solid {acc};border-radius:26px;background:rgba({rgb},.1);
 box-shadow:0 0 50px rgba({rgb},.55),inset 0 0 40px rgba({rgb},.25);text-shadow:0 0 30px rgba({rgb},.6);white-space:nowrap}}
.sc{{position:absolute;left:540px;top:200px;width:14px;height:14px;border-radius:3px;background:{luce}}}
.sc:nth-child(odd){{background:{acc}}}
.mono-sotto{{position:absolute;left:0;right:0;top:400px;text-align:center;{M};font-size:36px;letter-spacing:3px;color:{luce}}}
.mono-sotto.fisso{{left:80px;right:110px;z-index:31;opacity:0;text-shadow:0 2px 10px rgba(0,0,0,.8)}}
.chip{{position:absolute;left:70px;height:84px;display:flex;align-items:center;gap:18px;padding:0 30px 0 16px;border-radius:16px;
 background:{scuro}ee;border:3px solid rgba({rgb},.55);z-index:31;opacity:0;{W};font-size:42px;color:#fff;box-shadow:0 10px 30px rgba(0,0,0,.4)}}
.chip .ico{{width:52px;height:52px;border-radius:12px;border:3px solid {luce};color:{luce};display:flex;align-items:center;
 justify-content:center;font-size:30px;{M}}}
.prompt{{position:absolute;left:110px;right:140px;top:1290px;min-height:150px;padding:22px 90px 22px 28px;border-radius:24px;
 background:#fff;color:#111;font-family:'{ft["famiglia"]}';font-weight:600;font-size:36px;line-height:1.25;z-index:32;opacity:0;
 box-shadow:0 0 0 4px {luce},0 18px 50px rgba(0,0,0,.5)}}
.pr-lab{{{M};font-size:22px;color:{acc};margin-bottom:8px;letter-spacing:2px}}
.invia{{position:absolute;right:20px;bottom:20px;width:58px;height:58px;border-radius:50%;background:{acc};color:#fff;
 font-size:34px;display:flex;align-items:center;justify-content:center;font-weight:900}}
.prezzo{{position:absolute;left:190px;right:220px;height:150px;border-radius:20px;background:{scuro}f0;
 border:3px solid rgba({rgb},.55);z-index:32;opacity:0;display:flex;align-items:center;justify-content:center;gap:24px;transform-origin:0 50%}}
.pz-lab,.pz-sotto{{{M};font-size:26px;color:{luce};letter-spacing:2px;width:200px}}
.pz-lab{{text-align:right}}
.pz-num{{{W};font-size:120px;color:{acc};line-height:1;min-width:150px;text-align:center}}
.barra{{position:absolute;left:110px;right:140px;top:1340px;height:110px;display:flex;gap:12px;padding:14px;border-radius:20px;
 background:{scuro}f2;border:3px solid rgba({rgb},.4);z-index:32;opacity:0}}
.passo{{flex:1;position:relative}}
.passo .riemp{{height:52px;border-radius:10px;background:{luce};transform-origin:0 50%;transform:scaleX(0);display:flex;align-items:center;justify-content:flex-end;padding-right:12px}}
.passo:nth-child(2) .riemp{{background:{acc}}}
.passo .riemp span{{display:inline-block;font-weight:900;font-size:30px;color:{scuro}}}
.passo .pl{{{M};font-size:20px;color:{testo};margin-top:8px;letter-spacing:1px}}
.rec-tel{{position:absolute;left:510px;top:1350px;width:60px;height:60px;border-radius:50%;border:5px solid #fff;z-index:32;opacity:0}}
.rec-tel b{{position:absolute;inset:7px;border-radius:50%;background:#FF3B30}}
.rec-lab{{position:absolute;left:330px;top:560px;{M};font-size:24px;color:#fff;background:rgba(0,0,0,.55);padding:6px 14px;border-radius:10px;z-index:32;opacity:0}}
.finale{{position:absolute;left:80px;right:110px;top:640px;text-align:center;z-index:36;opacity:0}}
.fin-g{{{W};font-size:120px;color:#fff;margin-top:30px}}
.bottone{{display:inline-block;margin-top:24px;background:{acc};color:#fff;{W};font-size:150px;padding:10px 60px 18px;border-radius:30px;
 box-shadow:0 0 60px rgba({rgb},.6)}}
.freccia{{margin:30px auto 0;width:110px;height:110px;border-radius:50%;background:{acc};color:#fff;font-size:70px;font-weight:900;
 display:flex;align-items:center;justify-content:center}}
.zona{{position:absolute;background:rgba(255,0,0,.35);z-index:50}}
.rit{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:3}}
.pdietro{{position:absolute;left:0;right:0;text-align:center;{W};line-height:1;white-space:nowrap;opacity:0;z-index:2;
 transform-origin:50% 60%}}
.buio{{position:absolute;inset:0;z-index:7;opacity:0;pointer-events:none;
 background:radial-gradient(900px 1100px at 540px 900px,rgba(2,4,10,0) 45%,rgba(2,4,10,.35) 78%,rgba(2,4,10,.6) 100%)}}
.lampo{{position:absolute;inset:0;z-index:60;opacity:0;pointer-events:none}}
.schermo{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:2}}
.pozza{{position:absolute;inset:0;z-index:2;opacity:0;mix-blend-mode:screen}}
.lbuio{{position:absolute;inset:0;z-index:7;opacity:0;pointer-events:none;
 background:radial-gradient(640px 860px at 540px 820px,rgba(0,0,0,0) 35%,rgba(0,0,8,.75) 100%)}}
.lparola{{position:absolute;left:40px;right:40px;text-align:center;z-index:31;font-family:'{ft["famiglia"]}';font-weight:900;
 letter-spacing:-4px;line-height:1;color:#fff;opacity:0;text-shadow:0 10px 40px rgba(0,0,0,.5)}}
@font-face{{font-family:'Caveat';src:url('assets/Caveat.ttf');font-weight:400 700}}
.pagina{{position:absolute;inset:0;z-index:36;opacity:0;overflow:hidden}}
.raggi{{position:absolute;left:-600px;top:-500px;width:2280px;height:2920px;
 background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,.10) 0deg 7deg,rgba(255,255,255,0) 7deg 18deg);
 -webkit-mask:radial-gradient(circle at 50% 50%,#000 20%,rgba(0,0,0,.35) 60%);mask:radial-gradient(circle at 50% 50%,#000 20%,rgba(0,0,0,.35) 60%)}}
.segni{{position:absolute;width:70px;height:120px}}
.segni i{{position:absolute;left:0;width:64px;height:9px;border-radius:5px;background:#fff;transform-origin:100% 50%}}
.timbro{{position:absolute;left:90px;top:200px;font-family:'Archivo';font-weight:900;font-stretch:110%;font-size:54px;letter-spacing:2px;
 padding:6px 20px;border:6px solid;border-radius:12px;opacity:0;background:rgba(255,255,255,.06)}}
.adesivo{{position:absolute;filter:drop-shadow(0 18px 30px rgba(0,0,0,.45))}}
.nota{{position:absolute;left:90px;right:120px;text-align:center;font-family:'Caveat';font-weight:700;font-size:118px;line-height:1;
 color:#fff;opacity:0;text-shadow:0 3px 0 rgba(0,0,0,.25)}}
@font-face{{font-family:'Indie Flower';src:url('assets/IndieFlower.ttf')}}
.neon{{position:absolute;font-family:'Indie Flower';line-height:1.02;white-space:nowrap;opacity:0;z-index:2;transform:rotate(-3deg)}}
.ne-spento{{color:rgba(240,236,224,.34);text-shadow:0 1px 2px rgba(0,0,0,.3)}}
.ne-acceso{{position:absolute;left:0;top:0;opacity:0}}
.ne-r2{{position:relative;display:inline-block;margin-left:0.55em}}
.ne-sott{{position:absolute;left:-0.1em;right:-0.25em;bottom:0.02em;height:0.055em;border-radius:1em;background:currentColor;
 box-shadow:inherit;transform:rotate(-2deg)}}
.ne-acceso .ne-sott{{background:#FFF6CF;box-shadow:0 0 6px #FFF6CF,0 0 18px #FFD84A,0 0 40px #FFD84A}}
.ne-alone{{position:absolute;width:840px;height:760px;opacity:0;z-index:1;mix-blend-mode:screen}}
@font-face{{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}}
@font-face{{font-family:'Instrument Serif';src:url('assets/InstrumentSerif-Italic.ttf');font-style:italic}}
.cm{{position:absolute;left:90px;right:90px;z-index:33;opacity:0;font-family:'Inter Tight'}}
.cm-campo{{position:relative;display:flex;align-items:center;gap:20px;height:100px;padding:0 16px;border-radius:50px;
 background:rgba(22,22,24,.8);border:3px solid rgba(255,255,255,.12);box-shadow:0 10px 30px rgba(0,0,0,.35)}}
.cm-av{{position:relative;width:66px;height:66px;border-radius:50%;background:#C9CBD0;flex:none;overflow:hidden;object-fit:cover}}
.cm-av i{{position:absolute;left:50%;top:13px;width:24px;height:24px;margin-left:-12px;border-radius:50%;background:#F4F5F7;
 box-shadow:0 30px 0 10px #F4F5F7}}
.cm-av.piccolo{{width:54px;height:54px;border:3px solid rgba(255,255,255,.85)}}
.cm-ph{{color:rgba(255,255,255,.45);font-weight:500;font-size:34px}}
.cm-tx{{color:#fff;font-weight:800;font-size:50px;letter-spacing:-1px}}
.cm-car{{width:4px;height:52px;background:#F4E06D;margin-left:-14px}}
.cm-in{{margin-left:auto;width:62px;height:62px;border-radius:50%;background:rgba(255,255,255,.18);color:#fff;font-weight:900;font-size:36px;
 display:flex;align-items:center;justify-content:center}}
.cm-riga{{position:absolute;left:0;top:0;display:flex;align-items:center;gap:16px;opacity:0;transform-origin:0 50%}}
.cm-bol{{position:relative;display:flex;align-items:baseline;gap:14px;padding:14px 34px 16px;border-radius:44px;background:#F4EFE6;color:#141414;
 box-shadow:0 10px 30px rgba(0,0,0,.3)}}
.cm-bol small{{font-size:30px;color:#8C8780;font-weight:500}}
.cm-bol b{{font-weight:800;font-size:56px;letter-spacing:-1.5px}}
.cm-cuore{{position:absolute;right:-18px;top:-20px;width:50px;height:50px;border-radius:50%;background:#fff;color:#EE4E6E;font-style:normal;
 font-size:30px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,.25)}}
.cm-filo{{position:absolute;left:31px;top:78px;width:40px;height:64px;border-left:3px solid rgba(255,255,255,.6);border-bottom:3px solid rgba(255,255,255,.6);
 border-bottom-left-radius:16px;opacity:0;transform-origin:0 0}}
.cm-r{{top:116px;left:74px}}
.cm-scura{{display:flex;align-items:center;gap:18px;min-height:64px;padding:10px 12px 10px 26px;border-radius:36px;background:rgba(22,22,24,.86);color:#fff}}
.cm-attesa{{display:block;width:200px;height:34px;border-radius:18px;background:rgba(255,255,255,.22);margin-right:14px}}
.cm-rt{{display:none;font-weight:600;font-size:34px}}
.cm-chip{{display:inline-flex;align-items:center;gap:8px;background:#F4E06D;color:#141414;font-weight:800;font-size:28px;padding:8px 20px;
 border-radius:24px;white-space:nowrap}}
.cm-chip b{{font-size:24px}}
.nm{{position:absolute;left:0;right:0;text-align:center;z-index:33;opacity:0;font-family:'Inter Tight';transform-origin:50% 40%}}
.nm-n{{font-weight:800;line-height:0.92;color:#EFE4D3;letter-spacing:-0.055em;text-shadow:0 6px 30px rgba(0,0,0,.35)}}
.nm-r{{position:absolute;left:0;right:0;margin-top:10px;font-weight:800;font-size:34px;letter-spacing:0.5px;color:#fff;opacity:0;
 text-shadow:0 2px 10px rgba(0,0,0,.5)}}
.fermo{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:4}}
.fe-buio{{position:absolute;inset:0;z-index:5;opacity:0;pointer-events:none;
 background:radial-gradient(ellipse 75% 60% at 50% 48%,rgba(10,10,14,.32) 0%,rgba(10,10,14,.5) 60%,rgba(6,6,10,.78) 100%)}}
.fe{{position:absolute;inset:0;z-index:33;opacity:0}}
.fe-svg{{position:absolute;inset:0}}
.fe-svg line{{stroke:rgba(255,255,255,.9);stroke-width:3}}
.fe-svg .anello{{fill:none;stroke:#fff;stroke-width:4}}
.fe-svg .punto{{fill:#F4E06D;stroke:#1a1a1a;stroke-width:3}}
.et{{position:absolute;display:flex;align-items:center;gap:8px;height:96px;padding:0 30px 0 18px;border-radius:22px;background:#F6F1E7;color:#141414;
 font-family:'Inter Tight';font-weight:800;font-size:50px;letter-spacing:-1.5px;white-space:nowrap;box-shadow:0 10px 30px rgba(0,0,0,.35);opacity:0}}
.et-n{{font-family:'{fm["famiglia"]}';font-weight:500;font-size:24px;letter-spacing:0;background:#F4E06D;color:#3a3420;border-radius:10px;
 width:56px;height:56px;display:flex;align-items:center;justify-content:center;margin-right:12px}}
.et-p{{opacity:0}}
.pc{{position:absolute;inset:0;z-index:36;opacity:0;background:#0E1A1A}}
.pc-lab{{position:absolute;left:0;right:0;text-align:center;font-family:'Inter Tight';font-weight:800;font-size:26px;letter-spacing:0.5px;color:#EDE4D6}}
.pc-tit{{position:absolute;left:60px;right:60px;text-align:center;font-family:'Instrument Serif';font-style:italic;font-size:100px;line-height:1;color:#EDE4D6}}
.pc-l{{display:inline-block;opacity:0}}
.pc-filo{{position:absolute;left:539px;width:2px;height:66px;background:rgba(237,228,214,.55);transform-origin:50% 0}}
.pc-passo{{position:absolute;left:0;right:0;text-align:center;font-family:'Inter Tight';font-weight:800;font-size:66px;line-height:1;
 letter-spacing:-2px;color:#EDE4D6}}
.pc-passo.serif{{font-family:'Instrument Serif';font-style:italic;font-weight:400;font-size:78px;letter-spacing:0}}
.ck{{position:absolute;left:70px;right:70px;z-index:33;opacity:0;padding:30px 34px 26px;border-radius:34px;font-family:'Inter Tight';
 background:rgba(26,26,30,.72);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:2px solid rgba(255,255,255,.12);
 box-shadow:0 20px 60px rgba(0,0,0,.45)}}
.ck-testa{{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}}
.ck-lab{{display:flex;align-items:center;gap:14px;font-weight:600;font-size:24px;letter-spacing:5px;color:rgba(255,255,255,.62)}}
.ck-lab i{{width:10px;height:10px;border-radius:50%;background:#F4E06D}}
.ck-conta{{font-weight:800;font-size:26px;padding:6px 18px;border-radius:20px;background:rgba(255,255,255,.12);color:#fff}}
.ck-barra{{display:flex;gap:10px;margin-bottom:22px}}
.ck-barra i{{flex:1;height:7px;border-radius:4px;background:rgba(255,255,255,.12);overflow:hidden}}
.ck-barra b{{display:block;height:100%;background:#F4E06D;transform:scaleX(0);transform-origin:0 50%}}
.ck-riga{{display:flex;align-items:center;gap:22px;height:96px;padding:0 16px;margin:0 -16px 16px;border-radius:20px}}
.ck-tondo{{flex:none;width:56px;height:56px;border-radius:50%;border:3px solid rgba(255,255,255,.35);display:flex;align-items:center;justify-content:center}}
.ck-tondo svg{{width:34px;height:34px;fill:none;stroke:#141414;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round;opacity:0}}
.ck-tondo.fatto{{background:#F4E06D;border-color:#F4E06D}}
.ck-tondo.fatto svg{{opacity:1}}
.ck-vuoto{{flex:1;height:22px;border-radius:11px;background:rgba(255,255,255,.1);max-width:420px}}
.ck-tx{{font-weight:800;font-size:50px;letter-spacing:-1.5px;color:#fff;opacity:0;white-space:nowrap}}
.ck-stella{{position:absolute;right:-14px;top:-18px;color:#F4E06D;font-style:normal;font-size:40px;opacity:0;text-shadow:0 0 14px #F4E06D}}
.ck-stella.b{{right:auto;left:-16px;top:auto;bottom:40%;font-size:26px}}
.ods{{position:absolute;right:40px;top:150px;z-index:33;opacity:0;font-family:'Inter Tight'}}
.od{{position:absolute;right:0;top:0;opacity:0;transform-origin:100% 0;text-align:right}}
.od-pann{{display:inline-flex;align-items:center;gap:10px;padding:14px;border-radius:26px;background:linear-gradient(#232831,#151920);
 box-shadow:0 18px 50px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.08)}}
.od-cella{{position:relative;width:112px;height:150px;border-radius:14px;overflow:hidden;
 background:linear-gradient(#2c323c 0%,#1a1e25 48%,#0f1217 52%,#20252d 100%);box-shadow:inset 0 2px 6px rgba(0,0,0,.6)}}
.od-cella:after{{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:rgba(0,0,0,.55)}}
.od-str{{position:absolute;left:0;right:0;top:0;display:flex;flex-direction:column}}
.od-str b{{height:150px;line-height:150px;text-align:center;font-weight:800;font-size:118px;color:#F2EADB;letter-spacing:-3px}}
.od-segno{{font-weight:800;font-size:118px;line-height:150px;color:#F4E06D;padding:0 4px}}
.od-lab{{margin-top:12px;border-top:4px solid #F4E06D;padding-top:8px}}
.od-lab span{{font-weight:800;font-size:38px;letter-spacing:1px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.5)}}
.od-sotto{{font-weight:800;font-size:24px;letter-spacing:2px;color:#fff;opacity:0;text-shadow:0 2px 10px rgba(0,0,0,.6)}}
.pl{{position:absolute;left:40px;right:40px;display:flex;justify-content:center;gap:16px;z-index:32;opacity:0;font-family:'Inter Tight'}}
.pl-p{{padding:12px 28px 14px;border-radius:40px;border:2.5px solid rgba(255,255,255,.78);background:rgba(0,0,0,.18);color:#fff;
 font-weight:600;font-size:36px;white-space:nowrap;opacity:0;text-shadow:0 2px 8px rgba(0,0,0,.4)}}
.pr2{{position:absolute;left:100px;right:100px;z-index:33;opacity:0;font-family:'Inter Tight';padding:40px 40px 34px;border-radius:30px;
 border:2.5px solid rgba(255,255,255,.55);background:rgba(10,10,12,.22);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}}
.pr2-lab{{position:absolute;left:50%;top:-24px;transform:translateX(-50%);padding:0 22px;font-weight:500;font-size:32px;color:#fff;
 text-shadow:0 2px 8px rgba(0,0,0,.6)}}
.pr2-tx{{font-weight:800;letter-spacing:-1.5px;color:#F2EADB;line-height:1.12;text-shadow:0 2px 12px rgba(0,0,0,.35);min-height:60px}}
.pr2-car{{display:inline-block;width:4px;height:1em;background:#fff;vertical-align:-0.12em;margin-left:4px}}
.tf-scena{{position:absolute;width:400px;height:820px;z-index:31;perspective:1600px}}
.tf{{position:absolute;inset:0;border-radius:64px;background:#0B0B0D;padding:16px;opacity:0;font-family:'Inter Tight';
 box-shadow:0 0 0 3px #2a2a2e,0 0 0 5px #0a0a0a,0 40px 80px rgba(0,0,0,.55);overflow:hidden}}
.tf:before{{content:"";position:absolute;inset:16px;border-radius:50px;background:linear-gradient(#17181c,#111215)}}
.tf>*{{position:relative}}
.tf-isola{{position:absolute;left:50%;top:28px;width:116px;height:34px;margin-left:-58px;border-radius:20px;background:#000;z-index:3}}
.tf-stato{{display:flex;justify-content:space-between;padding:16px 30px 0;color:#fff;font-size:22px}}
.tf-stato span{{font-size:14px;letter-spacing:2px;padding-top:4px}}
.tf-testa{{display:flex;align-items:center;gap:14px;padding:26px 24px 16px;color:#fff}}
.tf-testa b{{display:block;font-size:26px;font-weight:700}}
.tf-testa small{{display:flex;align-items:center;gap:6px;font-size:18px;color:rgba(255,255,255,.55)}}
.tf-testa small i{{width:8px;height:8px;border-radius:50%;background:#4CD964}}
.tf-av{{width:52px;height:52px;border-radius:50%;background:#F4E06D;color:#141414;font-size:26px;display:flex;align-items:center;justify-content:center}}
.tf-chat{{padding:6px 18px;display:flex;flex-direction:column;gap:12px}}
.tf-m{{max-width:86%;padding:14px 18px;border-radius:20px;font-size:23px;line-height:1.25;opacity:0}}
.tf-m.app{{align-self:flex-start;background:#26282e;color:#fff}}
.tf-m.io{{align-self:flex-end;background:#F4E06D;color:#141414;font-weight:600}}
.tf-sch{{position:relative;padding:20px;border-radius:22px;background:#202228;color:#fff;opacity:0}}
.tf-sl{{font-size:16px;letter-spacing:3px;color:#F4E06D;font-weight:700;margin-bottom:10px}}
.tf-st{{font-size:34px;font-weight:800;line-height:1.1;letter-spacing:-1px;margin-bottom:18px}}
.tf-bot{{height:62px;border-radius:31px;background:#fff;color:#141414;font-weight:800;font-size:26px;display:flex;align-items:center;justify-content:center}}
.tf-onda{{position:absolute;left:50%;bottom:30px;width:80px;height:80px;margin-left:-40px;border-radius:50%;border:3px solid #F4E06D;opacity:0}}
.tf-scrivi{{position:absolute;left:30px;right:30px;bottom:34px;height:58px;border-radius:30px;background:#1f2126;color:rgba(255,255,255,.4);
 font-size:20px;display:flex;align-items:center;justify-content:space-between;padding:0 8px 0 22px}}
.tf-scrivi span{{width:42px;height:42px;border-radius:50%;background:#2c2e34;color:#fff;display:flex;align-items:center;justify-content:center}}
.tf-riflesso{{position:absolute;inset:0;border-radius:64px;background:linear-gradient(115deg,rgba(255,255,255,.10) 0%,rgba(255,255,255,0) 35%);pointer-events:none}}
.ob{{position:absolute;inset:0;opacity:0;pointer-events:none}}
.ob-c{{position:absolute;left:0;top:0;width:300px;height:534px;border-radius:24px;object-fit:cover;border:3px solid rgba(255,255,255,.9);
 box-shadow:0 20px 50px rgba(0,0,0,.45)}}
.sfu{{position:absolute;inset:0;z-index:45;opacity:0;pointer-events:none;overflow:hidden}}
.sfu-calda{{position:absolute;inset:-20%;opacity:0;mix-blend-mode:screen;
 background:radial-gradient(ellipse 70% 60% at 25% 75%,#FFC266 0%,#FF8A3D 40%,rgba(255,110,50,.35) 70%,rgba(255,110,50,.18) 100%),
 radial-gradient(ellipse 55% 50% at 80% 25%,#FFF0C8 0%,rgba(255,190,110,0) 70%)}}
.sfu-bianca{{position:absolute;inset:0;opacity:0;background:#FFFBF4}}
.tbox{{position:absolute;left:0;right:0;text-align:center;z-index:34;opacity:0}}
.tbox span{{display:inline-block;max-width:820px;padding:16px 30px 18px;background:#fff;color:#111;border-radius:6px;
 font-family:'{ft["famiglia"]}';font-weight:800;font-size:48px;line-height:1.15;box-shadow:0 8px 24px rgba(0,0,0,.25)}}
.scn{{position:absolute;inset:0;z-index:37;opacity:0;overflow:hidden;
 background:radial-gradient(ellipse 90% 70% at 50% 40%,{banda} 0%,{scuro} 75%);color:#fff}}
.scn.carta{{background:#F2EEE6;color:{scuro};
 background-image:radial-gradient(rgba(0,0,0,.035) 1px,transparent 1.2px),radial-gradient(rgba(0,0,0,.025) 1px,transparent 1.2px);
 background-size:7px 7px,11px 11px;background-position:0 0,3px 5px}}
.sc-lab{{position:absolute;left:0;right:0;top:200px;text-align:center;{M};font-size:22px;letter-spacing:4px;color:{acc}}}
.sc-lab.sx{{left:90px;text-align:left}}
.sc-tit{{position:absolute;left:60px;right:60px;top:240px;text-align:center}}
.sc-r{{{W};font-size:84px;line-height:1.02;opacity:0}}
.sc-r.targa-sc{{display:inline-block;background:{acc};color:#fff;padding:2px 18px 6px;border-radius:8px;margin-top:6px}}
.bar{{position:absolute;border-radius:18px;background:linear-gradient(90deg,#C94A12 0%,{acc} 35%,{luce} 60%,{acc} 100%);
 box-shadow:0 4px 10px rgba(0,0,0,.25)}}
.bar.spenta{{background:rgba(255,255,255,.08);box-shadow:none}}
.bar-on{{position:absolute;inset:0;border-radius:inherit;opacity:0;background:linear-gradient(90deg,#C94A12 0%,{acc} 35%,{luce} 60%,{acc} 100%);
 box-shadow:0 4px 10px rgba(0,0,0,.25)}}
.carta .bar.spenta{{background:rgba(0,0,0,.08)}}
.sc-tel{{position:absolute;left:300px;top:480px;width:480px;height:900px;border:4px solid rgba(255,255,255,.45);border-radius:56px}}
.carta .sc-tel{{border-color:rgba(0,0,0,.35)}}
.sc-conta{{position:absolute;left:0;right:0;text-align:center;display:flex;align-items:baseline;justify-content:center;gap:14px}}
.sc-conta b{{{W};font-size:70px;color:{acc}}}
.sc-conta span{{{M};font-size:24px;letter-spacing:3px}}
.sc-timbro{{position:absolute;left:0;right:0;margin:0 auto;top:880px;transform-origin:50% 50%;width:max-content;padding:0 40px 10px;text-align:center;{W};font-size:120px;
 color:{scuro};background:{acc};border:8px solid {scuro};border-radius:22px;padding:0 0 10px;opacity:0;box-shadow:0 14px 40px rgba(0,0,0,.35)}}
.sc-timbro.sx{{left:90px;right:auto;margin:0;padding:0 34px 10px}}
.sc-num{{position:absolute;left:0;right:0;top:980px;text-align:center;opacity:0}}
.sc-num b{{display:block;{W};font-size:300px;line-height:1;color:{acc}}}
.sc-num span{{{W};font-size:70px}}
.sc-riga{{position:absolute;left:90px;right:60px;{W};font-size:118px;line-height:1;opacity:0;white-space:nowrap}}
.sc-barra{{position:absolute;left:-10px;top:52%;height:14px;width:calc(100% - 50px);max-width:520px;background:{acc};transform:scaleX(0);transform-origin:0 50%}}
.sc-play{{position:absolute;left:330px;top:560px;width:420px;height:780px;border-radius:50px;background:#fff;border:4px solid rgba(0,0,0,.12);
 box-shadow:0 20px 50px rgba(0,0,0,.18);overflow:hidden}}
.sc-pl{{position:absolute;left:34px;top:40px;{M};font-size:18px;letter-spacing:2px;color:rgba(0,0,0,.4)}}
.sc-tasto{{position:absolute;left:50%;top:50%;width:110px;height:110px;margin:-55px 0 0 -55px;border-radius:50%;background:{acc}}}
.sc-tasto:after{{content:"";position:absolute;left:44px;top:32px;border-left:34px solid #fff;border-top:23px solid transparent;border-bottom:23px solid transparent}}
.sc-pronto{{position:absolute;inset:0;background:{scuro};color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;
 {W};font-size:56px;opacity:0}}
.sc-pronto b{{width:120px;height:120px;border-radius:50%;background:{acc};color:#fff;font-size:70px;display:flex;align-items:center;justify-content:center}}
.sc-pell{{position:absolute;left:0;right:0;top:820px;height:400px;background:#0b0b0b;overflow:hidden;
 border-top:28px dashed #0b0b0b;border-bottom:28px dashed #0b0b0b;
 background-image:repeating-linear-gradient(90deg,transparent 0 24px,rgba(255,255,255,.25) 24px 40px);background-size:100% 18px;background-repeat:repeat-x}}
.sc-film{{position:absolute;left:0;top:44px;display:flex;gap:30px}}
.sc-film img{{width:170px;height:302px;object-fit:cover;border-radius:8px}}
.sc-adesso-l{{position:absolute;left:538px;top:790px;width:5px;height:460px;background:{acc}}}
.sc-adesso{{position:absolute;left:50%;top:1280px;transform:translateX(-50%);background:{acc};color:#fff;{M};font-size:28px;letter-spacing:3px;
 padding:10px 26px;border-radius:30px;opacity:0}}
.fc-marchio{{position:absolute;left:90px;top:300px;display:flex;align-items:center;gap:18px;{W};font-size:40px;font-stretch:100%}}
.fc-marchio i{{font-style:normal;{M};font-size:24px;background:#fff;color:{scuro};border-radius:10px;padding:10px 12px}}
.fc-tit{{position:absolute;left:90px;right:60px;top:430px}}
.fc-r{{{W};line-height:1.08;white-space:nowrap}}
.fc-acc{{color:{acc}}}
.fc-barrata{{position:relative;display:inline-block;--b:0}}
.fc-barrata:after{{content:"";position:absolute;left:-6px;right:-6px;top:52%;height:12px;background:{acc};transform:scaleX(var(--b));transform-origin:0 50%}}
.fc-barre{{display:flex;gap:18px;margin-top:40px}}
.fc-sc{{position:absolute;left:0;right:0;top:1150px;text-align:center;{M};font-size:24px;letter-spacing:4px;color:rgba(255,255,255,.75)}}
.fc-freccia{{position:absolute;left:50%;top:1210px;width:110px;height:110px;margin-left:-55px;border-radius:50%;background:{acc};color:#fff;
 font-size:64px;font-weight:900;display:flex;align-items:center;justify-content:center}}
{css_sott}
</style>
<script src="{GSAP}"></script>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1080" data-height="1920">
<audio id="voce" src="assets/tagliato.mp4" data-start="0" data-media-start="0" data-duration="{D:.3f}" data-volume="1"></audio>
{chr(10).join(r.audio)}
<div id="cam" class="cam"><video id="bg" src="assets/tagliato.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{D:.3f}"></video>
{chr(10).join(r.camera)}</div>
<div class="mirino" id="mir"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i>
<div class="mir-lab" style="left:150px"><span class="rosso">●</span> REC <span id="tc">00:00:00</span></div>
<div class="mir-lab" style="right:200px">4K · 30FPS</div></div>
{chr(10).join(r.corpo)}
{zone_html}
</div>
<script>
const tl = gsap.timeline({{paused: true}});
const SEGNI = "#%&@$<>*+=?/_01XZ";
{sottotitoli.JS}
function decodifica(sel, testo, da, dur) {{
  const el = document.querySelector(sel); const o = {{p: 0}};
  tl.set(el, {{textContent: ""}}, Math.max(0, da - 0.001));
  tl.to(o, {{p: 1, duration: dur, ease: "none", onUpdate: () => {{
    const n = Math.floor(o.p * testo.length * 1.4); let s = "";
    for (let i = 0; i < testo.length; i++) {{
      const c = testo[i];
      if (c === " " || i < n - testo.length * 0.4) s += c;
      else if (i < n) s += SEGNI[(i * 7 + Math.floor(o.p * 30)) % SEGNI.length];
    }}
    el.textContent = o.p >= 1 ? testo : s;
  }}}}, da);
}}
function scrivi(sel, testo, da, a) {{
  const el = document.querySelector(sel); const o = {{p: 0}};
  tl.to(o, {{p: 1, duration: a - da, ease: "none", onUpdate: () => {{ el.textContent = testo.slice(0, Math.round(o.p * testo.length)); }}}}, da);
}}
function conta(sel, da_n, a_n, da, dur) {{
  const el = document.querySelector(sel); const o = {{v: da_n}};
  tl.to(o, {{v: a_n, duration: dur, ease: "power1.out", onUpdate: () => {{ el.textContent = Math.round(o.v); }}}}, da);
}}
function cronometro(sel, da, a) {{
  const el = document.querySelector(sel); const o = {{t: 0}};
  tl.to(o, {{t: a - da, duration: a - da, ease: "none", onUpdate: () => {{
    const s = Math.floor(o.t), f = Math.floor((o.t % 1) * 30);
    el.textContent = "00:" + String(s).padStart(2, "0") + ":" + String(f).padStart(2, "0"); }}}}, da);
}}
function orbita(sel, cx, cy, da, a, giri) {{
  // le copertine su un'ellisse attorno alla persona: davanti (z alto, grandi) o dietro il ritaglio (z basso, piccole)
  const carte = [...document.querySelectorAll(sel + " .ob-c")]; const o = {{t: 0}};
  const posa = () => {{
    const entra = Math.min(o.t / 0.6, 1), esce = Math.min(Math.max((a - da - o.t) / 0.5, 0), 1), f = entra * esce;
    carte.forEach((c, i) => {{
      const ang = (i / carte.length) * Math.PI * 2 + (o.t / (a - da)) * Math.PI * 2 * giri;
      const z = Math.cos(ang), x = cx + Math.sin(ang) * 470 * f, y = cy - 120 + z * 70 * f - Math.sin(ang) * 40;
      const s = (0.62 + 0.28 * (z + 1) / 2) * (0.3 + 0.7 * f);
      c.style.transform = `translate(${{x - 150}}px, ${{y - 267}}px) scale(${{s}}) rotateY(${{Math.sin(ang) * -25}}deg)`;
      c.style.zIndex = z > 0 ? 6 : 1; c.style.filter = `brightness(${{0.62 + 0.38 * (z + 1) / 2}})`; c.style.opacity = f;
    }});
  }};
  posa();
  tl.to(o, {{t: a - da, duration: a - da, ease: "none", onUpdate: posa}}, da);
}}
function contaCon(sel, segno, da_n, a_n, da, dur) {{
  const el = document.querySelector(sel); const o = {{v: da_n}};
  tl.to(o, {{v: a_n, duration: dur, ease: "power1.out", onUpdate: () => {{ el.textContent = segno + Math.round(o.v); }}}}, da);
}}
cronometro("#tc", 0, {D:.3f});
tl.to("#mir", {{opacity: 0, duration: 0.25}}, {MIRINO_FINO if stile.get("mirino", True) else 0});
{chr(10).join(r.tl)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    with open(os.path.join(reel, "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina)
    with open(os.path.join(reel, "hyperframes.json"), "w", encoding="utf-8") as f:
        json.dump({"paths": {"assets": "assets"}}, f)
    print(f"Reel costruito (motore grafica): {len(piano.get('elementi', []))} elementi, {len(r.audio)} suoni, "
          f"finale da {finale_da:.1f} s, durata {D:.1f} s")
