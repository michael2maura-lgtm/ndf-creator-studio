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
   {"tipo": "telefono", "da": 29.3, "a": 37.9, "titoli": [["SECONDA COSA", "UN REEL", 29.4], ["ALMENO", "60 SECONDI", 33.0]]}],
 "finale_da": 64.75, "finale_sopra": "TE LO INVIO IN DIRECT", "finale_testo": "COMMENTA", "finale_bottone": "INFO"}

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

from comune import FFMPEG, durata

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
MIRINO_FINO = 6.2  # il mirino REC solo in apertura: per tutto il reel stanca


class Reel:
    def __init__(self, stile, cart_stile, reel, D):
        self.stile, self.cart_stile, self.reel, self.D = stile, cart_stile, reel, D
        self.assets = os.path.join(reel, "assets")
        self.corpo, self.tl, self.audio, self.nascondi, self.transizioni = [], [], [], [], []

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
        os.link(os.path.join(cart, "tagliato.mp4"), dest)
    except OSError:
        shutil.copy2(os.path.join(cart, "tagliato.mp4"), dest)
    ft, fm = stile["font"]["titoli"], stile["font"]["mono"]
    for f in (ft, fm):
        shutil.copy2(os.path.join(cart_stile, f["file"]), os.path.join(r.assets, os.path.basename(f["file"])))

    petto = min(faccia["mento"] + 70, 1180)  # titoli e targhette sul petto, sotto il mento
    y_sub = min(faccia["mento"] + 160, 1300)
    ap = piano.get("apertura")
    if ap:
        r.titolo(ap["sopra"], ap["targa"], 0.0, ap.get("a", 2.0), petto - 20)
        r.nascondi.append((0.0, ap.get("a", 2.0)))
        r.suono("apertura", 0.0, 0.4)
    for e in sorted(piano.get("elementi", []), key=lambda x: x.get("da", x.get("voci", [[0, 0, 0]])[0][2])):
        tipo = e["tipo"]
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
    finale_da = piano.get("finale_da", D - 2.3)
    r.finale(piano, finale_da)
    if piano.get("musica", True):
        r.musica()
    r.sottotitoli(parole, {p.lower() for p in piano.get("parole_chiave", [])}, y_sub)

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
</style>
<script src="{GSAP}"></script>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1080" data-height="1920">
<audio id="voce" src="assets/tagliato.mp4" data-start="0" data-media-start="0" data-duration="{D:.3f}" data-volume="1"></audio>
{chr(10).join(r.audio)}
<div id="cam" class="cam"><video id="bg" src="assets/tagliato.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{D:.3f}"></video></div>
<div class="mirino" id="mir"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i>
<div class="mir-lab" style="left:150px"><span class="rosso">●</span> REC <span id="tc">00:00:00</span></div>
<div class="mir-lab" style="right:200px">4K · 30FPS</div></div>
{chr(10).join(r.corpo)}
{zone_html}
</div>
<script>
const tl = gsap.timeline({{paused: true}});
const SEGNI = "#%&@$<>*+=?/_01XZ";
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
cronometro("#tc", 0, {D:.3f});
tl.to("#mir", {{opacity: 0, duration: 0.25}}, {MIRINO_FINO});
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
