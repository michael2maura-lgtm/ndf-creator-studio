"""Libreria dei suoni: tutti i suoni dello studio, divisi per momento del video. La usa la pagina scegli.py.

Prende i suoni del kit (STUDIO/suoni/kit) e quelli scaricati o aggiunti dall'utente (DATI/suoni/...).
"""
import hashlib
import os

from comune import DATI, STUDIO

ESTENSIONI = (".mp3", ".wav", ".m4a")
SALTA = {"_riferimento"}  # pezzi di reel altrui usati per il confronto, non sono suoni da usare

# (titolo, a cosa serve, parole nel nome del file che lo fanno finire qui): il primo che combacia vince
MOMENTI = [
    ("Musiche", "sotto tutto il video", ["musica"]),
    ("Meme", "per attirare l'attenzione, video leggeri", ["fahh", "vine"]),
    ("Attesa", "sale prima di una cosa importante", ["riser"]),
    ("Colpi", "sulla parola forte, l'impatto", ["impatt", "impact", "boom"]),
    ("Scritte e glitch", "quando appare un titolo", ["glitch"]),
    ("Tastiera", "mentre un testo si scrive", ["tastiera", "typing", "macchina-scrivere", "key-press"]),
    ("Click e pop", "quando entra una grafica, un bottone", ["click", "pop", "interruttore", "sblocco"]),
    ("Notifiche e premi", "un traguardo, una spunta, un numero",
     ["ding", "notifica", "notification", "chime", "ping", "livello", "traguardo", "vittoria", "fanfara",
      "campanell", "sparkle", "glitter", "scintille", "luce-magica", "bacchetta", "moneta-gioco"]),
    ("Transizioni", "quando cambia la scena o c'è uno zoom",
     ["w-", "whoosh", "swish", "swoosh", "tr", "t1", "t2", "t3", "t4", "t5", "t6", "transizione"]),
    ("Oggetti e ambienti", "quando si vede o si dice quella cosa", [""]),
]


def impronta(percorso):
    with open(percorso, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def momento(cartella, nome):
    if cartella == "mixkit-whoosh":
        return "Transizioni"
    for titolo, _, parole in MOMENTI:
        if any(nome.startswith(p) if p in ("w-", "tr", "t1", "t2", "t3", "t4", "t5", "t6") else p in nome for p in parole):
            return titolo
    return MOMENTI[-1][0]


def trova():
    """[(momento, nome da dire, gruppo, percorso)], senza doppioni (stesso file = stesso suono)."""
    visti, suoni = set(), []
    sorgenti = [(os.path.join(STUDIO, "suoni", "kit"), "kit")]
    base = os.path.join(DATI, "suoni")
    for d in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if os.path.isdir(os.path.join(base, d)) and d not in SALTA:
            if d == "gruppi":
                sorgenti += [(os.path.join(base, d, g), g) for g in sorted(os.listdir(os.path.join(base, d)))
                             if os.path.isdir(os.path.join(base, d, g))]
            else:
                sorgenti.append((os.path.join(base, d), d))
    for cart, gruppo in sorgenti:
        for f in sorted(os.listdir(cart)):
            p = os.path.join(cart, f)
            if not f.lower().endswith(ESTENSIONI):
                continue
            h = impronta(p)
            if h in visti:
                continue
            visti.add(h)
            nome = os.path.splitext(f)[0]
            suoni.append((momento(gruppo, nome.lower()), nome if gruppo != "mixkit-whoosh" else f"whoosh {nome}", gruppo, p, h))
    return suoni
