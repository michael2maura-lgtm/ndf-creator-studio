#!/usr/bin/env python3
"""Il robot di prova dello studio: fa da solo, senza Claude, quello che fa un cliente nuovo.

  1. installa lo studio da zero (installa.py, come con "installa lo studio")
  2. prepara, taglia, trascrive e trova la faccia sul video di prova (la clip del telefono della pagina, già nello studio)
  3. monta un reel in Pulito e uno in Chiaro con la scritta dietro la testa
  4. rifà il reel Chiaro come su un computer con il disco quasi pieno (il modo "poco spazio" di rendi.py)
  5. copertina, controllo del video finito, controllo degli aggiornamenti
Ogni passo stampa una riga; alla fine RIUSCITO o FALLITO. Esce con 1 al primo passo che fallisce.
Solo libreria standard: gira con qualsiasi Python 3.

Uso:
  python3 ci/prova.py                       tutto, come un cliente nuovo (su GitHub o su un computer di prova)
  python3 ci/prova.py --senza-installa      salta l'installazione (usa lo studio già installato in ~/.studio-video)
  python3 ci/prova.py --studio <cartella>   prova un'altra copia dello studio (la cartella con .claude-plugin)
  python3 ci/prova.py --solo-reel           installazione e un solo reel Pulito (con --senza-installa: solo il reel)
Il robot lavora in una cartella dati sua (NDF_STUDIO_DATI, di serie una cartella nuova accanto a ci/): i lavori e le
scelte del cliente di questo computer non si toccano. Se NDF_STUDIO_DATI è già impostata, usa quella (serve alla
prova dell'aggiornamento: stessa cartella dati con la versione vecchia e poi con quella nuova).
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
CASA = os.path.join(os.path.expanduser("~"), ".studio-video")
PY = os.path.join(CASA, "venv", "Scripts", "python.exe") if WIN else os.path.join(CASA, "venv", "bin", "python")
USCITA = os.path.abspath(os.environ.get("PROVA_USCITA") or os.path.join(QUI, "ci", "uscita"))
DATI = os.path.abspath(os.environ.get("NDF_STUDIO_DATI") or os.path.join(USCITA, "dati"))
AMBIENTE = dict(os.environ, NDF_STUDIO_DATI=DATI, PYTHONIOENCODING="utf-8", NDF_STUDIO_ICLOUD_FATTO="1")
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
    with open(os.path.join(USCITA, "log", f"{len(ESITI) + 1:02d}-{nome.replace(' ', '-')}.txt"), "w", encoding="utf-8") as f:
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
            passo("installa uv", ["powershell", "-ExecutionPolicy", "ByPass", "-c",
                                  "irm https://astral.sh/uv/install.ps1 | iex"])
        else:
            passo("installa uv", ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"])
        trovato = next((p for p in posti[1:] if p and os.path.exists(p)), None)
    controlla("uv c'è", bool(trovato))
    return trovato


def installa():
    uscita = passo("installazione da zero", [uv(), "run", "--python", "3.12", "--no-project",
                                            os.path.join(STR, "installa.py")], deve="FINE", tempo=5400)
    mancano = [r for r in uscita.splitlines() if r.startswith("STATO") and ": MANCA" in r]
    controlla("ogni pezzo installato", not mancano, "; ".join(mancano))


def reel_pulito(nome):
    os.makedirs(LAVORI, exist_ok=True)
    clip = os.path.join(USCITA, "girato-di-prova.mp4")
    shutil.copyfile(os.path.join(STUDIO, "pagina", "telefono.mp4"), clip)
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


def main():
    scrivi_riga(f"Robot di prova · studio {versione()} · {PLUGIN}\nDati di prova: {DATI}")
    if "--senza-installa" not in sys.argv:
        installa()
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
        strumento("aggiornamenti", titolo="controllo aggiornamenti (non deve rompersi)", tempo=300)
    fine()


if __name__ == "__main__":
    main()
