"""Suoni e musica del reel: transizioni sui cambi di scena, colpi nei momenti forti, musica sotto (se serve).

Nel piano.json:  "suoni": {"transizione": true, "colpi": [1.32, 60.7], "musica": true}
  transizione: la transizione dello stile su ogni cambio di scena
  colpi: i secondi dei 2-3 momenti più forti
  musica: true solo per i video completi (regole/suoni.md)
La transizione parte da sola quando entra ogni scena a tutto schermo (mai prima, mai al ritorno: regola del vecchio kit).
"""
import os
import shutil
import subprocess

from comune import FFMPEG, trova

VOL_EFFETTI = 0.45  # circa 7 dB sotto la voce
VOL_COLPO = 0.5
VOL_MUSICA = 0.2    # nelle pause; quando la persona parla scende da sola di circa 8 dB (ducking in rendi.py)
VOL_RISALITA = 0.35
SILENZIO = 0.3      # la musica tace un attimo prima della frase chiave


def risalita(assets):
    """La parte che sale del riser (2 s, finisce di colpo), allo stesso volume degli altri effetti."""
    dest = os.path.join(assets, "risalita.wav")
    if not os.path.exists(dest):
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", "2.2", "-t", "2.0", "-i", trova("hyperframes/riser.mp3"), "-af",
                        "loudnorm=I=-16:TP=-1.5,aresample=48000", dest], check=True)
    return "assets/risalita.wav", 2.0


def frasi_chiave(piano, D):
    """Le 1-3 frasi chiave del piano ("frasi_chiave": [[da, a], ...]): risalita, silenzio, frase senza musica,
    la musica riparte con un colpo. [da, a, "netto"]: niente risalita, la musica si taglia di colpo poco prima della
    frase (come nel reel di esempio "come il 22"). Restituisce le frasi buone (da, a, netto) e il data-stop."""
    frasi = [(f[0], f[1], len(f) > 2 and f[2] == "netto") for f in piano.get("frasi_chiave", [])
             if 2.5 < f[0] < f[1] < D - 0.5]
    return frasi, ",".join(f"{da - (0.2 if netto else SILENZIO):.3f}:{a:.3f}" + (":n" if netto else "")
                           for da, a, netto in frasi)



# suoni degli oggetti, ripresi dal vocabolario del kit "Monta le tue Ads": [file in suoni/, ritardo dall'inizio, volume]
OGGETTI = {
    "soldi": [["mixkit/cassa.mp3", 0.1, 0.5], ["mixkit/monete.mp3", 0.35, 0.45]],
    "festa": [["mixkit/festa.mp3", 0.05, 0.35]],
    "persone-felici": [["mixkit/applauso.mp3", 0.1, 0.25]],
    "porta": [["mixkit/porta1.mp3", 0.1, 0.45], ["mixkit/porta2.mp3", 0.6, 0.35]],
    "sveglia": [["mixkit/tictac.mp3", 0.0, 0.4]],
    "ufficio": [["mixkit/tastiera.mp3", 0.0, 0.35]],
    "fabbrica": [["mixkit/fabbrica.mp3", 0.0, 0.35]],
    "bollette": [["mixkit/triste.mp3", 0.1, 0.4]],
    "stretta-di-mano": [["mixkit/notifica.mp3", 0.3, 0.4]],
    "cliente-computer": [["mixkit/notifica.mp3", 0.4, 0.4]],
    "relatore": [["mixkit/applauso.mp3", 0.2, 0.25]],
}
# omini: posa e cose in scena
OMINI = {"braccia_su": [["mixkit/livello.mp3", 0.1, 0.4]], "numero": [["mixkit/cassa.mp3", 0.1, 0.5], ["mixkit/monete.mp3", 0.3, 0.45]],
         "croce": [["hyperframes/error.mp3", 0.33, 0.4]], "scrivania": [["mixkit/tastiera.mp3", 0.2, 0.3]]}


def suoni_scena(s):
    """I suoni di una scena: quelli scritti nel piano ("suoni": [[file, ritardo, volume]]), altrimenti quelli
    dell'oggetto o della posa. "suoni": [] = nessun suono per quella scena."""
    if "suoni" in s:
        return s["suoni"]
    out = []
    if s["tipo"] == "clip":
        out += OGGETTI.get(s["clip"], [])
    if s["tipo"] == "omino":
        out += OMINI.get(s.get("posa"), [])
        out += [x for k in ("numero", "croce") if s.get(k) for x in OMINI[k]]
    if s["tipo"] == "telefono" and s.get("modo") != "reel":
        # una notifica per ogni domanda che arriva nella storia
        out += [["mixkit/notifica.mp3", 1.33 + i * 0.87, 0.4] for i in range(len(s.get("domande", [])))]
    if s["tipo"] == "schema":
        out += [["kit/pop.wav", p[2] - s["da"] + 0.27, 0.45] for p in s["passi"]]
    if s["tipo"] == "bianca":
        # un pop per ogni scheda che entra, una notifica per il messaggio, un colpo secco per ogni timbro
        for i, sc in enumerate(s.get("schede", [])):
            t = sc.get("t", s["da"] + 0.6 + i * 0.4) - s["da"]
            out.append(["kit/pop.wav", t, 0.4])
            if sc.get("chat"):
                out.append(["mixkit/notifica.mp3", t + 0.35, 0.35])
            if sc.get("barra"):
                out.append(["hyperframes/error.mp3", sc["barra"] - s["da"], 0.35])
        out += [["kit/boom.wav", tt - s["da"] + 0.2, 0.3] for _, tt in s.get("timbri", [])]
    return out


def prepara(piano, stile, cart_stile, reel, D):
    """Copia i suoni nella pagina del reel e restituisce i tag <audio> da metterci dentro."""
    cfg = piano.get("suoni")
    if not cfg:
        return []
    suoni = stile.get("suoni", {})
    assets = os.path.join(reel, "assets")
    tag = []

    def copia(rel, nome):
        shutil.copy2(os.path.join(cart_stile, rel), os.path.join(assets, nome))
        return f"assets/{nome}"

    def audio(id_, src, da, durata, vol):
        da = max(da, 0)
        durata = min(durata, D - da)
        if durata > 0.05:
            tag.append(f'<audio id="{id_}" src="{src}" data-start="{da:.3f}" data-media-start="0" '
                       f'data-duration="{durata:.3f}" data-volume="{vol}"></audio>')

    if cfg.get("transizione") and suoni.get("transizione"):
        scelta = suoni["transizione"]
        src = copia(scelta, "transizione" + os.path.splitext(scelta)[1])
        # come nel kit "Monta le tue Ads": un suono solo, che parte quando la scena entra; niente suono al ritorno
        for k, s in enumerate(sorted(piano.get("scene", []), key=lambda x: x["da"])):
            audio(f"tr{k}", src, s["da"], 1.2, VOL_EFFETTI)
    if suoni.get("tastiera"):
        # mentre la domanda si scrive nella chat si sente la tastiera
        src = None
        for k, s in enumerate(x for x in piano.get("scene", []) if x["tipo"] == "chat"):
            src = src or copia(suoni["tastiera"], "tastiera" + os.path.splitext(suoni["tastiera"])[1])
            fine = s["da"] + (s["a"] - s["da"]) * s.get("scrittura", 0.55)
            audio(f"ts{k}", src, s["da"] + 0.2, fine - s["da"] - 0.2, VOL_EFFETTI)
    # suoni degli oggetti nelle scene, e il "livello" per ogni parola che si somma negli elenchi
    copiati = {}

    def da_libreria(rel):
        # i file della libreria hanno volumi molto diversi (il tic tac è 20 volte più basso della cassa):
        # si portano tutti allo stesso volume, così il volume scritto nel piano vale uguale per tutti
        if rel not in copiati:
            nome = "lib-" + os.path.splitext(rel.replace("/", "-"))[0] + ".wav"
            subprocess.run([FFMPEG, "-v", "error", "-y", "-t", "3", "-i", trova(rel), "-af",
                            "loudnorm=I=-16:TP=-1.5,aresample=48000", os.path.join(assets, nome)], check=True)
            copiati[rel] = f"assets/{nome}"
        return copiati[rel]

    if cfg.get("oggetti", True):
        k = 0
        for s in piano.get("scene", []):
            for rel, rit, vol in suoni_scena(s):
                audio(f"og{k}", da_libreria(rel), s["da"] + rit, min(2.5, s["a"] - s["da"] - rit + 0.6), vol)
                k += 1
        for l in piano.get("liste", []):
            for _, t in l["voci"]:
                audio(f"og{k}", da_libreria("mixkit/livello.mp3"), t, 1.0, 0.35)
                k += 1
    if cfg.get("colpi") and suoni.get("colpo"):
        src = copia(suoni["colpo"], "colpo" + os.path.splitext(suoni["colpo"])[1])
        for k, t in enumerate(cfg["colpi"]):
            audio(f"cp{k}", src, t, 1.5, VOL_COLPO)
    if cfg.get("musica") and suoni.get("musica"):
        # la musica si ripete fino alla fine del video e sfuma nell'ultimo secondo e mezzo
        dest = os.path.join(assets, "musica.m4a")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-stream_loop", "-1", "-i", os.path.join(cart_stile, suoni["musica"]),
                        "-t", f"{D:.3f}", "-af", f"afade=t=in:d=0.8,afade=t=out:st={max(D - 1.5, 0):.3f}:d=1.5",
                        "-c:a", "aac", "-b:a", "160k", dest], check=True)
        audio("musica", "assets/musica.m4a", 0, D, VOL_MUSICA)
        frasi, stop = frasi_chiave(piano, D)
        if frasi:
            tag[-1] = tag[-1].replace("<audio ", f'<audio data-stop="{stop}" ', 1)
            src_r, dur_r = risalita(assets)
            colpo = suoni.get("colpo") and copia(suoni["colpo"], "colpo" + os.path.splitext(suoni["colpo"])[1])
            for k, (da, a, netto) in enumerate(frasi):
                if not netto:
                    audio(f"ri{k}", src_r, da - SILENZIO - dur_r, dur_r, VOL_RISALITA)
                if colpo:
                    audio(f"fc{k}", colpo, a, 1.5, VOL_COLPO)
    return tag
