"""Pagina "Scegli il tuo look": l'utente sceglie uno stile pronto, oppure parte da uno stile e cambia suoni e musica,
e salva. Le scelte finiscono in DATI/scelte.json e costruisci.py le usa da sole (comune.con_le_scelte).

    PY scegli.py              apre la pagina nel browser
    PY scegli.py --non-aprire non apre il browser (scrive solo l'indirizzo)
    PY scegli.py --resta      non si spegne quando si chiude la pagina

Righe che scrive:  PAGINA PRONTA <indirizzo>  /  SCELTE SALVATE <riassunto>  /  PAGINA CHIUSA
Risponde solo da questo computer (127.0.0.1) e manda solo i file della pagina, dei suoni e delle anteprime.
Si spegne da sola circa 40 secondi dopo che la pagina è stata chiusa.
"""
import datetime
import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, SCELTE, STUDIO, leggi, scrivi  # noqa: E402
import libreria_suoni  # noqa: E402
import sottotitoli  # noqa: E402

PAGINA = os.path.join(STUDIO, "pagina", "scegli.html")
TIPI = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".mp4": "video/mp4", ".ttf": "font/ttf",
        ".jpg": "image/jpeg", ".png": "image/png"}

# i momenti del video in cui suona qualcosa: (chiave, titolo, quando, categorie della libreria da proporre)
MOMENTI = {
    "apertura": ("Apertura", "appena parte il video", ["Meme", "Colpi", "Transizioni"]),
    "transizione": ("Transizione", "quando cambia la scena e negli zoom", ["Transizioni"]),
    "impatto": ("Colpo", "sulla parola gigante", ["Colpi", "Meme"]),
    "colpo": ("Colpo", "nei momenti forti", ["Colpi", "Meme"]),
}
# i momenti che l'utente sceglie: solo quelli che cambiano il carattere del video. Gli altri (tastiera, click, pop,
# spunta, contatore...) li mette lo studio da solo quando servono, con i suoni dello stile. Lo zoom suona la transizione.
MOMENTI_MOTORE = {
    "grafica": ["transizione", "impatto", "apertura"],
    "": ["transizione", "colpo"],
}


def raccogli():
    """Tutto quello che serve alla pagina, e l'elenco dei file che si possono mandare (id -> percorso)."""
    file = {}
    suoni, visti = [], {}
    for cat, nome, gruppo, p, h in libreria_suoni.trova():
        file[h] = p
        visti[h] = len(suoni)
        suoni.append({"id": h, "nome": nome, "da": gruppo, "cat": cat})

    stili = []
    for base in (DATI, STUDIO):
        cart = os.path.join(base, "stili")
        for k in sorted(os.listdir(cart)) if os.path.isdir(cart) else []:
            j = os.path.join(cart, k, "stile.json")
            if not os.path.exists(j) or any(s["chiave"] == k for s in stili):
                continue
            st = leggi(j)
            motore = st.get("motore", "")
            di_serie = {}
            for mom, rel in st.get("suoni", {}).items():
                p = os.path.join(cart, k, rel)
                if not os.path.exists(p):
                    continue
                h = libreria_suoni.impronta(p)
                file[h] = p
                if h not in visti:  # suono che sta solo nello stile: entra nella libreria del suo momento
                    visti[h] = len(suoni)
                    cat = "Musiche" if mom == "musica" else MOMENTI.get(mom, ("", "", ["Oggetti e ambienti"]))[2][0]
                    suoni.append({"id": h, "nome": os.path.splitext(os.path.basename(rel))[0], "da": st.get("nome", k), "cat": cat})
                di_serie[mom] = h
            anteprima = os.path.join(cart, k, "anteprima.mp4")
            if os.path.exists(anteprima):
                file["anteprima-" + k] = anteprima
            if st.get("sottotitoli_nome") in sottotitoli.CATALOGO:
                di_serie["sottotitoli"] = st["sottotitoli_nome"]
            momenti = [m for m in MOMENTI_MOTORE.get(motore, MOMENTI_MOTORE[""])]
            stili.append({"chiave": k, "nome": st.get("nome", k), "descrizione": st.get("descrizione", ""),
                          "grafiche": motore == "grafica", "anteprima": os.path.exists(anteprima),
                          "di_serie": di_serie,
                          "momenti": [{"chiave": m, "titolo": MOMENTI[m][0], "quando": MOMENTI[m][1],
                                       "categorie": MOMENTI[m][2]} for m in momenti]})
            font = os.path.join(cart, k, "font", "Archivo.ttf")
            if os.path.exists(font):
                file.setdefault("font-titoli", font)

    sott = []
    for k, s in sottotitoli.CATALOGO.items():
        p = os.path.join(STUDIO, "sottotitoli", "anteprime", k + ".mp4")
        if os.path.exists(p):
            file["sott-" + k] = p
        sott.append({"chiave": k, "nome": s["nome"], "per": s["per"], "descrizione": s["descrizione"],
                     "anteprima": os.path.exists(p)})

    # le scelte salvate l'ultima volta, rimesse come id
    per_percorso = {os.path.realpath(p): h for h, p in file.items()}
    scelte = None
    try:
        sc = leggi(SCELTE)
        scelte = {"strada": sc.get("strada", "pronto"), "stile": sc.get("stile"),
                  "suoni": {m: ("" if v == "" else per_percorso.get(os.path.realpath(v)))
                            for m, v in sc.get("suoni", {}).items()},
                  "sottotitoli": sc.get("sottotitoli"),
                  "musica": "nessuna" if sc.get("musica") == "nessuna" else per_percorso.get(os.path.realpath(sc["musica"]))
                  if sc.get("musica") else None}
    except (OSError, ValueError):
        pass
    return {"stili": stili, "suoni": suoni, "sottotitoli": sott, "scelte": scelte}, file


class Pagina(BaseHTTPRequestHandler):
    dati, file, ultimo_ping = None, {}, None

    def log_message(self, *a):
        pass

    def _manda(self, codice, corpo, tipo="application/json; charset=utf-8"):
        self.send_response(codice)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _nostro(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self._nostro():
            return self._manda(403, b"{}")
        percorso = self.path.split("?")[0]
        if percorso == "/":
            with open(PAGINA, "rb") as f:
                return self._manda(200, f.read(), "text/html; charset=utf-8")
        if percorso == "/dati":
            Pagina.dati, Pagina.file = raccogli()
            return self._manda(200, json.dumps(Pagina.dati, ensure_ascii=False).encode())
        if percorso.startswith("/file/") and percorso[6:] in Pagina.file:
            p = Pagina.file[percorso[6:]]
            with open(p, "rb") as f:
                return self._manda(200, f.read(), TIPI.get(os.path.splitext(p)[1].lower(), "application/octet-stream"))
        self._manda(404, b"{}")

    def do_POST(self):
        if not self._nostro():
            return self._manda(403, b"{}")
        corpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if self.path == "/ping":
            Pagina.ultimo_ping = time.time()
            return self._manda(200, b"{}")
        if self.path == "/salva":
            stili = {s["chiave"]: s for s in Pagina.dati["stili"]}
            if corpo.get("stile") not in stili:
                return self._manda(400, json.dumps({"errore": "Scegli uno stile"}).encode())
            crea = corpo.get("strada") == "crea"
            suoni = {}
            for m, h in (corpo.get("suoni") or {}).items() if crea else []:
                if h == "":
                    suoni[m] = ""
                elif h in Pagina.file and h != stili[corpo["stile"]]["di_serie"].get(m):
                    suoni[m] = Pagina.file[h]
            musica = corpo.get("musica") if crea else None
            if musica and musica != "nessuna":
                musica = Pagina.file.get(musica) if musica != stili[corpo["stile"]]["di_serie"].get("musica") else None
            sott = corpo.get("sottotitoli") if crea else None
            if sott not in sottotitoli.CATALOGO or sott == stili[corpo["stile"]]["di_serie"].get("sottotitoli"):
                sott = None  # quelli dello stile
            scrivi(SCELTE, {"strada": "crea" if crea else "pronto", "stile": corpo["stile"], "sottotitoli": sott, "suoni": suoni,
                            "musica": musica, "aggiornato": datetime.datetime.now().isoformat(timespec="seconds")})
            print(f"SCELTE SALVATE stile={corpo['stile']} sottotitoli={sott or 'dello stile'} suoni cambiati={len(suoni)} "
                  f"musica={'nessuna' if musica == 'nessuna' else ('cambiata' if musica else 'di serie')}", flush=True)
            return self._manda(200, b"{}")
        self._manda(404, b"{}")


def main():
    Pagina.dati, Pagina.file = raccogli()
    server = None
    for porta in (4848, 4849, 4850, 0):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", porta), Pagina)
            break
        except OSError:
            continue
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"PAGINA PRONTA {url}", flush=True)
    if "--non-aprire" not in sys.argv:
        webbrowser.open(url)

    def guardiano():  # si spegne quando la pagina è chiusa da un po' (un ricaricamento non conta)
        while True:
            time.sleep(5)
            if Pagina.ultimo_ping and time.time() - Pagina.ultimo_ping > 40:
                print("PAGINA CHIUSA", flush=True)
                server.shutdown()
                return

    if "--resta" not in sys.argv:
        threading.Thread(target=guardiano, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
