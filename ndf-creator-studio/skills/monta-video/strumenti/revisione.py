"""Pagina di revisione: il cliente guarda il reel finito, lo ferma dove vuole cambiare qualcosa, preme «Nota qui» e
scrive la correzione; alla fine preme «Correggi» oppure «Approva». Come la pagina del look: gira sul computer
(127.0.0.1), si apre nel browser.

    PY revisione.py NOME              apre l'ultima versione (finale/NOME-vN.mp4)
    PY revisione.py NOME --versione v2
    PY revisione.py NOME --non-aprire non apre il browser (scrive solo l'indirizzo)

Le note stanno in lavori/NOME/note.json:
  {"versione": "v2", "stato": "in revisione" | "da correggere" | "approvato",
   "velocita": 1.05, "note": [{"id": 1, "t": 12.4, "t_piano": 13.02, "testo": "...", "versione": "v2",
                               "fatta": false, "risposta": ""}]}
  t = secondo del video finito (quello che vede il cliente); t_piano = lo stesso momento nei tempi del piano
  (il video finito è accelerato: t_piano = t x velocita).
Righe che scrive:  PAGINA PRONTA <indirizzo>  /  CORREGGI <n> note (versione vN)  /  APPROVATO vN  /  PAGINA CHIUSA
Dopo «Correggi» o «Approva» la pagina si chiude da sola (così chi l'ha lanciata in sottofondo se ne accorge subito);
altrimenti si spegne circa 40 secondi dopo che è stata chiusa.
"""
import datetime
import json
import os
import re
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import STUDIO, VELOCITA, cartella_lavoro, con_le_scelte, leggi, scrivi  # noqa: E402

PAGINA = os.path.join(STUDIO, "pagina", "revisione.html")


def versioni(cart, nome):
    """Le versioni finite del lavoro, dalla più vecchia: [("v1", percorso), ...]."""
    fin = os.path.join(cart, "finale")
    trovate = []
    for f in os.listdir(fin) if os.path.isdir(fin) else []:
        m = re.fullmatch(re.escape(nome) + r"-v(\d+)\.mp4", f)
        if m:
            trovate.append((int(m.group(1)), os.path.join(fin, f)))
    return [(f"v{n}", p) for n, p in sorted(trovate)]


def velocita(cart):
    """Quanto è accelerato il video finito: come lo calcola rendi.py."""
    try:
        pi = leggi(os.path.join(cart, "piano.json"))
    except (OSError, ValueError):
        pi = {}
    return float(pi.get("velocita") or con_le_scelte(pi.get("stile", ""), {}).get("velocita") or VELOCITA)


class Pagina(BaseHTTPRequestHandler):
    cart = video = versione = None
    vel = 1.0
    ultimo_ping = None
    finito = False

    def log_message(self, *a):
        pass

    def _nostro(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def _manda(self, codice, corpo, tipo="application/json; charset=utf-8", extra=None):
        self.send_response(codice)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(corpo)
        except (BrokenPipeError, ConnectionResetError):   # il browser ha cambiato idea (salto nel video): normale
            pass

    def _note(self):
        p = os.path.join(Pagina.cart, "note.json")
        try:
            d = leggi(p)
        except (OSError, ValueError):
            d = {"note": []}
        d["versione"], d["velocita"] = Pagina.versione, Pagina.vel
        d.setdefault("stato", "in revisione")
        return d

    def do_GET(self):
        if not self._nostro():
            return self._manda(403, b"{}")
        percorso = self.path.split("?")[0]
        if percorso == "/":
            with open(PAGINA, "rb") as f:
                return self._manda(200, f.read(), "text/html; charset=utf-8")
        if percorso == "/dati":
            return self._manda(200, json.dumps(self._note(), ensure_ascii=False).encode())
        if percorso == "/video":   # con i pezzi (Range): così il video si può portare a qualsiasi secondo, anche in Safari
            size = os.path.getsize(Pagina.video)
            r = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
            da, a = 0, size - 1
            if r:
                if r.group(1):
                    da = int(r.group(1))
                    # senza una fine si manda un pezzo da 2 MB: il browser chiede il resto quando gli serve
                    a = int(r.group(2)) if r.group(2) else da + 2 * 1024 * 1024 - 1
                elif r.group(2):
                    da = max(0, size - int(r.group(2)))
                a = min(a, size - 1)
            else:   # senza Range: il file intero, a pezzi, senza caricarlo tutto in memoria
                self.send_response(200)
                for k, v in (("Content-Type", "video/mp4"), ("Content-Length", str(size)), ("Accept-Ranges", "bytes"),
                             ("Cache-Control", "no-store")):
                    self.send_header(k, v)
                self.end_headers()
                try:
                    with open(Pagina.video, "rb") as f:
                        while True:
                            pezzo = f.read(1024 * 1024)
                            if not pezzo:
                                break
                            self.wfile.write(pezzo)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            with open(Pagina.video, "rb") as f:
                f.seek(da)
                corpo = f.read(a - da + 1)
            extra = {"Accept-Ranges": "bytes"}
            if r:
                extra["Content-Range"] = f"bytes {da}-{a}/{size}"
            return self._manda(206 if r else 200, corpo, "video/mp4", extra)
        self._manda(404, b"{}")

    def do_POST(self):
        if not self._nostro():
            return self._manda(403, b"{}")
        corpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if self.path == "/ping":
            Pagina.ultimo_ping = time.time()
            return self._manda(200, b"{}")
        if self.path in ("/salva", "/fine"):
            d = self._note()
            vecchie = [n for n in d.get("note", []) if n.get("versione") != Pagina.versione or n.get("fatta")]
            nuove = []
            for i, n in enumerate(corpo.get("note", [])):
                testo = str(n.get("testo", "")).strip()[:600]
                if not testo:
                    continue
                t = round(max(0.0, float(n.get("t", 0))), 2)
                nuove.append({"id": len(vecchie) + i + 1, "t": t, "t_piano": round(t * Pagina.vel, 2), "testo": testo,
                              "versione": Pagina.versione, "fatta": False, "risposta": ""})
            d["note"] = vecchie + nuove
            if self.path == "/fine":
                d["stato"] = "approvato" if corpo.get("azione") == "approva" else "da correggere"
                d["quando"] = datetime.datetime.now().isoformat(timespec="seconds")
            scrivi(os.path.join(Pagina.cart, "note.json"), d)
            if self.path == "/fine":
                if d["stato"] == "approvato":
                    print(f"APPROVATO {Pagina.versione}" + (f" (con {len(nuove)} note da leggere)" if nuove else ""), flush=True)
                else:
                    print(f"CORREGGI {len(nuove)} note (versione {Pagina.versione}): {os.path.join(Pagina.cart, 'note.json')}",
                          flush=True)
                Pagina.finito = True
            return self._manda(200, b"{}")
        self._manda(404, b"{}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    nome = args[0]
    cart = cartella_lavoro(nome)
    vv = versioni(cart, nome)
    if not vv:
        sys.exit("Non c'è ancora un video finito per questo lavoro: prima rendi.py.")
    chiesta = sys.argv[sys.argv.index("--versione") + 1] if "--versione" in sys.argv else None
    versione, video = next(((v, p) for v, p in vv if v == chiesta), vv[-1])
    Pagina.cart, Pagina.video, Pagina.versione, Pagina.vel = cart, video, versione, velocita(cart)
    d = Pagina._note(Pagina)   # nuova versione: lo stato torna «in revisione»
    if d.get("versione_pagina") != versione:
        d["stato"], d["versione_pagina"] = "in revisione", versione
        scrivi(os.path.join(cart, "note.json"), d)
    server = None
    for porta in (4860, 4861, 4862, 0):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", porta), Pagina)
            server.daemon_threads = True
            break
        except OSError:
            continue
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"PAGINA PRONTA {url}", flush=True)
    if "--non-aprire" not in sys.argv:
        webbrowser.open(url)

    def guardiano():
        while True:
            time.sleep(1)
            if Pagina.finito:
                time.sleep(1.5)   # il tempo di mostrare «Fatto» nella pagina
                server.shutdown()
                return
            if Pagina.ultimo_ping and time.time() - Pagina.ultimo_ping > 40:
                print("PAGINA CHIUSA", flush=True)
                server.shutdown()
                return

    threading.Thread(target=guardiano, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
