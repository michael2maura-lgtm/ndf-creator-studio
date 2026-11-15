"""Pagina "Scegli il tuo look": l'utente sceglie uno stile pronto, oppure parte da uno stile e cambia suoni e musica,
e salva. Le scelte finiscono in DATI/scelte.json e costruisci.py le usa da sole (comune.con_le_scelte).

    PY scegli.py              apre la pagina nel browser
    PY scegli.py --non-aprire non apre il browser (scrive solo l'indirizzo)
    PY scegli.py --resta      non si spegne quando si chiude la pagina

Righe che scrive:  PAGINA PRONTA <indirizzo>  /  BRAND SALVATO <riassunto>  /  SCELTE SALVATE <riassunto>  /  PAGINA CHIUSA
Senza colore in DATI/profilo.json la pagina Stile mostra in alto l'invito ad andare su /brand (le domande iniziali).
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
import colore  # noqa: E402
import effetti  # noqa: E402
import sottotitoli  # noqa: E402
import ritocchi  # noqa: E402

PAGINA = os.path.join(STUDIO, "pagina", "scegli.html")
PAGINA_BRAND = os.path.join(STUDIO, "pagina", "brand.html")   # le domande iniziali: colore, logo, nome, parole (DATI/profilo.json)
PROFILO = os.path.join(DATI, "profilo.json")
PAGINA_EFFETTI = os.path.join(STUDIO, "pagina", "effetti.html")   # gli effetti: il cliente accende quelli che gli piacciono
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
            if st.get("nascosto"):   # stili vecchi uniti nei modelli pronti: restano salvati e si usano per nome, ma la
                continue             # pagina mostra solo i modelli e gli stili nuovi del cliente (Michael, 14/11: "ripartiamo da 0")
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
            if os.path.exists(anteprima[:-4] + ".jpg"):  # la copertina: il browser non salta a un secondo preciso
                file["anteprima-" + k + "-jpg"] = anteprima[:-4] + ".jpg"
            if st.get("sottotitoli_nome") in sottotitoli.CATALOGO:
                di_serie["sottotitoli"] = st["sottotitoli_nome"]
            momenti = [m for m in MOMENTI_MOTORE.get(motore, MOMENTI_MOTORE[""])]
            stili.append({"chiave": k, "modello": bool(st.get("modello")), "nome": st.get("nome", k), "descrizione": st.get("descrizione", ""), "mio": base == DATI and not os.path.isdir(os.path.join(STUDIO, "stili", k)),   # una copia di uno stile pronto non è "tuo"
                          "effetti": st.get("effetti"), "transizione": st.get("transizione", "bande" if motore == "grafica" else None),
                          "grafiche": motore == "grafica", "anteprima": os.path.exists(anteprima),
                          "diviso": st.get("layout") == "diviso",
                          "di_serie": di_serie,
                          "momenti": [{"chiave": m, "titolo": MOMENTI[m][0], "quando": MOMENTI[m][1],
                                       "categorie": MOMENTI[m][2]} for m in momenti]})
            font = os.path.join(cart, k, "font", "Archivo.ttf")
            if os.path.exists(font):
                file.setdefault("font-titoli", font)

    # i sottotitoli disegnati dal vivo sul telefono della pagina: css e la riga di esempio, come nel reel vero.
    # Il colore del brand è un segnaposto che la pagina sostituisce con quello scelto.
    campione = [{"testo": t, "da": i * 0.4, "a": i * 0.4 + 0.35} for i, t in enumerate("ti faccio vedere come cambia".split())]
    sott = []
    for k, s in sottotitoli.CATALOGO.items():
        try:
            # le parole come le dici: il maiuscolo lo mette la pagina (così si può cambiare dal vivo)
            css, corpo, _, fonti = sottotitoli.parti(k, campione, {"vedere"} if s.get("base") else {"cambia"}, 1180, [], {"accento": "#A1C0E5", "accento_luce": "#A1C0E6"},
                                                     {"maiuscolo": "no"})
            css = css.replace(".st{text-transform:none}", "")
            for f in fonti:
                file["font/" + f] = os.path.join(STUDIO, "font", f)
            # due righe come in un reel vero: il primo pezzo della frase e quello con la parola chiave, una sotto l'altra
            prima = corpo[0] if corpo else ""
            chiave = next((c for c in corpo if 'class="w k"' in c), "")
            # sul petto, sotto la bocca: un pezzo solo a 1270, due pezzi uno sopra l'altro intorno a 1270
            if s.get("base"):   # gli stili base: un pezzo solo, quello con la parola importante
                riga = (chiave or prima).replace("top:1180px", "top:1270px")
            elif chiave and chiave != prima:
                riga = prima.replace("top:1180px", "top:1205px") + chiave.replace("top:1180px", "top:1345px")
            else:
                riga = prima.replace("top:1180px", "top:1270px")
            vivo = {"css": css.replace("url('assets/", "url('/file/font/"), "html": riga}
        except Exception:   # uno stile che non si disegna: resta solo l'anteprima video
            vivo = None
        p = os.path.join(STUDIO, "sottotitoli", "anteprime", k + ".mp4")
        if os.path.exists(p):
            file["sott-" + k] = p
        if os.path.exists(p[:-4] + ".jpg"):
            file["sott-" + k + "-jpg"] = p[:-4] + ".jpg"
        sott.append({"chiave": k, "nome": s["nome"], "per": s["per"], "descrizione": s["descrizione"],
                     "anteprima": os.path.exists(p), "vivo": vivo, "maiuscolo": bool(s.get("maiuscolo")), "modo": s["modo"],
                     "riquadro": "background:rgba(10,10,12" in s["css"] or "/*riq*/" in s["css"],
                     "base": bool(s.get("base")), "due": s.get("due_righe") == "sotto",
                     "k_fondo": bool(re.search(r"\.st \.k\{[^}]*background", s["css"]))})
    rit = ritocchi.per_la_pagina()
    for f in rit["font"]:
        file["font/" + f["file"]] = os.path.join(STUDIO, "font", f["file"])
    try:
        profilo = leggi(os.path.join(DATI, "profilo.json"))
    except (OSError, ValueError):
        profilo = {}

    eff = []
    for k, e in effetti.CATALOGO.items():
        if k in effetti.NASCOSTI:   # doppioni: nella pagina c'è solo la versione uguale al Creator Studio
            continue
        p = os.path.join(STUDIO, "effetti", "anteprime", k + ".mp4")
        if os.path.exists(p):
            file["eff-" + k] = p
        if os.path.exists(p[:-4] + ".jpg"):
            file["eff-" + k + "-jpg"] = p[:-4] + ".jpg"
        eff.append(dict(e, chiave=k, anteprima=os.path.exists(p)))

    looks = []
    for k, (nome, per, _, _, _) in colore.LOOK.items():
        p = os.path.join(STUDIO, "colore", "anteprime", k + ".jpg")
        if os.path.exists(p):
            file["look-" + k] = p
        looks.append({"chiave": k, "nome": nome, "per": per, "anteprima": os.path.exists(p)})

    # le scelte salvate l'ultima volta, rimesse come id
    per_percorso = {os.path.realpath(p): h for h, p in file.items()}
    scelte = None
    try:
        sc = leggi(SCELTE)
        scelte = {"strada": sc.get("strada", "pronto"), "stile": sc.get("stile"),
                  "suoni": {m: ("" if v == "" else per_percorso.get(os.path.realpath(v)))
                            for m, v in sc.get("suoni", {}).items()},
                  "sottotitoli": sc.get("sottotitoli"), "effetti": sc.get("effetti"), "colore": sc.get("colore"), "velocita": sc.get("velocita"),
                  "transizione": sc.get("transizione"), "diviso": sc.get("diviso"),
                  **{k: sc[k] for k in ("modello", "accento", "chiusura", "parola", "durata", "punti", "testo_fisso", "note",
                                         "titoli", "sott", "fisso") if k in sc},
                  "musica": "nessuna" if sc.get("musica") == "nessuna" else per_percorso.get(os.path.realpath(sc["musica"]))
                  if sc.get("musica") else None}
    except (OSError, ValueError):
        pass
    transizioni = {}
    for k in ("sfumatura", "bande", "taglio"):
        p = os.path.join(STUDIO, "transizioni", "anteprime", k + ".mp4")
        if os.path.exists(p):
            file["tr-" + k] = p
            if os.path.exists(p[:-4] + ".jpg"):
                file["tr-" + k + "-jpg"] = p[:-4] + ".jpg"
        transizioni[k] = os.path.exists(p)
    tel = os.path.join(STUDIO, "pagina", "telefono.mp4")   # il video di esempio del telefono, uguale per tutti
    if os.path.exists(tel):
        file["telefono"] = tel
        if os.path.exists(tel[:-4] + ".jpg"):
            file["telefono-jpg"] = tel[:-4] + ".jpg"
    return {"ritocchi": rit, "brand": profilo.get("colore"), "parola_brand": profilo.get("parola"), "telefono": os.path.exists(tel), "gruppi": effetti.GRUPPI, "stili": stili, "suoni": suoni, "sottotitoli": sott, "effetti": eff, "colori": looks, "transizioni": transizioni,
            "scelte": scelte, "slot": leggi(SLOT) if os.path.exists(SLOT) else [None, None, None]}, file


import re  # noqa: E402

SLOT = os.path.join(DATI, "stili-salvati.json")
CHIUSURE = ("commenta", "segui", "clicca", "niente")


def extra(corpo):
    """Le scelte in più della pagina (come le usa Claude nel piano): colore del brand, chiusura, durata, effetti in punti
    precisi ("quando dico"), testo fisso e note. Solo valori puliti."""
    out = {}
    if corpo.get("modello") in ("pulito", "glow", "scene", "impact", "diviso", "ads", "animato"):
        out["modello"] = corpo["modello"]
    acc = str(corpo.get("accento") or "").strip()
    if re.fullmatch(r"#?[0-9A-Fa-f]{6}", acc):
        out["accento"] = "#" + acc.lstrip("#").upper()
    if corpo.get("chiusura") in CHIUSURE:
        out["chiusura"] = corpo["chiusura"]
        parola = re.sub(r"[^A-Za-zÀ-ÿ0-9]", "", str(corpo.get("parola") or ""))[:20]
        if parola:
            out["parola"] = parola.upper()
    try:
        d = int(corpo.get("durata") or 0)
        if 15 <= d <= 180:
            out["durata"] = d
    except (TypeError, ValueError):
        pass
    punti = []
    for r in (corpo.get("punti") or [])[:12]:
        quando, eff = str(r.get("quando") or "").strip()[:120], str(r.get("effetto") or "").strip()
        if quando and eff in effetti.CATALOGO:
            punti.append({"quando": quando, "effetto": eff, "testo": str(r.get("testo") or "").strip()[:60]})
    if punti:
        out["punti"] = punti
    fisso = str(corpo.get("testo_fisso") or "").strip()[:60]
    if fisso:
        out["testo_fisso"] = fisso
    note = str(corpo.get("note") or "").strip()[:1500]
    if note:
        out["note"] = note
    # font e lettere di titoli e sottotitoli (ritocchi.py), colori del testo fisso: solo valori conosciuti
    col = lambda v: "#" + v.lstrip("#").upper() if isinstance(v, str) and re.fullmatch(r"#?[0-9A-Fa-f]{6}", v) else None
    t = corpo.get("titoli") or {}
    titoli = {"font": t.get("font") if t.get("font") in ritocchi.FONT else None,
              "grassetto": t.get("grassetto") if t.get("grassetto") in (True, False) else None,
              "corsivo": t.get("corsivo") is True,
              "maiuscolo": t.get("maiuscolo") if t.get("maiuscolo") in ("su", "giu") else None,
              "ombra": t.get("ombra") if t.get("ombra") in ritocchi.OMBRE else None}
    try:
        g = int(t.get("grandezza") or 100)
        titoli["grandezza"] = max(70, min(140, g))
    except (TypeError, ValueError):
        titoli["grandezza"] = 100
    titoli = {k: v for k, v in titoli.items() if v not in (None, False) and not (k == "grandezza" and v == 100)}
    if titoli:
        out["titoli"] = titoli
    v = corpo.get("sott") or {}
    sott = {"font": v.get("font") if v.get("font") in ritocchi.FONT else None,
            "font_k": v.get("font_k") if v.get("font_k") in ritocchi.FONT else None,
            "grassetto": v.get("grassetto") if v.get("grassetto") in (True, False) else None,
            "corsivo": v.get("corsivo") is True,
            "maiuscolo": v.get("maiuscolo") if v.get("maiuscolo") in ("su", "giu", "no") else None,
            "ombra": v.get("ombra") if v.get("ombra") in ritocchi.OMBRE else None,
            "testo": col(v.get("testo")), "evidenza": col(v.get("evidenza")), "riquadro": col(v.get("riquadro"))}
    sott = {k: x for k, x in sott.items() if x not in (None, False)}
    if sott:
        out["sott"] = sott
    f = corpo.get("fisso") or {}
    fisso = {"testo": col(f.get("testo")), "sfondo": "nessuno" if f.get("sfondo") == "nessuno" else col(f.get("sfondo"))}
    fisso = {k: x for k, x in fisso.items() if x}
    if fisso and out.get("testo_fisso"):
        out["fisso"] = fisso
    return out


def profilo_per_la_pagina():
    pr = leggi(PROFILO) if os.path.exists(PROFILO) else {}
    c = lambda k: bool(pr.get(k)) and os.path.isfile(os.path.join(DATI, os.path.basename(pr[k])))
    return {"colore": pr.get("colore"), "nome": pr.get("nome", ""), "sotto": pr.get("sotto", ""), "parola": pr.get("parola", ""),
            "parole": pr.get("parole") or [], "ha_logo": c("logo"), "ha_foto": c("foto"),
            "telefono": os.path.exists(os.path.join(STUDIO, "pagina", "telefono.jpg"))}


def salva_brand(corpo):
    """Le risposte della pagina "Il tuo brand" dentro DATI/profilo.json (quello che c'era e non si tocca resta).
    Logo e foto arrivano come immagini già rimpicciolite dalla pagina; la foto vecchia non si cancella: si rinomina."""
    import base64
    acc = str(corpo.get("colore") or "").strip()
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", acc):
        return None
    pr = leggi(PROFILO) if os.path.exists(PROFILO) else {}
    pr["colore"] = acc.upper()
    pr["nome"] = re.sub(r"[^A-Za-z0-9._]", "", str(corpo.get("nome") or ""))[:40]
    pr["sotto"] = str(corpo.get("sotto") or "").strip()[:50]
    pr["parola"] = re.sub(r"[^A-Za-zÀ-ÿ0-9]", "", str(corpo.get("parola") or ""))[:20].upper()
    pr["parole"] = [x for x in (re.sub(r"[^\w .'&-]", "", w).strip()[:40] for w in str(corpo.get("parole") or "").split(",")) if x][:30]
    for chiave, file, inizio in (("logo", "logo.png", "data:image/png;base64,"), ("foto", "profilo.jpg", "data:image/jpeg;base64,")):
        d = corpo.get(chiave)
        if isinstance(d, str) and d.startswith(inizio) and len(d) < 6_000_000:
            dest = os.path.join(DATI, file)
            if os.path.exists(dest):
                os.replace(dest, dest[:-4] + "-prima" + dest[-4:])
            with open(dest, "wb") as f:
                f.write(base64.b64decode(d[len(inizio):]))
            pr[chiave] = file
    os.makedirs(DATI, exist_ok=True)
    scrivi(PROFILO, pr)
    return pr


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
        if percorso in ("/", "/effetti", "/brand"):
            with open({"/": PAGINA, "/effetti": PAGINA_EFFETTI, "/brand": PAGINA_BRAND}[percorso], "rb") as f:
                return self._manda(200, f.read(), "text/html; charset=utf-8")
        if percorso == "/dati":
            Pagina.dati, Pagina.file = raccogli()
            return self._manda(200, json.dumps(Pagina.dati, ensure_ascii=False).encode())
        if percorso == "/profilo":
            return self._manda(200, json.dumps(profilo_per_la_pagina(), ensure_ascii=False).encode())
        if percorso in ("/file/logo", "/file/foto"):
            pr = leggi(PROFILO) if os.path.exists(PROFILO) else {}
            p = os.path.join(DATI, os.path.basename(pr.get(percorso[6:]) or "-"))
            if os.path.isfile(p):
                with open(p, "rb") as f:
                    return self._manda(200, f.read(), TIPI.get(os.path.splitext(p)[1].lower(), "application/octet-stream"))
            return self._manda(404, b"{}")
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
        if self.path == "/salva-brand":
            pr = salva_brand(corpo)
            if pr is None:
                return self._manda(400, b"{}")
            print(f"BRAND SALVATO colore={pr['colore']} nome={pr.get('nome') or '-'} parola={pr.get('parola') or '-'} "
                  f"parole={', '.join(pr.get('parole') or []) or '-'} logo={'si' if pr.get('logo') else 'no'} foto={'si' if pr.get('foto') else 'no'}", flush=True)
            return self._manda(200, b"{}")
        if self.path == "/salva-effetti":   # solo gli effetti accesi; le altre scelte restano come sono
            accesi = [k for k in (corpo.get("effetti") or []) if k in effetti.CATALOGO]
            sc = leggi(SCELTE) if os.path.exists(SCELTE) else {}
            sc["effetti"] = accesi
            sc["aggiornato"] = datetime.datetime.now().isoformat(timespec="seconds")
            scrivi(SCELTE, sc)
            print(f"EFFETTI SALVATI {len(accesi)}: {', '.join(accesi)}", flush=True)
            return self._manda(200, b"{}")
        if self.path == "/slot":   # i 3 stili salvati: {"n": 0-2, "nome": ..., "scelte": {...}} oppure "scelte": null per svuotare
            slot = leggi(SLOT) if os.path.exists(SLOT) else [None, None, None]
            n = corpo.get("n")
            if n not in (0, 1, 2):
                return self._manda(400, b"{}")
            slot[n] = {"nome": str(corpo.get("nome") or f"Stile {n + 1}")[:30], "scelte": corpo["scelte"]} if corpo.get("scelte") else None
            scrivi(SLOT, slot)
            return self._manda(200, json.dumps(slot).encode())
        if self.path == "/salva":
            stili = {s["chiave"]: s for s in Pagina.dati["stili"]}
            st = stili.get(corpo.get("stile"))   # il modello è facoltativo: il look vale per tutti gli stili
            di_serie = st["di_serie"] if st else {}
            suoni = {}
            for m, h in (corpo.get("suoni") or {}).items() if st else []:
                if h == "":
                    suoni[m] = ""
                elif h in Pagina.file and h != di_serie.get(m):
                    suoni[m] = Pagina.file[h]
            musica = corpo.get("musica")
            if musica and musica != "nessuna":
                musica = Pagina.file.get(musica) if musica != di_serie.get("musica") else None
            sott = corpo.get("sottotitoli")
            if sott not in sottotitoli.CATALOGO or sott == di_serie.get("sottotitoli"):
                sott = None  # quelli dello stile
            look = corpo.get("colore") if corpo.get("colore") in colore.LOOK and corpo.get("colore") != "originale" else None
            vel = corpo.get("velocita") if corpo.get("velocita") in (1, 1.2) else None  # None = di serie (comune.VELOCITA)
            prima = leggi(SCELTE) if os.path.exists(SCELTE) else {}
            scrivi(SCELTE, {"strada": "crea", "stile": st["chiave"] if st else None, "colore": look, "velocita": vel,
                            "sottotitoli": sott, "effetti": prima.get("effetti"),   # gli effetti li salva la pagina Effetti
                            "suoni": suoni,
                            "musica": musica, **extra(corpo),
                            "aggiornato": datetime.datetime.now().isoformat(timespec="seconds")})
            e = extra(corpo)
            print(f"SCELTE SALVATE modello={st['chiave'] if st else 'nessuno'} look={look or 'naturale'} sottotitoli={sott or 'dello stile'} "
                  f"titoli={e.get('titoli', 'dello stile')} ritocchi sottotitoli={e.get('sott', 'nessuno')} "
                  f"musica={'nessuna' if musica == 'nessuna' else ('cambiata' if musica else 'di serie')} velocita={vel or 'di serie'}", flush=True)
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
