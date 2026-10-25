"""Impaginazione "Split": la persona nella metà bassa, le grafiche nella metà alta (sopra la testa).

Nel piano.json:  "layout": "split",
                 "pannelli": [
  {"tipo": "notifiche", "da": 0.5, "a": 6.3, "voci": [["Pubblicato", "07:02", 0.6], ...], "sotto": "0 contatti"},
  {"tipo": "percorso", "da": 10.0, "a": 17.5, "passi": [["ChatGPT", 10.2], ["15 domande", 13.0], ["15 contenuti", 15.5]]},
  {"tipo": "contatore", "da": 17.6, "a": 21.0, "da_valore": 0, "a_valore": 15, "etichetta": "contenuti pronti"},
  {"tipo": "testo", "da": 6.9, "a": 9.9, "sopra": "c'è un modo", "grande": "PIÙ SEMPLICE"}]
I pannelli stanno tra y 230 e y 960; la persona viene spostata in basso di SPOSTA pixel.
"""
import html

SPOSTA = 380          # quanto scende il video della persona
ALTO, BASSO = 230, 960  # area delle grafiche

CSS = """
#split-fondo{position:absolute;left:0;right:0;top:0;height:950px;z-index:1;
 background:linear-gradient(#140E0A 0%,#140E0A 55%,rgba(20,14,10,0) 100%)}
.pan{position:absolute;left:90px;right:90px;top:150px;height:560px;z-index:15;opacity:0;display:flex;
 flex-direction:column;align-items:center;justify-content:center;gap:18px}
.card{width:100%;display:flex;align-items:center;gap:22px;padding:26px 30px;border-radius:26px;
 background:rgba(249,247,244,.06);border:2px solid rgba(249,247,244,.14);font-family:'Plus Jakarta Sans';
 font-weight:700;font-size:40px;color:#F9F7F4;box-shadow:0 18px 40px rgba(0,0,0,.35)}
.card .ok{width:46px;height:46px;border-radius:23px;display:flex;align-items:center;justify-content:center;font-size:30px;color:#140E0A}
.card .ora{margin-left:auto;font-size:34px;opacity:.7}
.nodo{padding:26px 34px;border-radius:24px;border:3px solid rgba(249,247,244,.25);font-family:'Plus Jakarta Sans';
 font-weight:800;font-size:42px;color:rgba(249,247,244,.45);background:rgba(249,247,244,.04)}
.freccia-p{font-size:46px;color:rgba(249,247,244,.3);font-family:'Plus Jakarta Sans';font-weight:800}
.numero-c{font-family:'Plus Jakarta Sans';font-weight:800;font-size:210px;line-height:1;color:#F9F7F4;letter-spacing:-6px}
.barre{display:flex;align-items:flex-end;gap:16px;height:170px}
.barra{width:52px;border-radius:10px 10px 4px 4px;height:0}
.pieno{position:absolute;inset:0;z-index:25;opacity:0;overflow:hidden}
.pan-pieno{top:420px;height:900px;opacity:1}
.pieno.chiaro .cors{color:#1C1A18;text-shadow:none}
.pieno.chiaro .grande{text-shadow:none}
.pavimento{position:absolute;left:-50%;right:-50%;bottom:-200px;height:900px;transform:perspective(600px) rotateX(62deg);
 background-image:linear-gradient(rgba(0,0,0,.08) 2px,transparent 2px),linear-gradient(90deg,rgba(0,0,0,.08) 2px,transparent 2px);
 background-size:120px 120px}
.timbro{position:absolute;right:30px;top:-30px;padding:14px 30px;border:7px solid;border-radius:16px;
 font-family:'Plus Jakarta Sans';font-weight:800;font-size:62px;letter-spacing:2px;background:rgba(20,14,10,.55)}
"""


def pannello(p, n, colori, parole=(), chiave=()):
    acc, luce = colori["accento"], colori["accento_luce"]
    da, a = p["da"], p["a"]
    tl = [f'tl.fromTo("#pa{n}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.35,ease:"power3.out"}},{da:.3f});',
          f'tl.to("#pa{n}",{{opacity:0,y:-30,duration:0.25}},{a - 0.25:.3f});']
    if p["tipo"] == "notifiche":
        righe = ""
        for i, (titolo, ora, t) in enumerate(p["voci"]):
            righe += (f'<div class="card" id="pa{n}c{i}" style="opacity:0"><div class="ok" style="background:{acc}">✓</div>'
                      f'{html.escape(titolo)}<div class="ora">{html.escape(ora)}</div></div>')
            tl.append(f'tl.fromTo("#pa{n}c{i}",{{opacity:0,y:-40,scale:0.9}},{{opacity:1,y:0,scale:1,duration:0.35,ease:"back.out(1.6)"}},{t:.3f});')
        if p.get("sotto"):
            righe += (f'<div class="grande" id="pa{n}s" style="opacity:0;font-size:96px;color:{acc}">{html.escape(p["sotto"])}</div>')
            tl.append(f'tl.fromTo("#pa{n}s",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:0.3,ease:"power3.out"}},{p["sotto_da"]:.3f});')
        corpo = righe
    elif p["tipo"] == "percorso":
        corpo = ""
        for i, (testo, t) in enumerate(p["passi"]):
            if i:
                corpo += f'<div class="freccia-p" id="pa{n}f{i}">↓</div>'
                tl.append(f'tl.to("#pa{n}f{i}",{{color:"{luce}",duration:0.2}},{t - 0.2:.3f});')
            corpo += f'<div class="nodo" id="pa{n}n{i}">{html.escape(testo)}</div>'
            tl.append(f'tl.to("#pa{n}n{i}",{{color:"#F9F7F4",borderColor:"{acc}",backgroundColor:"rgba(232,101,48,.16)",'
                      f'boxShadow:"0 0 34px rgba(232,101,48,.55)",scale:1.06,duration:0.25,ease:"back.out(2)"}},{t:.3f});'
                      f'tl.to("#pa{n}n{i}",{{scale:1,duration:0.2}},{t + 0.25:.3f});')
    elif p["tipo"] == "contatore":
        dur = min(1.8, a - da - 0.5)
        corpo = (f'<div class="numero-c" id="pa{n}v">{p.get("da_valore", 0)}</div>'
                 f'<div class="cors" style="font-size:60px;color:{luce}">{html.escape(p.get("etichetta", ""))}</div>'
                 f'<div class="barre">' + "".join(f'<div class="barra" id="pa{n}b{i}" style="background:linear-gradient({luce},{acc})"></div>'
                                                for i in range(7)) + '</div>')
        tl.append(f'(function(){{const o={{v:{p.get("da_valore", 0)}}};tl.to(o,{{v:{p["a_valore"]},duration:{dur:.2f},ease:"power2.out",'
                  f'onUpdate:()=>{{document.getElementById("pa{n}v").textContent=Math.round(o.v).toLocaleString("it-IT")}}}},{da + 0.2:.3f});}})();')
        tl += [f'tl.to("#pa{n}b{i}",{{height:{30 + i * 22},duration:0.4,ease:"back.out(1.5)"}},{da + 0.25 + i * 0.12:.3f});' for i in range(7)]
    else:  # testo
        corpo = ((f'<div class="cors" style="font-size:72px">{html.escape(p["sopra"])}</div>' if p.get("sopra") else "")
                 + f'<div class="grande" style="font-size:120px;color:{acc}">{html.escape(p["grande"])}</div>')
    # la frase detta, parola per parola sotto la grafica, con le parole chiave colorate
    if p.get("frase"):
        pezzi = []
        for k, w in enumerate(x for x in parole if p["da"] - 0.4 <= x["da"] < p["a"]):
            pulita = w["testo"].strip(".,;:!?").lower()
            col = f"color:{acc}" if pulita in chiave else ""
            pezzi.append(f'<span id="pa{n}w{k}" style="opacity:.0;{col}">{html.escape(w["testo"])} </span>')
            tl.append(f'tl.to("#pa{n}w{k}",{{opacity:1,duration:0.08}},{w["da"]:.3f});')
        corpo += (f'<div class="frase" style="font-family:\'Plus Jakarta Sans\';font-weight:700;font-size:46px;line-height:1.25;'
                  f'text-align:center;color:{"#1C1A18" if p.get("pieno") == "chiaro" else "#F9F7F4"};text-wrap:balance">{"".join(pezzi)}</div>')
    # il timbro che "sbatte" sopra la grafica
    if p.get("timbro"):
        corpo += (f'<div class="timbro" id="pa{n}t" style="opacity:0;border-color:{acc};color:{acc}">{html.escape(p["timbro"])}</div>')
        tl.append(f'tl.fromTo("#pa{n}t",{{opacity:0,scale:2.2,rotation:-14}},{{opacity:1,scale:1,rotation:-8,duration:0.18,ease:"power4.in"}},{p["timbro_da"]:.3f});')
    if p.get("pieno"):
        # scena a tutto schermo: la persona sparisce con un taglio netto, poi si torna allo split
        chiaro = p["pieno"] == "chiaro"
        tl[0] = f'tl.set("#pp{n}",{{opacity:1}},{p["da"]:.3f});tl.fromTo("#pa{n}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{p["da"]:.3f});'
        tl[1] = f'tl.set("#pp{n}",{{opacity:0}},{p["a"]:.3f});'
        fondo = ("radial-gradient(ellipse at 50% 35%,#FFFFFF 0%,#E9E6E2 60%,#D8D3CD 100%)" if chiaro
                 else "radial-gradient(ellipse at 50% 40%,#2A1A12 0%,#140E0A 60%,#080605 100%)")
        pavimento = ('<div class="pavimento"></div>' if chiaro else "")
        return (f'<div class="pieno{" chiaro" if chiaro else ""}" id="pp{n}" style="background:{fondo}">{pavimento}'
                f'<div class="pan pan-pieno" id="pa{n}" style="color:{"#1C1A18" if chiaro else "#F9F7F4"}">{corpo}</div></div>', "".join(tl))
    return f'<div class="pan" id="pa{n}">{corpo}</div>', "".join(tl)
