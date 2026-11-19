"""Effetti nuovi del motore grafica (14/11/2026), rifatti da noi guardando i cataloghi di riferimento (mai copiati).
Tutti della stessa famiglia: scheda crema con angoli da 26 px e ombra leggera, colore del brand (var(--acc)),
testo nel font dei sottotitoli (grafica.font_degli_effetti cambia 'Inter Tight'), corsivo Instrument Serif per i titoletti,
scrittura a mano Caveat. Ognuno sta sul petto (sotto il mento) o di lato, e mentre c'è i sottotitoli si nascondono.

Nel piano (tempi del video TAGLIATO):
 {"tipo": "barra", "da", "a", "etichetta": "Posti occupati", "valore": 87, "quando": secondo in cui si riempie}
 {"tipo": "scontrino", "da", "a", "titolo": "Quanto ti costa", "righe": [["Montatore", "300 €", t], ...], "totale": ["Totale", "0 €", t]}
 {"tipo": "carrello", "da", "a", "prodotto": "Il corso", "prezzo": "97 €", "tocco": t}
 {"tipo": "sondaggio", "da", "a", "domanda": "Lo fai anche tu?", "opzioni": [["Sì", 72], ["No", 28]], "risultato": t}
 {"tipo": "voto", "da", "a", "titolo": "Quanto ti piace", "stelle": 4, "quando": t}
 {"tipo": "podio", "da", "a", "posti": [["terzo", t], ["secondo", t], ["primo", t]]}     (si dicono dal terzo al primo)
 {"tipo": "top", "da", "a", "titolo": "Top 5", "voci": [["la quinta", t], ...]}           (dalla quinta alla prima)
 {"tipo": "freccia", "da", "a", "testo": "io 3 anni fa", "lato": "sinistra" | "destra"}
 {"tipo": "postit", "da", "a", "testo": "Fatto è meglio di perfetto"}
 {"tipo": "citazione", "da", "a", "testo": "La frase", "autore": "Michael"}
"""
import html

E = html.escape


def _font(r):
    for f in ("InterTight.ttf", "Caveat.ttf", "InstrumentSerif-Italic.ttf"):
        r.font_extra(f)
    r.usa_nuovi = True


def _entra(r, sel, da, a, dy=60):
    r.tl.append(f'tl.fromTo("{sel}",{{opacity:0,y:{dy},scale:.96}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.5)",immediateRender:false}},{da:.3f});'
                f'tl.to("{sel}",{{opacity:0,y:{dy // 2},duration:.25,ease:"power2.in"}},{a - 0.25:.3f});')


def _petto(faccia):
    return min(faccia["mento"] + 50, 1180)


def barra(r, e, faccia):
    _font(r)
    n, da, a, q = len(r.corpo), e["da"], e["a"], e.get("quando", e["da"] + 0.5)
    v = max(0, min(100, int(e.get("valore", 80))))
    r.corpo.append(f'<div class="nx-card nx-barra" id="nb{n}" style="top:{_petto(faccia)}px"><div class="nx-riga"><span class="nx-et">{E(e.get("etichetta", ""))}</span>'
                   f'<b class="nx-pc" id="nb{n}p">0%</b></div><div class="nx-fondo"><i id="nb{n}b"></i></div></div>')
    _entra(r, f"#nb{n}", da, a)
    r.tl.append(f'tl.fromTo("#nb{n}b",{{scaleX:0}},{{scaleX:{v / 100:.3f},duration:1.1,ease:"power2.out",immediateRender:false}},{q:.3f});'
                f'(()=>{{const o={{v:0}};tl.to(o,{{v:{v},duration:1.1,ease:"power2.out",onUpdate:()=>{{document.querySelector("#nb{n}p").textContent=Math.round(o.v)+"%";}}}},{q:.3f});}})();')
    r.nascondi.append((da, a))
    r.suono("pop", da, 0.3)
    r.suono_libreria("hyperframes/riser.mp3", q, 0.18)


def scontrino(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    righe = "".join(f'<div class="nx-sr" id="ns{n}r{j}"><span>{E(t)}</span><b>{E(p)}</b></div>' for j, (t, p, _) in enumerate(e.get("righe", [])))
    tot = e.get("totale")
    tot_html = f'<div class="nx-st" id="ns{n}t"><span>{E(tot[0])}</span><b>{E(tot[1])}</b></div>' if tot else ""
    r.corpo.append(f'<div class="nx-card nx-scontrino" id="ns{n}" style="top:{_petto(faccia) - 40}px"><div class="nx-tit">{E(e.get("titolo", "Ricevuta"))}</div>'
                   f'{righe}<div class="nx-taglio"></div>{tot_html}</div>')
    _entra(r, f"#ns{n}", da, a, 120)
    for j, (_, _, t) in enumerate(e.get("righe", [])):
        r.tl.append(f'tl.fromTo("#ns{n}r{j}",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.25,immediateRender:false}},{t:.3f});')
        r.suono("click", t, 0.25)
    if tot:
        r.tl.append(f'tl.fromTo("#ns{n}t",{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{tot[2]:.3f});')
        r.suono_libreria("hyperframes/chime.mp3", tot[2], 0.3)
    r.nascondi.append((da, a))


def carrello(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    t = e.get("tocco", da + 1.2)
    r.corpo.append(f'<div class="nx-card nx-carrello" id="nc{n}" style="top:{_petto(faccia)}px"><div class="nx-prod">{E(e.get("prodotto", ""))}</div>'
                   f'<div class="nx-prezzo">{E(e.get("prezzo", ""))}</div><div class="nx-bot" id="nc{n}b"><span id="nc{n}s">Aggiungi al carrello</span></div>'
                   f'<i class="nx-badge" id="nc{n}n">1</i><i class="nx-dito" id="nc{n}d"></i></div>')
    _entra(r, f"#nc{n}", da, a)
    r.tl.append(f'tl.fromTo("#nc{n}d",{{opacity:0,x:60,y:60}},{{opacity:1,x:0,y:0,duration:.35,immediateRender:false}},{t - 0.4:.3f});'
                f'tl.to("#nc{n}b",{{scale:.94,duration:.08}},{t:.3f});tl.to("#nc{n}b",{{scale:1,duration:.12}},{t + 0.08:.3f});'
                f'tl.set("#nc{n}s",{{textContent:"Aggiunto ✓"}},{t + 0.05:.3f});tl.set("#nc{n}b",{{className:"nx-bot fatto"}},{t + 0.05:.3f});'
                f'tl.to("#nc{n}d",{{opacity:0,duration:.2}},{t + 0.3:.3f});'
                f'tl.fromTo("#nc{n}n",{{scale:0}},{{scale:1,duration:.3,ease:"back.out(3)",immediateRender:false}},{t + 0.1:.3f});')
    r.suono("click", t, 0.4)
    r.suono_libreria("hyperframes/chime.mp3", t + 0.1, 0.25)
    r.nascondi.append((da, a))


def sondaggio(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    t = e.get("risultato", da + 1.0)
    op = e.get("opzioni", [["Sì", 70], ["No", 30]])
    righe = "".join(f'<div class="nx-op"><i id="nq{n}o{j}"></i><span>{E(o)}</span><b id="nq{n}p{j}">{int(p)}%</b></div>' for j, (o, p) in enumerate(op))
    r.corpo.append(f'<div class="nx-card nx-sondaggio" id="nq{n}" style="top:{_petto(faccia)}px"><div class="nx-dom">{E(e.get("domanda", ""))}</div>{righe}</div>')
    _entra(r, f"#nq{n}", da, a)
    for j, (_, p) in enumerate(op):
        r.tl.append(f'tl.fromTo("#nq{n}o{j}",{{scaleX:0}},{{scaleX:{max(p, 4) / 100:.3f},duration:.8,ease:"power2.out",immediateRender:false}},{t:.3f});'
                    f'tl.fromTo("#nq{n}p{j}",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{t + 0.3:.3f});')
    r.suono("pop", da, 0.3)
    r.suono("click", t, 0.3)
    r.nascondi.append((da, a))


def voto(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    q, k = e.get("quando", da + 0.4), max(1, min(5, int(e.get("stelle", 5))))
    stelle = "".join(f'<i class="nx-stella" id="nv{n}s{j}">★</i>' for j in range(5))
    r.corpo.append(f'<div class="nx-card nx-voto" id="nv{n}" style="top:{_petto(faccia)}px"><div class="nx-tit">{E(e.get("titolo", ""))}</div>'
                   f'<div class="nx-stelle">{stelle}</div></div>')
    _entra(r, f"#nv{n}", da, a)
    for j in range(k):
        t = q + j * 0.18
        r.tl.append(f'tl.fromTo("#nv{n}s{j}",{{scale:.5}},{{scale:1,color:"var(--acc)",duration:.3,ease:"back.out(3)",immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.18)
    r.nascondi.append((da, a))


def podio(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    posti = e.get("posti", [])   # dal terzo al primo
    ordine = [(1, 2, "220px"), (0, 1, "300px"), (2, 3, "170px")]   # colonna: (indice del posto detto, numero, altezza)
    col = ""
    for c, (i, num, h) in enumerate(ordine):
        nome = posti[2 - (num - 1)][0] if len(posti) == 3 else ""
        col += (f'<div class="nx-pd"><div class="nx-pn" id="np{n}n{num}">{E(nome)}</div>'
                f'<div class="nx-gr{" uno" if num == 1 else ""}" id="np{n}g{num}" style="height:{h}">{num}</div></div>')
    r.corpo.append(f'<div class="nx-podio" id="np{n}" style="top:{_petto(faccia) - 40}px">{col}</div>')
    r.tl.append(f'tl.fromTo("#np{n}",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{da:.3f});'
                f'tl.to("#np{n}",{{opacity:0,y:40,duration:.25}},{a - 0.25:.3f});')
    for k, (_, t) in enumerate(posti[:3]):
        num = 3 - k
        r.tl.append(f'tl.fromTo("#np{n}g{num}",{{scaleY:0}},{{scaleY:1,duration:.45,ease:"back.out(1.4)",immediateRender:false}},{t:.3f});'
                    f'tl.fromTo("#np{n}n{num}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{t + 0.25:.3f});')
        r.suono("impatto" if num == 1 else "pop", t, 0.35 if num == 1 else 0.25)
    r.nascondi.append((da, a))


def top(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    voci = e.get("voci", [])
    tot = len(voci)
    righe = "".join(f'<div class="nx-tv" id="nt{n}v{j}"><b>{tot - j}</b><span>{E(t)}</span></div>' for j, (t, _) in enumerate(voci))
    r.corpo.append(f'<div class="nx-card nx-top" id="nt{n}" style="top:{max(_petto(faccia) - 60, 700)}px"><div class="nx-tit">{E(e.get("titolo", f"Top {tot}"))}</div>{righe}</div>')
    _entra(r, f"#nt{n}", da, a)
    for j, (_, t) in enumerate(voci):
        r.tl.append(f'tl.set("#nt{n}v{j}",{{className:"nx-tv acceso"}},{t:.3f});'
                    f'tl.fromTo("#nt{n}v{j}",{{x:-14}},{{x:0,duration:.25,immediateRender:false}},{t:.3f});')
        r.suono("pop", t, 0.22)
    r.nascondi.append((da, a))


def freccia(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    destra = e.get("lato") == "destra"
    y = max(faccia["occhi"] - 260, 300)
    x = 600 if destra else 70
    path = ("M60 30 C 30 90, 40 160, 150 190" if not destra else "M200 30 C 230 90, 220 160, 110 190")
    punta = ("M150 190 l-34 -2 M150 190 l-14 -30" if not destra else "M110 190 l34 -2 M110 190 l14 -30")
    r.corpo.append(f'<div class="nx-freccia" id="nf{n}" style="left:{x}px;top:{y}px"><div class="nx-mano">{E(e.get("testo", ""))}</div>'
                   f'<svg viewBox="0 0 260 220" width="260" height="220"><path id="nf{n}l" d="{path}"/><path id="nf{n}p" d="{punta}"/></svg></div>')
    r.tl.append(f'tl.fromTo("#nf{n}",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{da:.3f});'
                f'tl.fromTo("#nf{n}l",{{strokeDashoffset:420}},{{strokeDashoffset:0,duration:.6,ease:"power2.out",immediateRender:false}},{da + 0.15:.3f});'
                f'tl.fromTo("#nf{n}p",{{strokeDashoffset:120}},{{strokeDashoffset:0,duration:.2,immediateRender:false}},{da + 0.7:.3f});'
                f'tl.to("#nf{n}",{{opacity:0,duration:.25}},{a - 0.25:.3f});')
    r.suono("click", da + 0.15, 0.2)


def postit(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    r.corpo.append(f'<div class="nx-postit" id="nz{n}" style="top:250px"><span id="nz{n}t"></span></div>')   # sopra la testa, a destra
    testo = e.get("testo", "")
    r.tl.append(f'tl.fromTo("#nz{n}",{{opacity:0,scale:.6,rotate:-14}},{{opacity:1,scale:1,rotate:-5,duration:.4,ease:"back.out(2)",immediateRender:false}},{da:.3f});'
                f'(()=>{{const t={testo!r};const o={{p:0}};tl.to(o,{{p:1,duration:{min(1.2, len(testo) * 0.05):.2f},ease:"none",onUpdate:()=>{{document.querySelector("#nz{n}t").textContent=t.slice(0,Math.round(o.p*t.length));}}}},{da + 0.3:.3f});}})();'
                f'tl.to("#nz{n}",{{opacity:0,rotate:4,duration:.25}},{a - 0.25:.3f});')
    r.suono("pop", da, 0.3)
    r.suono("tastiera", da + 0.3, 0.15)


def citazione(r, e, faccia):
    _font(r)
    n, da, a = len(r.corpo), e["da"], e["a"]
    r.corpo.append(f'<div class="nx-card nx-citazione" id="nk{n}" style="top:{_petto(faccia) - 20}px"><i class="nx-virg">“</i>'
                   f'<div class="nx-frase">{E(e.get("testo", ""))}</div>'
                   + (f'<div class="nx-autore">— {E(e["autore"])}</div>' if e.get("autore") else "") + '</div>')
    _entra(r, f"#nk{n}", da, a)
    r.suono("pop", da, 0.25)
    r.nascondi.append((da, a))


TIPI = {"barra": barra, "scontrino": scontrino, "carrello": carrello, "sondaggio": sondaggio, "voto": voto, "podio": podio,
        "top": top, "freccia": freccia, "postit": postit, "citazione": citazione}

CSS = """
@font-face{font-family:'Inter Tight';src:url('assets/InterTight.ttf');font-weight:100 900}
@font-face{font-family:'Caveat';src:url('assets/Caveat.ttf');font-weight:400 700}
@font-face{font-family:'Instrument Serif Italic';src:url('assets/InstrumentSerif-Italic.ttf')}
.nx-card{position:absolute;left:150px;right:190px;background:#F7F1E6;color:#1C1A17;border-radius:26px;padding:30px 34px;
 box-shadow:0 18px 50px rgba(0,0,0,.35);font-family:'Inter Tight';opacity:0;z-index:40}
.nx-tit{font-family:'Instrument Serif Italic';font-size:46px;line-height:1;margin-bottom:18px;color:#3a2a20}
.nx-riga{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:16px}
.nx-et{font-weight:700;font-size:36px}
.nx-pc{font-weight:900;font-size:64px;color:var(--acc)}
.nx-fondo{height:28px;border-radius:14px;background:rgba(28,26,23,.12);overflow:hidden}
.nx-fondo i{display:block;height:100%;background:var(--acc);border-radius:14px;transform-origin:0 50%;transform:scaleX(0)}
.nx-scontrino{left:210px;right:250px;border-radius:10px 10px 26px 26px;font-family:'Inter Tight'}
.nx-sr,.nx-st{display:flex;justify-content:space-between;font-size:34px;padding:8px 0;opacity:0}
.nx-sr span{color:#4a3d33}.nx-sr b{font-weight:800}
.nx-taglio{border-top:4px dashed rgba(28,26,23,.3);margin:14px 0 8px}
.nx-st{font-weight:900;font-size:46px}.nx-st b{color:var(--acc)}
.nx-prod{font-weight:800;font-size:44px}
.nx-prezzo{font-weight:900;font-size:70px;color:var(--acc);margin:4px 0 22px}
.nx-bot{height:96px;border-radius:48px;background:#1C1A17;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:34px}
.nx-bot.fatto{background:var(--acc)}
.nx-badge{position:absolute;top:-18px;right:-18px;width:60px;height:60px;border-radius:50%;background:var(--acc);color:#fff;font-style:normal;
 font-weight:900;font-size:32px;display:flex;align-items:center;justify-content:center;transform:scale(0);box-shadow:0 6px 16px rgba(0,0,0,.3)}
.nx-dito{position:absolute;right:80px;bottom:-30px;width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.85);
 box-shadow:0 0 0 6px rgba(255,255,255,.35);opacity:0}
.nx-dom{font-weight:800;font-size:42px;text-align:center;margin-bottom:22px}
.nx-op{position:relative;height:84px;border-radius:42px;background:rgba(28,26,23,.08);margin-top:14px;overflow:hidden;display:flex;align-items:center;padding:0 30px}
.nx-op i{position:absolute;inset:0;background:var(--acc);opacity:.85;transform-origin:0 50%;transform:scaleX(0)}
.nx-op span,.nx-op b{position:relative;font-weight:800;font-size:34px}
.nx-op b{margin-left:auto;opacity:0}
.nx-voto{text-align:center}
.nx-stelle{display:flex;justify-content:center;gap:10px}
.nx-stella{font-style:normal;font-size:96px;line-height:1;color:rgba(28,26,23,.18)}
.nx-podio{position:absolute;left:150px;right:190px;display:flex;align-items:flex-end;justify-content:center;gap:16px;opacity:0;z-index:40}
.nx-pd{display:flex;flex-direction:column;align-items:center;width:210px}
.nx-pn{font-family:'Inter Tight';font-weight:800;font-size:34px;color:#fff;text-align:center;text-shadow:0 3px 10px rgba(0,0,0,.6);margin-bottom:10px;opacity:0}
.nx-gr{width:100%;border-radius:18px 18px 0 0;background:#F7F1E6;color:#1C1A17;font-family:'Inter Tight';font-weight:900;font-size:90px;
 display:flex;justify-content:center;padding-top:14px;transform-origin:50% 100%;transform:scaleY(0);box-shadow:0 18px 40px rgba(0,0,0,.35)}
.nx-gr.uno{background:var(--acc);color:#fff}
.nx-top{left:170px;right:170px;padding:28px 36px}
.nx-tv{display:flex;align-items:center;gap:22px;padding:10px 0;font-size:44px;font-weight:800;color:rgba(28,26,23,.3)}
.nx-tv b{width:76px;height:76px;flex:none;border-radius:18px;font-size:40px;background:rgba(28,26,23,.1);display:flex;align-items:center;justify-content:center;font-weight:900}
.nx-tv.acceso{color:#1C1A17}.nx-tv.acceso b{background:var(--acc);color:#fff}
.nx-freccia{position:absolute;width:420px;opacity:0;z-index:40}
.nx-mano{font-family:'Caveat';font-weight:700;font-size:66px;color:#fff;text-shadow:0 3px 12px rgba(0,0,0,.55);line-height:1}
.nx-freccia svg path{fill:none;stroke:#fff;stroke-width:8;stroke-linecap:round;stroke-dasharray:420;filter:drop-shadow(0 3px 6px rgba(0,0,0,.5))}
.nx-postit{position:absolute;right:120px;width:320px;min-height:250px;background:#FFE58A;background:color-mix(in srgb,var(--acc) 22%,#FFF3B0);
 padding:30px 28px;box-shadow:0 20px 40px rgba(0,0,0,.35);font-family:'Caveat';font-weight:700;font-size:52px;line-height:1.05;color:#2a2318;opacity:0;z-index:40}
.nx-citazione{padding:44px 40px 34px}
.nx-virg{position:absolute;top:-30px;left:26px;font-style:normal;font-family:'Instrument Serif Italic';font-size:180px;line-height:1;color:var(--acc)}
.nx-frase{font-family:'Instrument Serif Italic';font-size:58px;line-height:1.08;color:#1C1A17}
.nx-autore{margin-top:16px;font-weight:700;font-size:28px;color:#6b5a4c;letter-spacing:.04em}
"""
