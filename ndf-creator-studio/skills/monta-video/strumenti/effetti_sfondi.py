"""Effetti di sfondi, liste e messaggi (18/11/2026), rifatti da noi guardando come si muovono gli effetti di
riferimento (mai copiato il codice). Motore grafica, tempi del video TAGLIATO. Mentre ci sono, i sottotitoli si nascondono.

 {"tipo": "immagini", "da", "a", "pagine": [{"pagina": "articolo", "testata": "NOTIZIE", "titolo": "riga 1|riga 2", "t": t},
     {"pagina": "statistiche", "titolo": "Le mie visualizzazioni", "valori": [3, 5, 4, 8, 12], "t": t},
     {"pagina": "griglia", "t": t}, {"file": "screenshot.jpg", "t": t}]}
     Le immagini dietro di me: diventi un adesivo grande con il bordo bianco, spostato in basso, e dietro di te, a tutto
     sfondo, cambia una schermata per ogni cosa detta. Le schermate le costruisce lo studio con le parole del video:
     "articolo" (pagina di giornale con il titolo detto), "statistiche" (finestra con le barre che salgono: valori veri
     se detti, se no solo la crescita), "griglia" (i tuoi reel, fotogrammi del video). "file": un'immagine 
     del CLIENTE (solo immagini ferme: di una clip si prende un fotogramma) (DATI/immagini o DATI/clip), solo se te la dà lui. Mai foto o clip prese a caso solo per riempire.
 {"tipo": "scorri", "da", "a", "voci": [["Giulia", "ho venduto il corso"], ["Marta", "iscritta al Club"]]}
     Lista che scorre: il video si scurisce un po' e sopra arriva una lista di PERSONE (poche: salgono una alla volta
     e restano; tante: scorrono veloci): l'iniziale colorata, il nome, quello che hanno ottenuto e la spunta, come una
     chat. È una prova sociale e la sua forza è la QUANTITÀ: una marea di risultati che scorre veloce su tutto lo
     schermo. Chiedi al cliente 12-20 risultati veri (nome + cosa hanno ottenuto); con meno di 8 è meglio "elenco".
     Solo persone vere (clienti, studenti) con il loro nome, mai cose astratte ("programmi", "stress") e mai nomi o
     facce inventati. Se il video nomina clienti ma non hai i nomi, chiedili. Una foto al posto
     dell'iniziale ([nome, riga, "foto.jpg"]) solo se il cliente dà la foto vera di quella persona.
 {"tipo": "messaggio", "da", "a", "nome": "Sara", "testo": "Grazie! Ho venduto il corso", "cuore": t}
     Messaggio in arrivo: sul petto arriva un messaggio diretto con il nome e il tondo dell'iniziale; poi sul fumetto
     compare il cuore ("cuore": quando). Per leggere il messaggio di una cliente.
 {"tipo": "fondale", "da", "a", "frasi": [["Ti faccio", "vedere", t], ["una cosa", "", t]]}
     Apertura tipografica: dietro di te scende un fondale nei colori dello stile e le parole del gancio compaiono
     enormi, una schermata per frase (riga piccola e riga grande); tu resti davanti. Per l'apertura, 1 volta.
"""
import html
import os
import shutil
import subprocess

from comune import DATI, FFMPEG
from effetti_carte import _cima, _cx

E = html.escape


def _css(r):
    if getattr(r, "css_sfondi", False):
        return
    r.css_sfondi = True
    r.font_extra("InterTight.ttf")
    r.corpo.append(
        "<style>"
        "@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}"
        ".es-fondo{position:absolute;inset:0;opacity:0}"
        ".es-fin{position:absolute;left:50px;right:50px;top:230px;height:760px;border-radius:30px;overflow:hidden;"
        "background:#fff;box-shadow:0 20px 44px rgba(0,0,0,.3)}"
        ".es-fin>*{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0}"
        ".es-velo{position:absolute;inset:0;z-index:29;opacity:0;pointer-events:none}"
        ".es-lista{position:absolute;left:0;top:0;width:1080px;z-index:31;font-family:'Inter Tight'}"
        ".es-r{position:relative;height:122px}"
        ".es-r .ic{position:absolute;left:80px;top:10px;width:92px;height:92px;border-radius:50%;display:grid;place-items:center;"
        "font-weight:900;font-size:50px;overflow:hidden;box-shadow:0 0 0 4px rgba(255,255,255,.85)}"
        ".es-r .ic img{width:100%;height:100%;object-fit:cover}"
        ".es-r .no{position:absolute;left:200px;top:12px;font-weight:800;font-size:42px;color:#fff;white-space:nowrap;"
        "text-shadow:0 2px 10px rgba(0,0,0,.45)}"
        ".es-r .ri{position:absolute;left:200px;top:62px;font-weight:600;font-size:30px;color:rgba(255,255,255,.78);white-space:nowrap;"
        "text-shadow:0 2px 10px rgba(0,0,0,.45)}"
        ".es-r .ok{position:absolute;right:90px;top:30px;width:52px;height:52px;border-radius:50%;display:grid;place-items:center}"
        ".es-dm{position:absolute;z-index:31;opacity:0;font-family:'Inter Tight'}"
        ".es-dm .chi{display:flex;align-items:center;gap:16px;margin:0 0 14px 10px;font-weight:800;font-size:34px;color:#fff;"
        "text-shadow:0 2px 10px rgba(0,0,0,.55)}"
        ".es-dm .av{width:66px;height:66px;border-radius:50%;display:grid;place-items:center;font-weight:900;font-size:34px;color:#fff;"
        "box-shadow:0 4px 12px rgba(0,0,0,.3);text-shadow:none}"
        ".es-dm .bo{position:relative;display:inline-block;border-radius:40px 40px 40px 12px;padding:30px 40px;font-weight:700;"
        "font-size:44px;line-height:1.22;box-shadow:0 14px 32px rgba(0,0,0,.32);max-width:820px}"
        ".es-dm .cu{position:absolute;right:-22px;bottom:-24px;width:70px;height:70px;border-radius:50%;background:#fff;"
        "display:grid;place-items:center;box-shadow:0 6px 16px rgba(0,0,0,.3);opacity:0}"
        ".es-fr{position:absolute;left:30px;right:30px;text-align:center;font-family:'Inter Tight';font-weight:900;"
        "letter-spacing:-.03em;line-height:.92;opacity:0;white-space:nowrap}"
        "</style>")


def _contorno(s=8):
    ombre = " ".join(f"drop-shadow({x}px {y}px 0 #fff)" for x, y in ((s, 0), (-s, 0), (0, s), (0, -s)))
    return f'filter:"{ombre} drop-shadow(0 14px 22px rgba(0,0,0,.35))"'


def _foto_video(r, nome, secondo, faccia):
    from effetti_carte import _foto
    return _foto(r, nome, secondo=secondo, w=512, h=612, faccia=faccia)


def _file(nome):
    for cartella in ("immagini", "clip"):
        p = os.path.join(DATI, cartella, nome)
        if os.path.exists(p):
            return p
    return None


# ---------------------------------------------------------------- le immagini dietro di me
def immagini(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    c = r.stile["colori"]
    voci = [x if isinstance(x, dict) else {"file": x[0], "t": x[1]} if isinstance(x, (list, tuple)) else {"file": x}
            for x in (e.get("pagine") or e.get("foto") or [])][:6]
    n = len(r.camera)
    acc, chiaro = c.get("accento", "#E86530"), c.get("accento_luce", "#FFB27A")
    bruno, crema = c.get("banda", "#4A2412"), "#FBF8F2"
    pezzi, anim = [], []
    for k, v in enumerate(voci):
        t = max(v.get("t", da + k * 1.2) or da, da)
        pid = f"ei{n}f{k}"
        tipo = v.get("pagina")
        if tipo == "articolo":
            # una pagina di giornale costruita con le parole dette: testata, titolo su due righe, foto, righe di testo
            r1, _, r2 = v.get("titolo", "").partition("|")
            d1 = max(min(88, int(980 / (max(len(r1), 3) * 0.55))), 52)
            d2 = max(min(88, int(980 / (max(len(r2), 3) * 0.55))), 52)
            righe = "".join(f'<i style="position:absolute;left:56px;top:{900 + q * 64}px;width:{[960, 900, 940, 720, 960, 860, 930, 640, 960, 880, 940, 700, 960, 820, 900][q]}px;'
                            f'height:24px;border-radius:12px;background:#DED7CD"></i>' for q in range(15))
            html_p = (f'<div style="position:absolute;left:0;right:0;top:0;height:140px;background:{bruno};display:flex;align-items:center;'
                      f'padding:0 56px;font:800 34px \'Inter Tight\';letter-spacing:.14em;color:#fff">{E(v.get("testata", "NOTIZIE").upper())}</div>'
                      f'<div id="{pid}a" style="position:absolute;left:56px;right:40px;top:200px;font:900 {d1}px/1.05 \'Inter Tight\';color:#231F1C;white-space:nowrap">{E(r1)}</div>'
                      f'<div id="{pid}b" style="position:absolute;left:56px;right:40px;top:{200 + d1 * 1.08:.0f}px;font:900 {d2}px/1.05 \'Inter Tight\';color:{acc};white-space:nowrap">{E(r2)}</div>'
                      f'<div style="position:absolute;left:56px;right:56px;top:{230 + d1 * 1.08 + d2 * 1.1:.0f}px;height:400px;border-radius:20px;'
                      f'background:linear-gradient(135deg,{acc},{chiaro})"></div>{righe}')
            fondo = crema
            anim.append(f'tl.fromTo(["#{pid}a","#{pid}b"],{{opacity:0,x:-40}},{{opacity:1,x:0,duration:.3,stagger:.12,ease:"power3.out",immediateRender:false}},{t + 0.1:.3f});')
        elif tipo == "statistiche":
            # la finestra delle statistiche: le barre salgono
            valori = v.get("valori") or [3, 5, 4, 7, 9, 12]
            mx = max(valori)
            barre = "".join(f'<i id="{pid}s{q}" style="position:absolute;left:{70 + q * (880 // len(valori))}px;bottom:50px;width:{int(880 / len(valori) * 0.68)}px;'
                            f'height:{int(440 * x / mx)}px;border-radius:14px 14px 0 0;background:{chiaro};transform-origin:50% 100%"></i>'
                            for q, x in enumerate(valori))
            html_p = (f'<div style="position:absolute;left:40px;right:40px;top:260px;height:680px;border-radius:26px;background:#2A2420;overflow:hidden;'
                      f'box-shadow:0 20px 44px rgba(0,0,0,.3)"><div style="height:66px;background:#3B332E;display:flex;align-items:center;gap:14px;padding:0 28px">'
                      f'<i style="width:20px;height:20px;border-radius:50%;background:#FF6159"></i><i style="width:20px;height:20px;border-radius:50%;background:#FFBD2E"></i>'
                      f'<i style="width:20px;height:20px;border-radius:50%;background:#28C941"></i></div>'
                      f'<div style="position:absolute;left:46px;top:100px;font:800 48px \'Inter Tight\';color:#fff">{E(v.get("titolo", ""))}</div>{barre}</div>')
            fondo = acc
            anim.append(f'tl.fromTo("[id^={pid}s]",{{scaleY:0}},{{scaleY:1,duration:.5,stagger:.08,ease:"back.out(1.4)",immediateRender:false}},{t + 0.15:.3f});')
        elif tipo == "griglia":
            # i tuoi reel: una griglia di riquadri con i fotogrammi del video
            tess = ""
            for q in range(6):
                f = _foto_video(r, f"gr-{n}-{k}-{q}.jpg", r.D * (q + 0.5) / 6, faccia)
                tess += (f'<i id="{pid}g{q}" style="position:absolute;left:{(q % 2) * 540 + 14}px;top:{(q // 2) * 640 + 14}px;width:512px;height:612px;'
                         f'border-radius:18px;background:{chiaro} url(assets/{f}) center/cover"></i>')
            html_p = tess
            fondo = acc
            anim.append(f'tl.fromTo("[id^={pid}g]",{{opacity:0,scale:.7}},{{opacity:1,scale:1,duration:.3,stagger:.06,ease:"back.out(1.6)",immediateRender:false}},{t + 0.05:.3f});')
        else:
            src = _file(v.get("file", ""))
            if not src:
                continue
            f = os.path.basename(src)
            dest = os.path.join(r.assets, f)
            if not os.path.exists(dest):
                shutil.copy2(src, dest)
            if f.lower().endswith((".mp4", ".mov", ".webm")):
                # dietro di te solo immagini ferme: si leggono meglio di una clip (Michael, 19/11). Di una clip si
                # prende un fotogramma.
                ferma = os.path.splitext(f)[0] + "-ferma.jpg"
                subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", "1.0", "-i", dest, "-frames:v", "1", "-q:v", "2",
                                os.path.join(r.assets, ferma)], capture_output=True)
                if not os.path.exists(os.path.join(r.assets, ferma)):
                    continue
                f, dest = ferma, os.path.join(r.assets, ferma)
            try:
                from PIL import Image
                w, h = Image.open(dest).size
            except Exception:
                w, h = 9, 16
            if w > h * 1.05:
                alto = int(1000 * h / w)
                html_p = (f'<img src="assets/{f}" style="position:absolute;left:40px;top:{max(260, 640 - alto // 2)}px;width:1000px;'
                          f'height:{alto}px;object-fit:cover;border-radius:24px;box-shadow:0 20px 44px rgba(0,0,0,.35)">')
                fondo = acc
            else:
                html_p = f'<img src="assets/{f}" style="width:100%;height:100%;object-fit:cover">'
                fondo = "#fff"
        pezzi.append((pid, t, f'<div id="{pid}" style="position:absolute;inset:0;opacity:0;background:{fondo}">{html_p}</div>'))
    if not pezzi:
        return
    pagine = "".join(x[2] for x in pezzi)
    r.camera.insert(0, f'<div class="es-fondo" id="ei{n}" style="background:{acc}">{pagine}</div>')
    sel = r.ritaglio(da - 0.1, a + 0.1)
    T = r.tl.append
    # tu diventi un adesivo grande, spostato in basso, con il bordo bianco
    T(f'tl.set("#ei{n}",{{opacity:1}},{da:.3f});tl.set("{sel}",{{opacity:1,transformOrigin:"540px 960px",{_contorno(9)}}},{da:.3f});'
      f'tl.fromTo("{sel}",{{scale:1,y:0}},{{scale:.75,y:300,duration:.45,ease:"power3.inOut",immediateRender:false}},{da:.3f});'
      f'tl.to("{sel}",{{scale:1,y:0,duration:.4,ease:"power3.inOut"}},{a - 0.4:.3f});'
      f'tl.to("#ei{n}",{{opacity:0,duration:.25}},{a - 0.3:.3f});'
      f'tl.set("{sel}",{{opacity:0,filter:"none",scale:1,y:0}},{a:.3f});')
    for k, (pid, t, _) in enumerate(pezzi):
        t = da + 0.05 if k == 0 else t
        T(f'tl.fromTo("#{pid}",{{opacity:0,scale:1.04}},{{opacity:1,scale:1,duration:.18,ease:"power2.out",immediateRender:false}},{t:.3f});')
        if k:
            T(f'tl.set("#{pezzi[k - 1][0]}",{{opacity:0}},{t + 0.18:.3f});')
            r.suono_libreria("hyperframes/whoosh-short.mp3", t, 0.22)
    for x in anim:
        T(x)
    r.suono("transizione", da, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- lista che scorre
_SPUNTA = '<svg width="30" height="30" viewBox="0 0 30 30"><path d="M7 15.5 L12.5 21 L23 9.5" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def scorri(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    voci = [list(x) if isinstance(x, (list, tuple)) else [x, ""] for x in e.get("voci", [])]
    if not voci:
        return
    for v in voci:   # la foto della persona, se c'è
        f = _file(v[2]) if len(v) > 2 and v[2] else None
        if f:
            dest = os.path.join(r.assets, "lista-" + os.path.basename(f))
            if not os.path.exists(dest):
                shutil.copy2(f, dest)
            v[2] = os.path.basename(dest)
        elif len(v) > 2:
            v[2] = None
    tinte = [(c.get("accento", "#E86530"), "#fff"), ("#FBF8F2", "#2A2420"), (c.get("accento_luce", "#FFB27A"), "#2A2420"),
             (c.get("banda", "#4A2412"), "#fff")]
    righe = []
    tot = min(len(voci), 30)   # ogni persona una volta sola: ripeterle la fa sembrare finta (Michael, 19/11)
    for i in range(tot):
        v = voci[i]
        nome, riga = v[:2]
        foto = v[2] if len(v) > 2 else None
        bg, fg = tinte[i % len(tinte)]
        volto = f'<img src="assets/{foto}">' if foto else E(nome[:1].upper())
        ok = f'<i class="ok" style="background:{c.get("accento", "#E86530")}">{_SPUNTA}</i>'
        righe.append(f'<div class="es-r" id="eu{n}r{i}"><i class="ic" style="background:{bg};color:{fg}">{volto}</i>'
                     f'<span class="no">{E(nome)}</span><span class="ri">{E(riga)}</span>{ok}</div>')
    alto = tot * 122
    T = r.tl.append
    velo = ".45" if alto <= 1000 else ".6"   # la marea copre tutto: il video resta dietro, più scuro
    r.corpo.append(f'<div class="es-velo" id="eu{n}v" style="background:rgba(20,14,10,{velo})"></div>')
    T(f'tl.fromTo("#eu{n}v",{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{da:.3f});'
      f'tl.to("#eu{n}v",{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    if alto <= 1000:
        # poche persone: salgono una alla volta e restano ferme al centro, poi se ne vanno
        y0 = min(max(faccia["mento"] + 40, 700), 1700 - alto)   # sul petto: la faccia resta libera
        righe = [x.replace('class="es-r"', 'class="es-r" style="opacity:0"', 1) for x in righe]
        r.corpo.append(f'<div class="es-lista" id="eu{n}" style="top:{y0:.0f}px">{"".join(righe)}</div>')
        passo = min(0.35, (a - da - 1.2) / max(tot, 1))
        for i in range(tot):
            T(f'tl.fromTo("#eu{n}r{i}",{{opacity:0,y:80}},{{opacity:1,y:0,duration:.35,ease:"power3.out",immediateRender:false}},{da + 0.15 + i * passo:.3f});')
            r.suono_libreria("hyperframes/click-soft.mp3", da + 0.15 + i * passo, 0.2)
        T(f'tl.to("#eu{n}",{{opacity:0,y:-60,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    else:
        # tante persone: una marea che riempie lo schermo e scorre veloce verso l'alto, una volta
        r.corpo.append(f'<div class="es-lista" id="eu{n}" style="top:260px;opacity:0">{"".join(righe)}</div>')
        T(f'tl.fromTo("#eu{n}",{{opacity:0,y:700}},{{opacity:1,y:0,duration:.35,ease:"power3.out",immediateRender:false}},{da:.3f});'
          f'tl.to("#eu{n}",{{y:{-(alto - 1300)},duration:{max(a - da - 0.65, 0.5):.2f},ease:"none"}},{da + 0.35:.3f});'
          f'tl.to("#eu{n}",{{opacity:0,duration:.3}},{a - 0.3:.3f});')
        for k in range(int((a - da) / 0.35)):
            r.suono_libreria("hyperframes/click-soft.mp3", da + 0.3 + k * 0.35, 0.12)
    r.suono_libreria("hyperframes/whoosh-short.mp3", da, 0.25)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- messaggio in arrivo
_CUORE = '<svg width="38" height="34" viewBox="0 0 48 44"><path d="M24 42C10 32 3 24 3 15A11 11 0 0 1 24 10A11 11 0 0 1 45 15C45 24 38 32 24 42Z" fill="COL"/></svg>'


def messaggio(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    n = len(r.corpo)
    c = r.stile["colori"]
    nome = e.get("nome", "")
    acc = c.get("accento", "#E86530")
    y = min(faccia["mento"] + 160, 1300)
    r.corpo.append(f'<div class="es-dm" id="ed{n}" style="left:70px;top:{y:.0f}px">'
                   f'<div class="chi"><span class="av" style="background:{acc}">{E(nome[:1].upper())}</span>{E(nome)}</div>'
                   f'<div class="bo" style="background:#FBF8F2;color:#231F1C">{E(e.get("testo", ""))}'
                   f'<span class="cu" id="ed{n}c">{_CUORE.replace("COL", acc)}</span></div></div>')
    T = r.tl.append
    T(f'tl.fromTo("#ed{n}",{{opacity:0,y:50,scale:.92}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.8)",immediateRender:false}},{da:.3f});'
      f'tl.to("#ed{n}",{{opacity:0,y:30,duration:.3,ease:"power2.in"}},{a - 0.3:.3f});')
    r.suono_libreria("hyperframes/notification.mp3", da, 0.3)
    cu = e.get("cuore", da + 0.9)
    if cu:
        T(f'tl.fromTo("#ed{n}c",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:.35,ease:"back.out(3)",immediateRender:false}},{cu:.3f});')
        r.suono("pop", cu, 0.3)
    r.nascondi.append((da, a))


# ---------------------------------------------------------------- apertura tipografica
def fondale(r, e, faccia):
    _css(r)
    da, a = e["da"], e["a"]
    c = r.stile["colori"]
    frasi = e.get("frasi", [])[:4]
    if not frasi:
        return
    n = len(r.camera)
    chiaro, acc, scuro = c.get("accento_luce", "#FFB27A"), c.get("accento", "#E86530"), c.get("banda", "#4A2412")
    giu = min(faccia["mento"] + 80, 1320)
    maschera = f"linear-gradient(#000 0,#000 {giu}px,transparent {giu + 260}px)"
    sel = r.ritaglio(da - 0.1, a + 0.1)
    cima = r.cima_testa(r.ultimo_ritaglio, 0.3) or _cima(faccia)
    spazio = max(cima + 50 - 190, 220)   # le parole stanno sopra la testa (al massimo sfiorano i capelli)
    testi = []
    for k, fr in enumerate(frasi):
        sopra, sotto = fr[0], fr[1] if len(fr) > 2 else ""
        d1 = max(min(200, int(960 / (max(len(sopra), 3) * 0.6))), 70)
        d2 = max(min(300, int(980 / (max(len(sotto), 3) * 0.62))), 80) if sotto else 0
        k_alto = min(1, spazio / (d1 * 0.95 + d2 * 0.95))
        d1, d2 = int(d1 * k_alto), int(d2 * k_alto)
        y1 = 190
        testi.append(f'<div class="es-fr" id="ef{n}a{k}" style="top:{y1:.0f}px;font-size:{d1}px;color:#fff">{E(sopra.upper())}</div>')
        if sotto:
            testi.append(f'<div class="es-fr" id="ef{n}b{k}" style="top:{y1 + d1 * 0.95:.0f}px;font-size:{d2}px;color:{scuro}">{E(sotto.upper())}</div>')
    r.camera.insert(0, f'<div class="es-fondo" id="ef{n}" style="background:radial-gradient(80% 55% at 50% 15%,{chiaro},{acc} 75%);'
                       f'-webkit-mask-image:{maschera};mask-image:{maschera}">{"".join(testi)}</div>')
    T = r.tl.append
    T(f'tl.set("{sel}",{{opacity:1}},{da:.3f});'
      f'tl.fromTo("#ef{n}",{{opacity:0,y:-300}},{{opacity:1,y:0,duration:.4,ease:"power3.out",immediateRender:false}},{da:.3f});'
      f'tl.to("#ef{n}",{{opacity:0,duration:.3}},{a - 0.3:.3f});tl.set("{sel}",{{opacity:0}},{a:.3f});')
    for k, fr in enumerate(frasi):
        t = max(fr[-1] if isinstance(fr[-1], (int, float)) else da + k, da + 0.15)
        fine = frasi[k + 1][-1] if k + 1 < len(frasi) else a
        T(f'tl.fromTo("#ef{n}a{k}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{t:.3f});')
        if len(fr) > 2 and fr[1]:
            T(f'tl.fromTo("#ef{n}b{k}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{t + 0.12:.3f});')
        if k + 1 < len(frasi):
            T(f'tl.to(["#ef{n}a{k}","#ef{n}b{k}"],{{opacity:0,scale:1.15,duration:.2}},{fine - 0.05:.3f});')
        r.suono("pop", t, 0.25)
    r.suono_libreria("hyperframes/whoosh-short.mp3", da, 0.3)
    r.nascondi.append((da, a))


TIPI = {"immagini": immagini, "scorri": scorri, "messaggio": messaggio, "fondale": fondale}
