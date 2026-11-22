"""VSL orizzontale, passo finale: grafiche sopra il video, sottotitoli in basso, volume per il web. Un render solo.

Uso:  PY strumenti/vsl_monta.py <nome-lavoro> --anteprima [--tempi 12.5,40,61.2]
          crea le grafiche e un foglio di fotogrammi (controllo/foglio-vsl.jpg) presi dal montaggio VERO,
          senza creare il video: si guarda il foglio, si corregge vsl.json, si riprova (secondi, non minuti)
      PY strumenti/vsl_monta.py <nome-lavoro>
          crea il video finito: finale/<nome>-vN.mp4 (ogni versione resta)

Legge dal lavoro: tagliato.mp4, parole.json, faccia.json (da vsl_taglia.py) e vsl.json (lo scrive Claude):
  {"grafiche": [...vedi vsl_grafica.py...], "sottotitoli": true}

Come si monta (pensato per 10-15 minuti): il video tagliato passa una volta sola dentro ffmpeg; le grafiche sono
piccoli video trasparenti appoggiati solo nei loro secondi; nelle grafiche a schermo pieno la persona va nel riquadro
piccolo; i sottotitoli li disegna ffmpeg (libass), parola per parola, e spariscono sotto le grafiche a schermo pieno.
Audio: voce, musica bassa sotto per tutta la VSL ("musica" in vsl.json, false = niente; "musica_sotto": dB sotto la
voce) e i suoni dei passaggi decisi da ogni grafica (whoosh su clip, lampi e chiusura, pop sui numeri;
"suono": false nella grafica li toglie, "suono": "file.wav" li cambia).
Volume: -14 LUFS, picchi sotto -2 dB (come i reel: va bene per YouTube, Facebook e le pagine web).
"""
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, FFMPEG, STUDIO, cartella_lavoro, codec_video, durata, esegui, leggi, scrivi  # noqa: E402
import vsl_grafica as vg  # noqa: E402

OBIETTIVO_LUFS, PICCO_DB = -14.0, -2.0
ACCENTO = "#E86530"


def accento():
    try:
        c = leggi(os.path.join(DATI, "profilo.json")).get("colore") or ACCENTO
    except (OSError, ValueError):
        c = ACCENTO
    return c if re.fullmatch(r"#[0-9A-Fa-f]{6}", c) else ACCENTO


# ------------------------------------------------------------------ sottotitoli
def _tempo_ass(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _colore_ass(hexa):
    r, g, b = vg.rgb(hexa)
    return f"&H00{b:02X}{g:02X}{r:02X}"


def gruppi(parole, max_car=30, max_parole=6):
    """Le parole in pezzi brevi da una riga: si va a capo dopo la punteggiatura, dopo una pausa o quando è lunga."""
    out, cur = [], []
    for i, w in enumerate(parole):
        if cur and (len(" ".join(x["testo"] for x in cur + [w])) > max_car or len(cur) >= max_parole
                    or w["da"] - cur[-1]["a"] > 0.4):
            out.append(cur)
            cur = []
        cur.append(w)
        if w["testo"].endswith((".", "?", "!", ",", ":")) and len(cur) >= 2:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def sottotitoli(parole, coperti, acc, dest, barre=()):
    """File .ass: una riga in basso, la parola detta in quel momento nel colore del brand."""
    luce = "#%02X%02X%02X" % vg.luce(vg.rgb(acc))   # schiarito: sul video si legge meglio
    libere = [w for w in parole if not any(da - 0.1 < (w["da"] + w["a"]) / 2 < a + 0.1 for da, a in coperti)]
    righe, tutti = [], gruppi(libere)
    for n, g in enumerate(tutti):
        for i, w in enumerate(g):
            # l'ultima parola resta un attimo, ma mai sopra la riga dopo (due righe insieme si accavallano)
            dopo = tutti[n + 1][0]["da"] if n + 1 < len(tutti) else 1e9
            fine = g[i + 1]["da"] if i + 1 < len(g) else min(w["a"] + 0.25, dopo)
            testo = " ".join((f"{{\\c{_colore_ass(luce)}&}}{x['testo']}{{\\c&H00FFFFFF&}}" if j == i else x["testo"])
                             for j, x in enumerate(g))
            su = any(da - 0.5 < w["da"] < a + 0.5 for da, a in barre)   # con la barra dei passaggi: più su
            righe.append(f"Dialogue: 0,{_tempo_ass(w['da'])},{_tempo_ass(fine)},Sotto,,0,0,{150 if su else 0},,{testo}")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
                "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Sotto,Poppins,76,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,"
                "120,120,70,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        f.write("\n".join(righe) + "\n")


# ------------------------------------------------------------------ grafiche
def prepara_grafiche(cart, piano, acc):
    """Crea (o riusa, se non sono cambiate) le grafiche come video trasparenti in grafiche/."""
    cart_g = os.path.join(cart, "grafiche")
    os.makedirs(cart_g, exist_ok=True)
    out = []
    for g in sorted(piano.get("grafiche", []), key=lambda g: g["da"]):
        chiave = hashlib.md5((json.dumps(g, sort_keys=True) + acc + str(os.path.getmtime(vg.__file__))).encode()).hexdigest()[:10]
        dest = os.path.join(cart_g, f"{g['tipo']}-{chiave}.mov")
        disegno = vg.grafica(g, acc) if os.path.exists(dest) else vg.crea(g, acc, dest)
        x = {"g": g, "file": dest, "buco": disegno.buco, "copre": disegno.copre, "area": disegno.area,
             "suoni": [] if g.get("suono") is False else
                      [(t, g["suono"] if isinstance(g.get("suono"), str) else f) for t, f in disegno.suoni(g)]}
        if g["tipo"] == "clip":
            x["clip"] = g["file"] if os.path.isabs(g["file"]) else os.path.join(DATI, "clip", g["file"])
            if not os.path.exists(x["clip"]):
                sys.exit(f"Non trovo la clip {x['clip']}: scaricala con clip.py --orizzontale")
            if disegno.buco:
                x["maschera"] = os.path.join(cart_g, "maschera-%dx%d.png" % disegno.buco[2:])
                disegno.maschera(x["maschera"])
        out.append(x)
    return out


def taglio_persona(faccia, w, h):
    """Dove prendere la persona per il riquadro piccolo: la faccia in alto, spalle sotto, proporzioni del riquadro."""
    alto = min(1080, max(540, faccia["h"] * (3.4 if w <= h else 4.2)))
    largo = alto * w / h
    if largo > 1920:   # riquadro largo (la chiusura): si prende quasi tutta l'inquadratura
        largo, alto = 1920, 1920 * h / w
    x = min(max(faccia["x"] - largo / 2, 0), 1920 - largo)
    y = min(max(faccia["y"] - alto * 0.36, 0), 1080 - alto)
    return f"crop={largo:.0f}:{alto:.0f}:{x:.0f}:{y:.0f},scale={w}:{h}:flags=lanczos,setsar=1"


def grafo(grafiche, faccia, subs):
    """Il montaggio come filtro ffmpeg. Ingresso 0 = video tagliato; poi per ogni grafica il suo video trasparente
    e, per le clip, la clip e la maschera degli angoli della persona. Ritorna (ingressi, filtro).
    Ordine dei livelli: video, clip, persona nel riquadro, grafica (cornice o schermo pieno con il buco), sottotitoli."""
    ingressi = []

    def entra(*args):
        ingressi.extend(args)
        return ingressi.count("-i")   # l'ingresso 0 è il video tagliato

    con_buco = [x for x in grafiche if x["buco"]]
    filtri = [f"[0:v]split={1 + len(con_buco)}[c0]" + "".join(f"[p{j}]" for j in range(len(con_buco)))]
    cur, n, j = "c0", 0, 0

    def sopra(etichetta, x=0, y=0):
        nonlocal cur, n
        n += 1
        filtri.append(f"[{cur}][{etichetta}]overlay={x}:{y}:eof_action=pass[c{n}]")
        cur = f"c{n}"

    for i, x in enumerate(grafiche):
        g = x["g"]
        dur = g["a"] - g["da"]
        if "clip" in x:
            k = entra("-ss", f"{g.get('inizio', 0):.3f}", "-t", f"{dur:.3f}", "-i", x["clip"])
            filtri.append(f"[{k}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,"
                          f"setsar=1,setpts=PTS-STARTPTS+{g['da']:.3f}/TB[cl{i}]")
            sopra(f"cl{i}")
        if x["buco"]:
            bx, by, bw, bh = x["buco"]
            if "clip" in x:   # sopra la clip la persona c'è per tutta la durata, con gli angoli arrotondati
                da, a = g["da"], g["a"]
                m = entra("-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", x["maschera"])
                filtri.append(f"[p{j}]trim=start={da:.3f}:end={a:.3f},{taglio_persona(faccia, bw, bh)},format=yuva420p[pq{j}]")
                filtri.append(f"[{m}:v]format=gray,setpts=PTS-STARTPTS+{da:.3f}/TB[mk{j}]")
                filtri.append(f"[pq{j}][mk{j}]alphamerge[pp{j}]")
            else:             # nella grafica a schermo pieno il buco si apre dopo l'entrata
                filtri.append(f"[p{j}]trim=start={g['da'] + vg.ENTRA - 0.04:.3f}:end={g['a'] - vg.ESCE + 0.04:.3f},"
                              f"{taglio_persona(faccia, bw, bh)}[pp{j}]")
            sopra(f"pp{j}", bx, by)
            j += 1
        k = entra("-i", x["file"])
        filtri.append(f"[{k}:v]setpts=PTS+{g['da']:.3f}/TB[g{i}]")
        sopra(f"g{i}", x["area"][0], x["area"][1])
    fonts = os.path.join(STUDIO, "font").replace("\\", "/").replace(":", "\\:")
    if subs:
        s = subs.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        filtri.append(f"[{cur}]subtitles=filename='{s}':fontsdir='{fonts}',format=yuv420p[v]")
    else:
        filtri.append(f"[{cur}]format=yuv420p[v]")
    return ingressi, ";".join(filtri)


def finale_codec():
    """Come i reel, ma 8 Mbit/s: una VSL di 15 minuti resta sotto 1 GB e si carica bene sul web, nitida in 1080p."""
    c = codec_video()
    return [("8M" if x == "16M" else "20" if x == "18" else x) for x in c]


def lufs(src):
    import subprocess
    err = subprocess.run([FFMPEG, "-i", src, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def foglio(fotogrammi, didascalie, dest, colonne=3):
    from PIL import Image, ImageDraw, ImageFont
    w, h = 640, 360
    righe = (len(fotogrammi) + colonne - 1) // colonne
    out = Image.new("RGB", (colonne * w, righe * (h + 34)), (24, 24, 24))
    f = ImageFont.truetype(os.path.join(STUDIO, "font", "Poppins-SemiBold.ttf"), 20)
    for k, (p, testo) in enumerate(zip(fotogrammi, didascalie)):
        x, y = k % colonne * w, k // colonne * (h + 34)
        out.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y))
        ImageDraw.Draw(out).text((x + 8, y + h + 5), testo, font=f, fill=(230, 230, 230))
    out.save(dest, quality=88)


# ------------------------------------------------------------------ audio
MUSICA_SOTTO = 22   # dB sotto la voce (misurate tutte e due): si sente appena, non disturba per 15 minuti


def massimo(src):
    import subprocess
    err = subprocess.run([FFMPEG, "-i", src, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"max_volume:\s+(-?[\d.]+) dB", err)[-1])


def brano(piano):
    """La musica sotto la VSL: "musica" in vsl.json (un file di DATI/musica o un percorso), false = niente.
    Se manca: rilassante-natura.mp3 della libreria dello studio, se no il primo brano di DATI/musica, se no la base del kit."""
    scelta = piano.get("musica", True)
    if scelta is False:
        return None
    candidati = []
    if isinstance(scelta, str):
        candidati += [scelta, os.path.join(DATI, "musica", scelta)]
    cart = os.path.join(DATI, "musica")
    candidati.append(os.path.join(cart, "rilassante-natura.mp3"))
    if os.path.isdir(cart):
        candidati += [os.path.join(cart, f) for f in sorted(os.listdir(cart)) if f.lower().endswith((".mp3", ".wav", ".m4a"))]
    candidati.append(os.path.join(STUDIO, "suoni", "kit", "musica-base.wav"))
    return next((c for c in candidati if os.path.isfile(c)), None)


def audio(cart, video, piano, grafiche, dur):
    """Voce + musica bassa per tutta la VSL + un suono quando compare ogni numero. Scrive mix.wav (il volume finale
    lo fa il render). Ritorna il percorso e cosa c'è dentro."""
    voce = lufs(video)
    ingressi, filtri, nomi, detto = ["-i", video], ["[0:a]aresample=48000,aformat=channel_layouts=stereo[a0]"], ["[a0]"], []
    musica = brano(piano)
    if musica:
        vol = voce - piano.get("musica_sotto", MUSICA_SOTTO) - lufs(musica)
        ingressi += ["-stream_loop", "-1", "-i", musica]
        filtri.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,"
                      f"volume={vol:.2f}dB,afade=t=in:d=1.5,afade=t=out:st={max(dur - 2.5, 0):.3f}:d=2.5[m]")
        nomi.append("[m]")
        detto.append(f"musica {os.path.basename(musica)} ({piano.get('musica_sotto', MUSICA_SOTTO)} dB sotto la voce)")
    # i suoni dei passaggi: li dà ogni grafica (whoosh sulle clip e sui lampi, pop sui numeri...)
    colpi = sorted((t, f if os.path.isabs(f) else os.path.join(STUDIO, "suoni", "kit", f))
                   for x in grafiche for t, f in x["suoni"])
    picchi = {}
    for t, f in colpi:
        if not os.path.exists(f):
            continue
        if f not in picchi:
            picchi[f] = massimo(f)
        # il picco sta poco sopra il volume medio della voce; i whoosh un po' più bassi (sono lunghi)
        vol = voce + (7 if "whoosh" in f or "swoosh" in f else 12) - picchi[f]
        k = ingressi.count("-i")
        ingressi += ["-i", f]
        ms = int(max(t, 0) * 1000)
        filtri.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol:.2f}dB,adelay={ms}|{ms}[s{k}]")
        nomi.append(f"[s{k}]")
    if colpi:
        detto.append(f"{len(colpi)} suoni sui passaggi")
    dest = os.path.join(cart, "mix.wav")
    filtri.append("".join(nomi) + f"amix=inputs={len(nomi)}:normalize=0:duration=first[a]")
    esegui([FFMPEG, "-v", "error", "-y", *ingressi, "-filter_complex", ";".join(filtri), "-map", "[a]",
            "-c:a", "pcm_s16le", "-ar", "48000", dest])
    return dest, detto


def tempi_di_controllo(grafiche, dur):
    """Per ogni grafica: entrata, a metà, ogni voce appena comparsa, fine. Più due momenti senza grafiche."""
    tempi = []
    for x in grafiche:
        g = x["g"]
        tempi += [(g["da"] + 0.15, "entra"), (g["da"] + 0.6, "dentro")]
        for k, (t, i) in enumerate(g.get("attivo", [])):
            if t > g["da"] + 1:
                tempi.append((t + 0.6, f"barra: passo {i + 1}"))
        for k, (v, t) in enumerate(g.get("voci", [])):
            if t > g["da"]:   # le voci già comparse prima (stessa lista che torna) non servono
                tempi.append((t + 0.5, f"voce {k + 1}"))
        tempi.append((g["a"] - 0.5, "prima di uscire"))
    liberi = [t for t in (dur * 0.2, dur * 0.55) if not any(x["g"]["da"] - 1 < t < x["g"]["a"] + 1 for x in grafiche)]
    tempi += [(t, "senza grafiche") for t in liberi]
    return sorted((max(t, 0.05), c) for t, c in tempi)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = sys.argv[1]
    cart = cartella_lavoro(nome)
    video = os.path.join(cart, "tagliato.mp4")
    piano = leggi(os.path.join(cart, "vsl.json")) if os.path.exists(os.path.join(cart, "vsl.json")) else {}
    faccia = leggi(os.path.join(cart, "faccia.json"))
    acc = accento()
    dur = durata(video)
    for g in piano.get("grafiche", []):
        if not 0 <= g["da"] < g["a"] <= dur + 0.01:
            sys.exit(f"Grafica fuori dal video: {g}")

    print("Preparo le grafiche...")
    grafiche = prepara_grafiche(cart, piano, acc)
    subs = None
    if piano.get("sottotitoli", True):
        subs = os.path.join(cart, "sottotitoli.ass")
        sottotitoli(leggi(os.path.join(cart, "parole.json")),
                    [(x["g"]["da"], x["g"]["a"]) for x in grafiche if x["copre"]], acc, subs,
                    [(x["g"]["da"], x["g"]["a"]) for x in grafiche if x["g"]["tipo"] == "barra"])

    if "--anteprima" in sys.argv:
        ctrl = os.path.join(cart, "controllo")
        os.makedirs(ctrl, exist_ok=True)
        if "--tempi" in sys.argv:
            tempi = [(float(t), "") for t in sys.argv[sys.argv.index("--tempi") + 1].split(",")]
        else:
            tempi = tempi_di_controllo(grafiche, dur)
        file, didascalie = [], []
        for k, (t, cosa) in enumerate(tempi):
            attive = [x for x in grafiche if x["g"]["da"] <= t < x["g"]["a"]]
            dest = os.path.join(ctrl, f"vsl-{k:02d}.jpg")
            ingressi, filtro = grafo(attive, faccia, subs)
            # -copyts: il fotogramma tiene il suo tempo vero, così grafiche e sottotitoli sono quelli del montaggio
            esegui([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-copyts", "-i", video, *ingressi,
                    "-filter_complex", filtro, "-map", "[v]", "-frames:v", "1", "-q:v", "3", dest])
            file.append(dest)
            didascalie.append(f"{int(t // 60)}:{t % 60:05.2f}  {cosa}")
        foglio(file, didascalie, os.path.join(ctrl, "foglio-vsl.jpg"))
        for p in file:
            os.remove(p)
        print(f"Foglio di controllo: {os.path.join(ctrl, 'foglio-vsl.jpg')} ({len(file)} fotogrammi)")
        return

    cart_f = os.path.join(cart, "finale")
    os.makedirs(cart_f, exist_ok=True)
    v = 1
    while os.path.exists(os.path.join(cart_f, f"{nome}-v{v}.mp4")):
        v += 1
    dest = os.path.join(cart_f, f"{nome}-v{v}.mp4")
    mix, detto = audio(cart, video, piano, grafiche, dur)
    if detto:
        print("Audio: voce, " + ", ".join(detto))
    guadagno = OBIETTIVO_LUFS - lufs(mix)
    ingressi, filtro = grafo(grafiche, faccia, subs)
    script = os.path.join(cart, "montaggio.txt")
    with open(script, "w", encoding="utf-8") as f:
        f.write(filtro)
    print(f"Creo il video ({dur / 60:.1f} minuti, {len(grafiche)} grafiche)...")
    esegui([FFMPEG, "-v", "error", "-y", "-i", video, *ingressi, "-i", mix,
            "-filter_complex_script", script, "-map", "[v]", "-map", f"{ingressi.count('-i') + 1}:a", *finale_codec(),
            "-af", f"volume={guadagno:.2f}dB,alimiter=limit={10 ** (PICCO_DB / 20):.3f}:level=false:attack=5:release=50",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dest])
    # il limitatore dei picchi abbassa un po' il volume medio: se manca più di mezzo dB si rifà solo l'audio (secondi)
    manca = OBIETTIVO_LUFS - lufs(dest)
    if abs(manca) > 0.5:
        tmp = dest + ".audio.mp4"
        esegui([FFMPEG, "-v", "error", "-y", "-i", dest, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", f"volume={guadagno + manca:.2f}dB,alimiter=limit={10 ** (PICCO_DB / 20):.3f}:level=false:attack=5:release=50",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", tmp])
        os.replace(tmp, dest)
    os.remove(mix)
    scrivi(os.path.join(cart, "ultimo.json"), {"video": dest, "versione": v})
    print(f"Fatto: {dest} ({durata(dest):.1f} s, volume {lufs(dest):.1f} LUFS)")


if __name__ == "__main__":
    main()
