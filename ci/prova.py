#!/usr/bin/env python3
"""Il robot di prova dello studio: fa da solo, senza Claude, quello che fa un cliente nuovo.

  1. installa lo studio da zero con il programma di avvio (avvio.sh / avvio.ps1), poi i pezzi grandi (scarica.py)
     e il primo avvio (le due cartelle); poi il controllo silenzioso (veloce, niente da scaricare) e la riparazione
     di pezzi tolti apposta (musiche, icona, modello della faccia)
  2. prepara, taglia, trascrive e trova la faccia sul video di prova (la clip del telefono della pagina, già nello studio)
  3. monta un reel in Pulito e uno in Chiaro con la scritta dietro la testa
  4. rifà il reel Chiaro come su un computer con il disco quasi pieno (il modo "poco spazio" di rendi.py)
  5. copertina, consegna in "2 - Video finiti", controllo del video finito, controllo degli aggiornamenti
Ogni passo stampa una riga; alla fine RIUSCITO o FALLITO. Esce con 1 al primo passo che fallisce.
Solo libreria standard: gira con qualsiasi Python 3.

Uso:
  python3 ci/prova.py                       tutto, come un cliente nuovo (su GitHub o su un computer di prova)
  python3 ci/prova.py --senza-installa      niente installazione da zero: solo il controllo (che ripara e, per chi
                                            viene dalla versione di prima, fa il passaggio alla casa nuova)
  python3 ci/prova.py --studio <cartella>   prova un'altra copia dello studio (la cartella con .claude-plugin)
  python3 ci/prova.py --solo-reel           installazione e un solo reel Pulito (con --senza-installa: solo il reel)
  python3 ci/prova.py --dati-veri           usa le cartelle vere di un cliente (su GitHub: per la prova del passaggio
                                            dalla versione dei clienti, che teneva tutto in ~/.studio-video e Documenti)
  python3 ci/prova.py --passaggio <lavoro>  dopo il controllo, il lavoro fatto con la versione di prima deve esserci
Su GitHub (GITHUB_ACTIONS) la casa dello studio è quella vera, come per un cliente. Sul computer di Michael il robot
usa una casa e una cartella dati sue dentro ci/uscita (NDF_STUDIO_CASA, NDF_STUDIO_DATI): lo studio vero non si tocca.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
WIN = platform.system() == "Windows"
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = time.time()
ESITI = []


def opzione(nome, ripiego=None):
    return sys.argv[sys.argv.index(nome) + 1] if nome in sys.argv[:-1] else ripiego


PLUGIN = os.path.abspath(opzione("--studio", os.path.join(QUI, "ndf-creator-studio")))
STUDIO = os.path.join(PLUGIN, "skills", "monta-video")
STR = os.path.join(STUDIO, "strumenti")
NUOVO = os.path.exists(os.path.join(STR, "avvio.sh"))   # dalla 0.2: programma di avvio e casa nuova
USCITA = os.path.abspath(os.environ.get("PROVA_USCITA") or os.path.join(QUI, "ci", "uscita"))
SU_GITHUB = bool(os.environ.get("GITHUB_ACTIONS"))
AMBIENTE = dict(os.environ, PYTHONIOENCODING="utf-8", NDF_STUDIO_ICLOUD_FATTO="1")
if not SU_GITHUB:   # sul computer di Michael: mai la casa vera
    AMBIENTE.setdefault("NDF_STUDIO_CASA", os.path.join(os.path.dirname(USCITA), "casa-robot"))
    AMBIENTE["NDF_STUDIO_PROVA_SENZA_ICONA"] = "1"


def casa_nuova():
    if AMBIENTE.get("NDF_STUDIO_CASA"):
        return AMBIENTE["NDF_STUDIO_CASA"]
    if WIN:
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local"),
                            "NDFCreatorStudio")
    return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "NDFCreatorStudio")


CASA = casa_nuova() if NUOVO else os.path.join(os.path.expanduser("~"), ".studio-video")
PY = os.path.join(CASA, "venv", "Scripts", "python.exe") if WIN else os.path.join(CASA, "venv", "bin", "python")
if "--dati-veri" in sys.argv:
    DATI = os.path.join(CASA, "dati") if NUOVO else os.path.join(os.path.expanduser("~"), "Documents", "NDFCreatorStudio")
    AMBIENTE.pop("NDF_STUDIO_DATI", None)
else:
    DATI = os.path.abspath(os.environ.get("NDF_STUDIO_DATI") or os.path.join(USCITA, "dati"))
    AMBIENTE["NDF_STUDIO_DATI"] = DATI
LAVORI = os.path.join(DATI, "lavori")

for _s in (sys.stdout, sys.stderr):   # la console di Windows non è utf-8
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def scrivi_riga(testo):
    print(testo, flush=True)


def passo(nome, cmd, deve=None, ambiente=None, tempo=3600):
    """Un passo: lo lancia, tiene l'uscita in USCITA/log, controlla codice e (se dato) una parola nell'uscita."""
    t = time.time()
    scrivi_riga(f"\n##### {nome}  [dopo {t - T0:.0f} s]")
    try:
        p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=ambiente or AMBIENTE, timeout=tempo)
        uscita, codice = (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired:
        uscita, codice = f"FERMO: più di {tempo} s", 124
    except OSError as e:
        uscita, codice = f"NON PARTE: {e}", 127
    os.makedirs(os.path.join(USCITA, "log"), exist_ok=True)
    pulito = "".join(c if c.isalnum() or c in "-_" else "-" for c in nome.replace(" ", "-"))   # Windows: niente : ( ) ecc.
    with open(os.path.join(USCITA, "log", f"{len(ESITI) + 1:02d}-{pulito}.txt"), "w", encoding="utf-8") as f:
        f.write(" ".join(str(c) for c in cmd) + "\n\n" + uscita)
    ok = codice == 0 and (deve is None or deve in uscita)
    scrivi_riga("\n".join(uscita.strip().splitlines()[-15:]))
    controlla(nome, ok, f"{time.time() - t:.0f} s" + ("" if ok else f", codice {codice}"
                                                        + (f", manca '{deve}'" if deve and deve not in uscita else "")))
    return uscita


def controlla(nome, ok, nota=""):
    ESITI.append((nome, ok, nota))
    scrivi_riga(f"{'OK    ' if ok else 'FALLITO'} {nome}{' · ' + nota if nota else ''}")
    if not ok:
        fine()


def fine():
    scrivi_riga("\n===== RIEPILOGO =====")
    for nome, ok, nota in ESITI:
        scrivi_riga(f"{'OK    ' if ok else 'FALLITO'} {nome}{' · ' + nota if nota else ''}")
    tutto = all(ok for _, ok, _ in ESITI)
    scrivi_riga(f"\n{'RIUSCITO' if tutto else 'FALLITO'} in {(time.time() - T0) / 60:.1f} minuti · studio "
                f"{versione()} · {platform.system()} {platform.machine()}")
    sys.exit(0 if tutto else 1)


def versione():
    try:
        with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f)["version"]
    except (OSError, ValueError, KeyError):
        return "?"


def strumento(nome, *args, **kw):
    return passo(kw.pop("titolo", nome), [PY, *(["-X", "utf8"] if WIN else []), os.path.join(STR, nome + ".py"), *args], **kw)


def leggi(percorso):
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


def durata(video):
    out = subprocess.run([PY, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import comune; "
                                    "print(comune.durata(sys.argv[2]))", STR, video],
                         capture_output=True, text=True, env=AMBIENTE).stdout.strip().splitlines()
    try:
        return float(out[-1])
    except (IndexError, ValueError):
        return 0.0


def ha_audio(video):
    r = subprocess.run([PY, "-c", "import sys, subprocess; sys.path.insert(0, sys.argv[1]); import comune; "
                                  "print(subprocess.run([comune.FFPROBE, '-v', 'error', '-select_streams', 'a', "
                                  "'-show_entries', 'stream=codec_name', '-of', 'csv=p=0', sys.argv[2]], "
                                  "capture_output=True, text=True).stdout.strip())", STR, video],
                       capture_output=True, text=True, env=AMBIENTE)
    return bool(r.stdout.strip())


def uv():
    nome = "uv.exe" if WIN else "uv"
    casa = os.path.expanduser("~")
    posti = [shutil.which("uv"), os.path.join(casa, ".local", "bin", nome), os.path.join(casa, ".cargo", "bin", nome)]
    trovato = next((p for p in posti if p and os.path.exists(p)), None)
    if not trovato:   # come dice il passo 0 di SKILL.md al cliente
        if WIN:
            # su GitHub il PowerShell 7 passa i suoi moduli al PowerShell di Windows, che non li carica: si tolgono
            amb = {k: v for k, v in AMBIENTE.items() if k.upper() != "PSMODULEPATH"}
            passo("installa uv", ["powershell", "-ExecutionPolicy", "ByPass", "-c",
                                  "irm https://astral.sh/uv/install.ps1 | iex"], ambiente=amb)
        else:
            passo("installa uv", ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"])
        trovato = next((p for p in posti[1:] if p and os.path.exists(p)), None)
    controlla("uv c'è", bool(trovato))
    return trovato


def avvio(titolo, deve="PRONTO", tempo=5400):
    """Il programma di avvio, come lo lancia Claude nel Passo 0 di SKILL.md."""
    if WIN:
        # su GitHub il PowerShell 7 passa i suoi moduli al PowerShell di Windows, che non li carica: si tolgono
        amb = {k: v for k, v in AMBIENTE.items() if k.upper() != "PSMODULEPATH"}
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(STR, "avvio.ps1")]
    else:
        amb, cmd = AMBIENTE, ["sh", os.path.join(STR, "avvio.sh")]
    return passo(titolo, cmd + ["--senza-aggiornamenti"], deve=deve, ambiente=amb, tempo=tempo)


def mancanze(uscita):
    mancano = [r for r in uscita.splitlines() if r.startswith("STATO") and ": MANCA" in r]
    if mancano and "--tollera-mancanze" in sys.argv:   # la versione dei clienti, con i suoi difetti già noti
        scrivi_riga("AVVISO (versione vecchia): " + "; ".join(mancano))
    else:
        controlla("ogni pezzo installato", not mancano, "; ".join(mancano))


def installa():
    if not NUOVO:   # la versione dei clienti di prima (0.1.x): uv e installa.py
        mancanze(passo("installazione da zero (versione di prima)", [uv(), "run", "--python", "3.12", "--no-project",
                                                                     os.path.join(STR, "installa.py")],
                       deve="FINE", tempo=5400))
        return
    u = avvio("installazione da zero (programma di avvio)")
    mancanze(u)
    controlla("Python proprio dello studio (mai quello del computer)",
              os.path.exists(os.path.join(CASA, "python")), os.path.join(CASA, "python"))
    controlla("chiede il primo avvio", "primo avvio: DA FARE" in u)
    controlla("dice quanti GB scaricare", "pezzi grandi: DA SCARICARE" in u and "GB" in u)
    strumento("scarica", titolo="pezzi grandi (in sottofondo per il cliente)", deve="STATO scarica: FATTO", tempo=5400)
    primo_avvio()
    t = time.time()
    u = avvio("controllo silenzioso (seconda chat)", tempo=600)
    secondi = time.time() - t
    controlla("controllo silenzioso veloce, niente da scaricare",
              secondi < 120 and "scarico" not in u and "primo avvio" not in u and "pezzi grandi: OK" in u,
              f"{secondi:.0f} s")
    mancanze(u)
    ripara()


def primo_avvio():
    cartelle = [] if SU_GITHUB else ["--clip", os.path.join(USCITA, "1 - Clip da montare"),
                                     "--finiti", os.path.join(USCITA, "2 - Video finiti")]
    strumento("primo_avvio", "--senza-aprire", *cartelle, titolo="primo avvio: le due cartelle", deve="CARTELLE")
    conf = leggi(os.path.join(CASA, "config.json"))
    controlla("cartelle del cliente create", all(os.path.isdir(conf.get(k, "")) for k in ("clip", "finiti")),
              f"{conf.get('clip')} | {conf.get('finiti')}")


def ripara():
    """Toglie apposta tre pezzi (una musica, l'icona, il modello della faccia): il controllo li deve rimettere."""
    musiche = os.path.join(DATI, "suoni", "musiche-libere")
    tolta = sorted(f for f in os.listdir(musiche) if f.endswith(".mp3"))[0] if os.path.isdir(musiche) else None
    if tolta:
        os.remove(os.path.join(musiche, tolta))
    faccia = os.path.join(CASA, "modelli", "face_detector.tflite")
    if os.path.exists(faccia):
        os.remove(faccia)
    icona = subprocess.run([PY, os.path.join(STR, "icona.py"), "--c-e"], env=AMBIENTE).returncode == 0 and SU_GITHUB
    if icona:   # solo su GitHub: sul computer di Michael l'icona vera non si tocca
        r = subprocess.run([PY, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import icona; print(icona.dove_sta())",
                            STR], capture_output=True, text=True, env=AMBIENTE)
        dove = r.stdout.strip()
        if dove and os.path.isdir(dove):
            shutil.rmtree(dove)
        elif dove and os.path.exists(dove):
            os.remove(dove)
    u = avvio("riparazione: tolti una musica, l'icona e il modello della faccia", tempo=1800)
    controlla("la musica tolta è tornata", bool(tolta) and os.path.exists(os.path.join(musiche, tolta)), tolta or "")
    if icona:
        controlla("l'icona tolta è tornata",
                  subprocess.run([PY, os.path.join(STR, "icona.py"), "--c-e"], env=AMBIENTE).returncode == 0)
        if WIN:   # l'icona deve puntare a un programma che c'è davvero (su un PC vero mancava pythonw.exe)
            r = subprocess.run([PY, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import icona; print(icona.dove_sta())",
                                STR], capture_output=True, text=True, env=AMBIENTE)
            lnk = r.stdout.strip()
            t = subprocess.run(["powershell", "-NoProfile", "-Command",
                                f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').TargetPath"],
                               capture_output=True, text=True).stdout.strip() if lnk.endswith(".lnk") else ""
            controlla("l'icona apre un programma che c'è", bool(t) and os.path.exists(t), t or lnk)
    controlla("il controllo vede che manca un pezzo grande", "pezzi grandi: DA SCARICARE" in u)
    strumento("scarica", titolo="riscarica il pezzo grande tolto", deve="STATO scarica: FATTO", tempo=1800)
    controlla("il modello della faccia è tornato", os.path.exists(faccia))


def reel_pulito(nome):
    os.makedirs(LAVORI, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    clip = os.path.join(USCITA, "girato-di-prova.mp4")
    shutil.copyfile(os.path.join(STUDIO, "pagina", "telefono.mp4"), clip)
    if NUOVO:   # come un video allegato in chat: prima nella cartella delle clip
        u = strumento("clip_cliente", "metti", clip, titolo="video allegato messo tra le clip da montare", deve="MESSA")
        clip = [r for r in u.splitlines() if r.startswith("MESSA ")][-1][6:].strip()
        strumento("clip_cliente", "elenco", titolo="le clip da montare", deve=os.path.basename(clip))
    strumento("prepara", clip, nome, deve="SCELTE DEL CLIENTE", tempo=1800)
    cart = os.path.join(LAVORI, nome)
    frasi = leggi(os.path.join(cart, "parole_grezze.json"))
    parole = [p for fr in frasi for p in fr.get("parole", [])]
    controlla("la voce si sente (trascrizione)", len(parole) >= 20, f"{len(parole)} parole")
    fondo = leggi(os.path.join(cart, "sorgente.json"))["durata"] - 0.05
    da, a = max(0.0, parole[0]["da"] - 0.15), min(fondo, parole[-1]["a"] + 0.25)
    with open(os.path.join(cart, "tagli.json"), "w", encoding="utf-8") as f:
        json.dump([{"id": "tutto", "da": round(da, 2), "a": round(a, 2), "riga": "video di prova"}], f)
    strumento("taglia", nome, tempo=1800)
    strumento("parole", nome, tempo=1800)
    strumento("controlla_tagli", nome)
    strumento("controlla_audio", nome, deve="DA SISTEMARE")
    strumento("faccia", nome)
    f = leggi(os.path.join(cart, "faccia.json"))
    controlla("la faccia si trova", f.get("trovata", 0) >= 0.8, f"trovata {f.get('trovata', 0):.2f}")
    with open(os.path.join(cart, "piano.json"), "w", encoding="utf-8") as fp:
        json.dump({"stile": "pulito", "stile_chiesto": True, "musica": False}, fp)
    rendi(nome, "Pulito")


def rendi(nome, etichetta, poco_spazio=False):
    cart = os.path.join(LAVORI, nome)
    strumento("costruisci", nome, titolo=f"costruisci {etichetta}")
    prima = set(os.listdir(os.path.join(cart, "finale"))) if os.path.isdir(os.path.join(cart, "finale")) else set()
    amb = dict(AMBIENTE, NDF_STUDIO_PROVA_POCO_SPAZIO="1") if poco_spazio else None
    strumento("rendi", nome, titolo=f"rendi {etichetta}", ambiente=amb, tempo=3600)
    nuovi = sorted(x for x in set(os.listdir(os.path.join(cart, "finale"))) - prima if x.endswith(".mp4"))
    controlla(f"video {etichetta} uscito", bool(nuovi), ", ".join(nuovi))
    video = os.path.join(cart, "finale", nuovi[-1])
    dt, df = durata(os.path.join(cart, "tagliato.mp4")), durata(video)
    controlla(f"video {etichetta} intero", dt > 5 and 0.8 * dt <= df <= 1.1 * dt, f"{df:.1f} s (tagliato {dt:.1f} s)")
    controlla(f"video {etichetta} con l'audio", ha_audio(video))
    return video


def reel_chiaro(nome, poco_spazio):
    """Chiaro con la parola dietro la testa, sullo stesso video tagliato del reel Pulito."""
    sorg, cart = os.path.join(LAVORI, "prova-pulito"), os.path.join(LAVORI, nome)
    if os.path.exists(cart):
        shutil.rmtree(cart)
    shutil.copytree(sorg, cart, ignore=shutil.ignore_patterns("finale", "reel", "controllo"))
    d = durata(os.path.join(cart, "tagliato.mp4"))
    with open(os.path.join(DATI, "scelte.json"), "w", encoding="utf-8") as f:   # come un cliente che accende l'effetto
        json.dump({"stile": "chiaro", "effetti": ["scritte"]}, f)
    piano = {"stile": "chiaro", "stile_chiesto": True, "musica": False, "colori": {"accento": "#E86530"},
             "elementi": [
                 {"tipo": "evidenza", "da": 0.0, "a": 2.3, "sopra": "ogni giorno", "testo": "lo studio", "grande": True},
                 # parole giganti DIETRO la persona (ritaglio): l'effetto che si bloccava con il disco pieno
                 {"tipo": "scritte", "da": 2.6, "a": 5.8, "frasi": [["IL ROBOT", 2.7], ["PROVA TUTTO", 3.9]]},
                 {"tipo": "scheda", "da": round(d * 0.4, 2), "a": round(d * 0.4 + 2.5, 2), "icona": "✂️",
                  "testo": "Prova", "sotto": "il robot dello studio"},
                 {"tipo": "evidenza", "da": round(d * 0.7, 2), "a": round(d * 0.7 + 1.8, 2), "sopra": "fatto",
                  "testo": "bene"}]}
    with open(os.path.join(cart, "piano.json"), "w", encoding="utf-8") as f:
        json.dump(piano, f, ensure_ascii=False)
    video = rendi(nome, "Chiaro con disco quasi pieno" if poco_spazio else "Chiaro", poco_spazio)
    controlla("scritta dietro la testa fatta (ritaglio della persona)",
              any(x.startswith("rit-") and x.endswith(".webm") for x in os.listdir(cart)))
    return video


def dopo_aggiornamento():
    """La versione nuova su un computer che aveva quella di prima: il controllo fa il passaggio e ripara."""
    u = avvio("controllo dopo l'aggiornamento (passaggio alla casa nuova)", tempo=5400)
    mancanze(u)
    lavoro = opzione("--passaggio")
    if lavoro:
        controlla("i lavori di prima ci sono ancora", os.path.isdir(os.path.join(LAVORI, lavoro)),
                  os.path.join(LAVORI, lavoro))
        controlla("i modelli di prima spostati, non riscaricati", os.path.isdir(os.path.join(CASA, "modelli")))
    if "primo avvio: DA FARE" in u:
        primo_avvio()
    if "pezzi grandi: OK" not in u:
        strumento("scarica", titolo="pezzi grandi che mancano", deve="STATO scarica: FATTO", tempo=5400)


def main():
    scrivi_riga(f"Robot di prova · studio {versione()} · {PLUGIN}\nCasa: {CASA}\nDati di prova: {DATI}")
    if "--senza-installa" not in sys.argv:
        installa()
    elif NUOVO:
        dopo_aggiornamento()
    controlla("Python dello studio c'è", os.path.exists(PY), PY)
    reel_pulito("prova-pulito")
    if "--solo-reel" not in sys.argv:
        reel_chiaro("prova-chiaro", poco_spazio=False)
        reel_chiaro("prova-poco-spazio", poco_spazio=True)
        strumento("copertina", "prova-pulito", "--titolo", "IL ROBOT *DI PROVA*")
        controlla("copertina fatta", os.path.exists(os.path.join(LAVORI, "prova-pulito", "finale", "prova-pulito-copertina.jpg")))
        ultimo = sorted(x for x in os.listdir(os.path.join(LAVORI, "prova-chiaro", "finale")) if x.endswith(".mp4"))[-1]
        strumento("controlla_tagli", "prova-chiaro", os.path.join(LAVORI, "prova-chiaro", "finale", ultimo), "--telefono",
                  titolo="controllo del video finito")
        if NUOVO:
            consegna()
        strumento("aggiornamenti", titolo="controllo aggiornamenti (non deve rompersi)", tempo=300)
    fine()


def consegna():
    conf = leggi(os.path.join(CASA, "config.json"))
    for giro in (1, 2):   # la seconda volta la versione di prima va in "Versioni vecchie"
        strumento("clip_cliente", "consegna", "prova-pulito", titolo=f"consegna in 2 - Video finiti ({giro})",
                  deve="CONSEGNATO")
    finiti = conf["finiti"]
    controlla("video e copertina insieme nei video finiti",
              all(os.path.exists(os.path.join(finiti, f)) for f in ("prova-pulito.mp4", "prova-pulito - copertina.jpg")))
    controlla("la versione di prima in Versioni vecchie",
              len(os.listdir(os.path.join(finiti, "Versioni vecchie"))) >= 1)
    controlla("la clip montata spostata in Già montate",
              os.path.isdir(os.path.join(conf["clip"], "Già montate")) and
              not [f for f in os.listdir(conf["clip"]) if f.endswith(".mp4")])


if __name__ == "__main__":
    main()
