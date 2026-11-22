"""VSL orizzontale, passo 2: taglia il video lungo (16:9, 1920x1080) seguendo lavori/<nome>/tagli.json.

Uso:  PY strumenti/vsl_taglia.py <nome-lavoro> [--respiri | --senza-stringere] [--voce-originale | --voce-forte]
                                  [--senza-zoom]

È il fratello orizzontale di taglia.py (che resta solo per i reel verticali). Stesse regole:
  - prima stringi.py toglie le pause (tagli-scelti.json resta la scelta di Claude: l'ultima ripresa buona di ogni frase)
  - voce pulita con DeepFilterNet (pulitore.py), con ritorno alla pulizia di prima se manca
  - HDR dell'iPhone riportato ai colori normali
In più, pensato per video di 10-15 minuti:
  - il video si crea a blocchi di circa un minuto (memoria bassa anche con 300 tagli), l'audio in una passata sola
  - zoom leggeri sulla faccia a ogni cambio di frase (largo, poco stretto, largo, più stretto), già dentro il taglio:
    la faccia resta ferma nel suo punto e il salto tra due riprese non si nota
  - le parole della prima trascrizione si spostano sui tempi del taglio: niente seconda trascrizione

Scrive:
  tagliato.mp4      1920x1080, con i fotogrammi al secondo del girato (25 o 30), voce pulita (il volume lo fa vsl_monta.py)
  segmenti.json     dove inizia ogni pezzo nel video tagliato
  faccia.json       dove sta la faccia (in pixel del 1920x1080), per il riquadro piccolo della persona
  parole.json       ogni parola con i tempi del video tagliato (per i sottotitoli)
  testo.txt         il testo del video tagliato, frase per frase con i tempi: da qui si scelgono le grafiche
"""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import FFMPEG, MODELLI, cartella_lavoro, codec_video, durata, esegui, leggi, scrivi  # noqa: E402
from taglia import COLORE_HDR, DISSOLVENZA, VOCE, VOCE_FORTE, VOCE_LEGGERA, VOCE_VENTO, e_hdr  # noqa: E402

LARGO, ALTO = 1920, 1080
# fotogrammi al secondo: quelli del girato, mai convertiti (25 resta 25, 30 resta 30). Li fissa main().
FPS, FPS_TESTO = 30.0, "30"
FPS_NOTI = {24: "24", 25: "25", 29.97: "30000/1001", 30: "30", 50: "50", 59.94: "60000/1001", 60: "60"}


def fps_sorgente(video):
    """I fotogrammi al secondo del video: il valore standard più vicino (i telefoni a volte segnano 29.98 o 30.02)."""
    from comune import FFPROBE
    out = esegui([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate,r_frame_rate",
                  "-of", "csv=p=0", video]).stdout.strip().splitlines()[0]
    valori = []
    for x in out.split(","):
        if "/" in x and not x.endswith("/0"):
            a, b = x.split("/")
            valori.append(float(a) / float(b))
    vero = valori[-1] if valori else 30.0
    vicino = min(FPS_NOTI, key=lambda v: abs(v - vero))
    testo = FPS_NOTI[vicino]
    a, _, b = testo.partition("/")
    return float(a) / float(b or 1), testo
BLOCCO = 40.0              # secondi di video per blocco
# a ogni stacco l'inquadratura si stringe o si allarga (è il ritmo delle VSL che funzionano), ma leggera
ZOOM = [1.0, 1.08, 1.0, 1.14, 1.04, 1.1]
ZOOM_OGNI = 2.5            # secondi minimi tra due cambi di zoom
QUADRO = f"scale={LARGO}:{ALTO}:force_original_aspect_ratio=increase:flags=lanczos,crop={LARGO}:{ALTO},setsar=1"


def a_fotogramma(t):
    return round(round(t * FPS) / FPS, 4)


def facce(video, dur):
    """Centro e altezza della faccia ogni 2 secondi del video ORIGINALE, in pixel del 1920x1080."""
    tmp = tempfile.mkdtemp()
    try:
        esegui([FFMPEG, "-v", "error", "-i", video, "-vf", f"fps=0.5,{QUADRO},scale=640:360", "-q:v", "4",
                os.path.join(tmp, "f%05d.jpg")])
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision
        ril = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=os.path.join(MODELLI, "face_detector.tflite")),
            min_detection_confidence=0.5))
        out, k = [], LARGO / 640
        for i, nome in enumerate(sorted(os.listdir(tmp))):
            r = ril.detect(mp.Image.create_from_file(os.path.join(tmp, nome)))
            if r.detections:
                b = max(r.detections, key=lambda d: d.bounding_box.width * d.bounding_box.height).bounding_box
                out.append({"t": i * 2 + 1, "x": (b.origin_x + b.width / 2) * k, "y": (b.origin_y + b.height / 2) * k,
                            "h": b.height * k})
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mediana(v):
    v = sorted(v)
    return v[len(v) // 2]


def faccia_in(campioni, da, a, tutta):
    dentro = [c for c in campioni if da - 2 <= c["t"] <= a + 2] or tutta
    return mediana([c["x"] for c in dentro]), mediana([c["y"] for c in dentro])


# ritmo: misurato sulla trascrizione delle riprese scelte. Una persona lenta (poche parole al minuto o pause lunghe)
# rende la VSL "moscia": lo studio la rende più dinamica da solo, senza toccare la voce.
LENTA_PAROLE, LENTA_PAUSA = 165, 0.5   # sotto 165 parole al minuto o pause medie sopra mezzo secondo
OBIETTIVO_PAROLE = 168                 # velocità che si cerca di raggiungere, al massimo +8% (i reel arrivano a +12%)


def ritmo(cart):
    """Parole al minuto e pausa media tra le frasi, nelle riprese scelte da Claude (tagli-scelti.json)."""
    scelti = leggi(os.path.join(cart, "tagli-scelti.json" if os.path.exists(os.path.join(cart, "tagli-scelti.json"))
                                else "tagli.json"))
    parole = [w for fr in leggi(os.path.join(cart, "parole_grezze.json")) for w in fr["parole"]
              if any(t["da"] - 0.05 <= (w["da"] + w["a"]) / 2 <= t["a"] + 0.05 for t in scelti)]
    if len(parole) < 20:
        return {"parole_minuto": 0, "pausa_media": 0, "lenta": False, "velocita": 1.0, "zoom_ogni": ZOOM_OGNI}
    spazi = [b["da"] - a["a"] for a, b in zip(parole, parole[1:]) if 0 < b["da"] - a["a"] < 1.5]
    parlato = sum(w["a"] - w["da"] for w in parole) + sum(spazi)
    pm = len(parole) / parlato * 60
    pause = [x for x in spazi if x > 0.15]
    pausa = sum(pause) / len(pause) if pause else 0
    lenta = pm < LENTA_PAROLE or pausa > LENTA_PAUSA
    vel = round(min(max(OBIETTIVO_PAROLE / pm, 1.05), 1.08), 2) if lenta else 1.0
    return {"parole_minuto": round(pm), "pausa_media": round(pausa, 2), "lenta": lenta, "velocita": vel,
            "zoom_ogni": 1.8 if lenta else ZOOM_OGNI}


def zoom_dei_pezzi(tagli, campioni, ogni=ZOOM_OGNI):
    """Uno zoom per pezzo: cambia solo su un taglio (lì il salto si nasconde), al massimo ogni ZOOM_OGNI secondi.
    Anche dentro una frase lunga: ogni pausa tolta da stringi.py è un taglio."""
    tutta = campioni or [{"x": LARGO / 2, "y": ALTO * 0.4, "h": ALTO / 3}]
    k, ultimo, t_cut, z = 0, -99.0, 0.0, ZOOM[0]
    for t in tagli:
        if t_cut - ultimo >= ogni:
            z, k, ultimo = ZOOM[k % len(ZOOM)], k + 1, t_cut
        cx, cy = faccia_in(campioni, t["da"], t["a"], tutta)
        t["_zoom"] = (z, cx, cy)
        t_cut += t["a"] - t["da"]


def filtro_zoom(z, cx, cy):
    if z <= 1.001:
        return ""
    w, h = round(LARGO / z / 2) * 2, round(ALTO / z / 2) * 2
    # la faccia resta nello stesso punto dello schermo: si stringe "attorno" a lei
    x = min(max(cx * (1 - 1 / z), 0), LARGO - w)
    y = min(max(cy * (1 - 1 / z), 0), ALTO - h)
    return f",crop={w}:{h}:{x:.0f}:{y:.0f},scale={LARGO}:{ALTO}:flags=lanczos"


def blocco_video(video, pezzi, colore, dest):
    """Un blocco di pezzi: ogni pezzo è un ingresso a sé, letto dal suo punto (ffmpeg li legge uno dopo l'altro,
    così la memoria resta bassa anche con pezzi lunghi). Ogni pezzo dà esattamente durata x 30 fotogrammi."""
    ingressi, filtri = [], []
    for i, p in enumerate(pezzi):
        z, cx, cy = p["_zoom"]
        n_fot = round((p["a"] - p["da"]) * FPS)
        ingressi += ["-ss", f"{p['da']:.4f}", "-t", f"{p['a'] - p['da'] + 0.5:.4f}", "-i", video]
        filtri.append(f"[{i}:v]setpts=PTS-STARTPTS,fps={FPS_TESTO},trim=end_frame={n_fot},{QUADRO}"
                      f"{filtro_zoom(z, cx, cy)},setsar=1{colore}[v{i}]")
    n = len(pezzi)
    filtri.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,setpts=N/({FPS_TESTO})/TB[v]")
    # -r: senza, ffmpeg non sa più la velocità dopo setpts e salva a 25 buttando fotogrammi
    esegui([FFMPEG, "-v", "error", "-y", *ingressi, "-filter_complex", ";".join(filtri), "-map", "[v]", "-an",
            "-r", FPS_TESTO, *codec_video(), dest])


def parole_sul_taglio(cart, segmenti):
    """Le parole della trascrizione dell'originale, portate sui tempi del taglio (solo quelle tenute)."""
    grezze = leggi(os.path.join(cart, "parole_grezze.json"))
    out, prec = [], None
    for fr in grezze:
        for w in fr["parole"]:
            prima, prec = prec, w   # la parola grezza di prima (anche se è stata tolta)
            # Whisper mette spesso l'inizio delle parole un po' prima della voce vera: si tiene la parola se tocca un
            # pezzo tenuto (il pezzo con più sovrapposizione), non solo se il suo centro ci cade dentro
            def sopra(s):
                return min(w["a"], s["a_originale"]) - max(w["da"], s["da_originale"])
            s = max(segmenti, key=sopra)
            if sopra(s) < 0.03 or not w["testo"]:
                continue
            v = s.get("velocita", 1.0)
            da = s["inizio"] + (max(w["da"], s["da_originale"]) - s["da_originale"]) / v
            a = s["inizio"] + (min(w["a"], s["a_originale"]) - s["da_originale"]) / v
            if w["testo"].startswith("'") and (not out or out[-1]["_grezza"] is not prima):
                w = dict(w, testo=(prima["testo"] if prima else "") + w["testo"])   # "l" + "'acqua": la "l" era fuori
            elif out and w["testo"].startswith("'"):
                out[-1]["testo"] += w["testo"]
                out[-1]["a"] = round(a, 2)
                continue
            out.append({"testo": w["testo"], "da": round(da, 2), "a": round(max(a, da + 0.05), 2), "_pezzo": s["id"],
                        "_grezza": w})
    # fine di una frase scelta da Claude (pezzo diverso in tagli-scelti.json): se manca, ci va il punto, così i
    # sottotitoli vanno a capo lì e non uniscono due riprese diverse
    def base(i):
        return i.rsplit("-", 1)[0] if i.rsplit("-", 1)[-1].isdigit() else i
    for k, w in enumerate(out):
        if k + 1 < len(out) and base(out[k + 1]["_pezzo"]) != base(w["_pezzo"]) and w["testo"][-1:].isalnum():
            w["testo"] += "."
    for w in out:
        del w["_pezzo"], w["_grezza"]
    return out


def scrivi_testo(cart, parole):
    """Il testo tagliato in frasi (a capo dopo il punto o dopo una pausa), con i tempi: per scegliere le grafiche."""
    righe, cur = [], []
    for i, w in enumerate(parole):
        cur.append(w)
        fine = w["testo"].endswith((".", "?", "!")) or (i + 1 < len(parole) and parole[i + 1]["da"] - w["a"] > 0.6)
        if fine or i == len(parole) - 1:
            righe.append(f"[{cur[0]['da']:7.2f} → {cur[-1]['a']:7.2f}] " + " ".join(x["testo"] for x in cur))
            righe.append("    " + " ".join(f"{x['testo']}@{x['da']:.2f}" for x in cur))
            cur = []
    with open(os.path.join(cart, "testo.txt"), "w", encoding="utf-8") as f:
        f.write("# testo del video tagliato: [da → a] frase, poi parola@inizio (secondi del video tagliato)\n\n")
        f.write("\n".join(righe) + "\n")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = sys.argv[1]
    cart = cartella_lavoro(nome)
    sorgente = leggi(os.path.join(cart, "sorgente.json"))
    video = sorgente["video"]
    global FPS, FPS_TESTO
    FPS, FPS_TESTO = fps_sorgente(video)
    if "--senza-stringere" not in sys.argv:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "stringi.py"), nome,
                        *[f for f in ("--respiri", "--voce-originale") if f in sys.argv]], check=True)
    tagli = leggi(os.path.join(cart, "tagli.json"))
    if not tagli:
        sys.exit("tagli.json è vuoto")
    for t in tagli:
        t["da"], t["a"] = a_fotogramma(t["da"]), a_fotogramma(t["a"])
        if not 0 <= t["da"] < t["a"] <= sorgente["durata"] + 0.05:
            sys.exit(f"Tempi sbagliati nel pezzo '{t['id']}': {t['da']} → {t['a']}")
    tagli = [t for t in tagli if t["a"] - t["da"] >= 1 / FPS]

    r = ritmo(cart)
    if "--velocita" in sys.argv:   # per forzarla (1 = com'è girata)
        r["velocita"] = float(sys.argv[sys.argv.index("--velocita") + 1])
    vel = r["velocita"]
    scrivi(os.path.join(cart, "ritmo.json"), r)
    print(f"Ritmo: {r['parole_minuto']} parole al minuto, pause di {r['pausa_media']} s"
          + (f" → lenta: velocità +{round((vel - 1) * 100)}%, zoom più spessi, più clip e grafiche nei tratti piatti, "
             "musica con più energia" if r["lenta"] else " → va bene così"))

    hdr = e_hdr(video)
    colore = f",{COLORE_HDR}" if hdr else ""
    if hdr:
        print("Il video è in HDR: correggo i colori.")

    print("Cerco la faccia...")
    campioni = facce(video, sorgente["durata"])
    if "--senza-zoom" in sys.argv:
        for t in tagli:
            t["_zoom"] = (1.0, 0, 0)
    else:
        zoom_dei_pezzi(tagli, campioni, r["zoom_ogni"])

    # --- video a blocchi ---
    blocchi, cur = [], []
    for t in tagli:
        if cur and (sum(p["a"] - p["da"] for p in cur) >= BLOCCO or len(cur) >= 30):
            blocchi.append(cur)
            cur = []
        cur.append(t)
    blocchi.append(cur)
    tmp = tempfile.mkdtemp(dir=cart)
    print(f"Taglio {len(tagli)} pezzi in {len(blocchi)} blocchi...")
    file_blocchi = [os.path.join(tmp, f"b{i:03d}.mp4") for i in range(len(blocchi))]
    with ThreadPoolExecutor(3) as pool:
        list(pool.map(lambda ib: blocco_video(video, ib[1], colore, file_blocchi[ib[0]]), enumerate(blocchi)))
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.write("".join(f"file '{p}'\n" for p in file_blocchi))
    solo_video = os.path.join(tmp, "video.mp4")
    esegui([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", solo_video])

    # --- audio in una passata, dalla voce pulita ---
    voce = "anull" if "--voce-originale" in sys.argv else VOCE_FORTE if "--voce-forte" in sys.argv else "deepfilter"
    df_ok, pulita = False, os.path.join(tmp, "voce-pulita.wav")
    if voce == "deepfilter":
        from pulitore import pulisci
        grezza = os.path.join(tmp, "voce-grezza.wav")
        esegui([FFMPEG, "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", grezza])
        print("Pulisco la voce con DeepFilterNet...")
        df_ok = pulisci(grezza, pulita)
        print("Voce pulita con DeepFilterNet." if df_ok else "DeepFilterNet non disponibile: uso la pulizia normale.")
    scelte = {"deepfilter": "anull" if df_ok else VOCE, "originale": "anull", "normale": VOCE, "forte": VOCE_FORTE,
              "leggera": VOCE_LEGGERA, "vento": VOCE_VENTO}
    filtri, segmenti, inizio = [], [], 0.0
    for i, t in enumerate(tagli):
        d = t["a"] - t["da"]
        scelta = t.get("voce") if t.get("voce") in scelte else voce
        ingresso = "1:a" if df_ok and scelta == "deepfilter" else "0:a"
        filtri.append(f"[{ingresso}]atrim={t['da']}:{t['a']},asetpts=PTS-STARTPTS,{scelte.get(scelta, scelta)},"
                      f"aresample=48000,aformat=sample_fmts=s16:channel_layouts=mono,"
                      f"afade=t=in:d={DISSOLVENZA},afade=t=out:st={max(d - DISSOLVENZA, 0):.3f}:d={DISSOLVENZA}[a{i}]")
        segmenti.append({"id": t["id"], "inizio": round(inizio / vel, 3), "fotogramma": round(inizio / vel * FPS),
                         "durata": round(d / vel, 3), "da_originale": t["da"], "a_originale": t["a"],
                         "zoom": t["_zoom"][0], "velocita": vel})
        inizio += d
    n = len(tagli)
    filtri.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,aformat=channel_layouts=stereo"
                  + (f",atempo={vel}" if vel != 1 else "") + "[a]")   # più veloce senza cambiare il tono della voce
    graf = os.path.join(tmp, "audio.txt")
    with open(graf, "w") as f:
        f.write(";".join(filtri))
    solo_audio = os.path.join(tmp, "audio.m4a")
    esegui([FFMPEG, "-v", "error", "-y", "-i", video, *(["-i", pulita] if df_ok else []), "-filter_complex_script", graf,
            "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", solo_audio])

    dest = os.path.join(cart, "tagliato.mp4")
    if vel != 1:   # il video va alla stessa velocità della voce, con gli stessi fotogrammi al secondo
        veloce = os.path.join(tmp, "video-veloce.mp4")
        esegui([FFMPEG, "-v", "error", "-y", "-i", solo_video, "-vf", f"setpts=PTS/{vel}", "-r", FPS_TESTO, "-an",
                *codec_video(), veloce])
        solo_video = veloce
    esegui([FFMPEG, "-v", "error", "-y", "-i", solo_video, "-i", solo_audio, "-map", "0:v", "-map", "1:a", "-c", "copy",
            *(["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"] if hdr else []),
            "-movflags", "+faststart", dest])
    dv, da = durata(solo_video), durata(solo_audio)
    shutil.rmtree(tmp, ignore_errors=True)

    scrivi(os.path.join(cart, "segmenti.json"), segmenti)
    if campioni:
        scrivi(os.path.join(cart, "faccia.json"), {"x": round(mediana([c["x"] for c in campioni])),
                                                   "y": round(mediana([c["y"] for c in campioni])),
                                                   "h": round(mediana([c["h"] for c in campioni])),
                                                   "trovata": len(campioni)})
    parole = parole_sul_taglio(cart, segmenti)
    scrivi(os.path.join(cart, "parole.json"), parole)
    scrivi_testo(cart, parole)
    print(f"Fatto: {sorgente['durata']:.1f} s → {inizio / vel:.1f} s (video {dv:.2f} s, audio {da:.2f} s), "
          f"{len(parole)} parole. Leggi {os.path.join(cart, 'testo.txt')}")


if __name__ == "__main__":
    main()
