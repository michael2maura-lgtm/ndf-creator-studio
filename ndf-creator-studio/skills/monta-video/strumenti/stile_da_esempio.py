"""Crea uno stile nuovo, copiato da un reel di esempio: la cartella dello stile, pronta da riempire.

Uso:  PY strumenti/stile_da_esempio.py <nome> --base <stile> --esempio <nome dell'esempio>[,<altro esempio>...]
      --base: lo stile pronto più vicino all'esempio, da cui si parte (motore, font, suoni):
              pulito (solo sottotitoli, zoom e sfumatura), chiaro (titolo sul gancio, parole chiave, schede),
              energia (tutto sopra la testa, una trovata ogni pochi secondi), scene (clip e foto a tutto schermo
              tra una frase e l'altra). I modelli sono questi: parti sempre da uno di loro.

Scrive DATI/stili/<nome>/: la copia dello stile base (senza anteprima e registro) e uno stile.md con la scheda da
compilare, una riga per aspetto. Poi: cambia stile.json (colori, font, sottotitoli, transizione...) e stile.md con
quello che hai visto nell'esempio, monta il primo reel con "stile": "<nome>", confronta (confronta.py), correggi.
Quando l'utente approva il reel, fai l'anteprima dello stile da quel reel (anteprima.mp4 + anteprima.jpg).
"""
import argparse
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, cartella_stile, leggi, scrivi  # noqa: E402

SCHEDA = """# {titolo}

Copiato dai reel di esempio: {fonte}. Si copiano l'aspetto e la struttura, mai le immagini,
la musica, la voce, il logo, il nome o le parole di chi l'ha fatto. Partito dallo stile "{base}".
Motore: {motore}.

- Caratteri: (che tipo, peso, maiuscolo o no, grandezza, spaziatura; il carattere che usiamo e perché)
- Colori: (testo, accento, targhe, ombre, fondo, colore del video: caldo, freddo, piatto, contrastato)
- Sottotitoli: (dove stanno, quante parole, targa o no, cosa fa la parola detta, cosa fa la parola chiave)
- Movimento dei sottotitoli: (come entra ed esce una riga, cosa fa ogni parola: dalle strisce di movimento)
- Ritmo: (tagli ogni 10 secondi, quanto dura un'inquadratura, zoom, pause tenute o tolte)
- Inquadratura: (quanto è grande la persona, dove sta, cosa c'è dietro o attorno)
- Grafiche: (titoli, barre, cornici, adesivi, schede, scene: cosa, dove, quando entrano ed escono)
- Suono: (suoni sui tagli o sulle parole, quanto forti rispetto alla voce, musica sì o no)
- Da quale esempio: (con più esempi, cosa viene da quale: "sottotitoli dal primo, colori dal secondo")
- Non si è potuto rifare: (detto all'utente)

## Note fisse ({utente})
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("nome")
    p.add_argument("--base", required=True)
    p.add_argument("--esempio", required=True)
    p.add_argument("--utente", default="utente")
    a = p.parse_args()
    nome = a.nome.lower().replace(" ", "-")
    dest = os.path.join(DATI, "stili", nome)
    if os.path.exists(dest):
        sys.exit(f"Lo stile '{nome}' c'è già: scegli un altro nome.")
    shutil.copytree(cartella_stile(a.base), dest, ignore=shutil.ignore_patterns("anteprima.*", "telefono.mp4", "registro.md", "stile.md"))
    st = leggi(os.path.join(dest, "stile.json"))
    st["nome"] = "Stile " + a.nome.strip().title()
    esempi = [e.strip() for e in a.esempio.split(",") if e.strip()]
    st["descrizione"] = "Copiato da " + ("un reel che ti piace." if len(esempi) == 1 else f"{len(esempi)} reel che ti piacciono.")
    st["fonte"] = {"esempi": esempi, "base": a.base}
    st.pop("modello", None)   # è uno stile dell'utente: nella pagina sta tra "I tuoi stili", non tra i modelli
    st.pop("ordine", None)
    st.pop("nascosto", None)
    scrivi(os.path.join(dest, "stile.json"), st)
    def link(e):
        f = os.path.join(DATI, "esempi", e, "fonte.txt")
        return f"esempi/{e} ({open(f, encoding='utf-8').read().strip() if os.path.exists(f) else 'file'})"
    with open(os.path.join(dest, "stile.md"), "w", encoding="utf-8") as f:
        f.write(SCHEDA.format(titolo=st["nome"], base=a.base, utente=a.utente,
                              motore=f'strumenti/{"grafica" if st.get("motore") == "grafica" else "costruisci"}.py',
                              fonte="; ".join(link(e) for e in esempi)))
    print(f"Stile creato: {dest}. Ora compila stile.md e cambia stile.json con quello che hai visto nell'esempio.")


if __name__ == "__main__":
    main()
