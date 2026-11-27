"""Il primo avvio: le due cartelle del cliente, scelte una volta sola (SKILL.md, Passo 0 "Primo avvio").

Uso:  PY strumenti/primo_avvio.py                                    le cartelle di serie
      PY strumenti/primo_avvio.py --clip "<cartella>" --finiti "<cartella>"   altre cartelle (anche una sola)
      PY strumenti/primo_avvio.py --senza-aprire                     non aprire la cartella (il robot di prova)

Di serie, nella cartella utente:  NDF Creator Studio/1 - Clip da montare  e  NDF Creator Studio/2 - Video finiti
(fuori da Documenti e Scrivania, quindi fuori da iCloud). Le scrive in <casa>/config.json (tiene le altre voci),
le crea, mette il loro collegamento sulla Scrivania (collegamento.py) e apre la cartella delle clip. Righe:  CARTELLE <clip> | <finiti>   e   APERTA <clip>
"""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cartelle  # noqa: E402


def opzione(nome):
    return sys.argv[sys.argv.index(nome) + 1] if nome in sys.argv[:-1] else None


def apri(cart):
    try:
        if cartelle.WIN:
            os.startfile(cart)   # noqa: S606
        elif cartelle.MAC:
            subprocess.run(["open", cart], check=False)
        print(f"APERTA {cart}")
    except Exception:
        pass


def main():
    conf = cartelle.config()
    prima = (conf.get("clip"), conf.get("finiti"))
    clip = os.path.abspath(os.path.expanduser(opzione("--clip") or conf.get("clip") or cartelle.CLIP_DI_SERIE))
    finiti = os.path.abspath(os.path.expanduser(opzione("--finiti") or conf.get("finiti") or cartelle.FINITI_DI_SERIE))
    for c in (clip, finiti):
        os.makedirs(c, exist_ok=True)
    conf.update({"clip": clip, "finiti": finiti})
    conf.setdefault("primo_avvio", time.strftime("%Y-%m-%d"))
    cartelle.scrivi(cartelle.CONFIG, conf)
    print(f"CARTELLE {clip} | {finiti}")
    if not os.environ.get("NDF_STUDIO_PROVA_SENZA_ICONA"):   # prova sul Mac di Michael: la sua Scrivania non si tocca
        try:
            import collegamento
            collegamento.main(rifai=bool(prima[0]) and prima != (clip, finiti))   # il collegamento alle cartelle sulla Scrivania, perché il cliente le trovi
        except Exception:
            pass
    if "--senza-aprire" not in sys.argv:
        apri(clip)


if __name__ == "__main__":
    main()
