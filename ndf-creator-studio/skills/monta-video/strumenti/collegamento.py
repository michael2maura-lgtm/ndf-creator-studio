"""Il collegamento alle cartelle del cliente sulla Scrivania, perché le trovi senza cercarle.

    PY collegamento.py          lo fa, una volta sola (se il cliente poi lo toglie, non torna da solo)
    PY collegamento.py --rifai  lo rifà anche se era già stato fatto (il cliente dice "rimettimi le cartelle sulla Scrivania")

Le cartelle vere restano dove sono (di serie ~/NDF Creator Studio, fuori da iCloud e OneDrive): sulla Scrivania va solo
un collegamento, che non pesa niente e non sposta i video. Se le due cartelle hanno la stessa cartella sopra, un
collegamento solo a quella ("NDF Creator Studio - Video"); se no, uno per cartella.
Non cancella e non sovrascrive mai un file del cliente con lo stesso nome. Se non riesce, non ferma niente.
Righe:  COLLEGAMENTO <sulla Scrivania> -> <cartella>   oppure   COLLEGAMENTO GIA FATTO   oppure   COLLEGAMENTO NON RIUSCITO · <perché>
Solo libreria standard.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import cartelle  # noqa: E402

SEGNO = os.path.join(cartelle.CASA, "collegamento-fatto.txt")
NOME = "NDF Creator Studio - Video"


def scrivania():
    from icona import scrivania as s   # la stessa Scrivania dell'icona (su Windows anche quella dentro OneDrive)
    return s()


def da_collegare():
    """[(nome sulla Scrivania, cartella vera)]"""
    clip, finiti = cartelle.cartella_clip(), cartelle.cartella_finiti()
    sopra = os.path.dirname(os.path.abspath(clip))
    if sopra == os.path.dirname(os.path.abspath(finiti)) and sopra != os.path.expanduser("~"):
        return [(NOME, sopra)]
    return [("NDF - " + os.path.basename(clip.rstrip("/\\")), clip),
            ("NDF - " + os.path.basename(finiti.rstrip("/\\")), finiti)]


def gia_nostro(link, cart):
    """Il nome sulla Scrivania è già un nostro collegamento a quella cartella (si può rifare senza toccare niente)?"""
    if cartelle.WIN:
        return False   # un .lnk non si legge con la libreria standard: lo riscrive WScript.Shell, che è sicuro
    return os.path.islink(link) and os.path.realpath(link) == os.path.realpath(cart)


def collega(link_senza_est, cart, rifai=False):
    if cartelle.WIN:
        link = link_senza_est + ".lnk"
        if os.path.exists(link) and not (os.path.exists(SEGNO) or rifai):
            return link, "c'è già un file con questo nome"
        ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{link.replace(chr(39), chr(39) * 2)}');"
              f"$s.TargetPath='{cart.replace(chr(39), chr(39) * 2)}';$s.Save()")
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
        return link, ("" if r.returncode == 0 and os.path.exists(link) else (r.stderr or "PowerShell")[-120:].strip())
    link = link_senza_est
    if os.path.lexists(link):
        if gia_nostro(link, cart):
            return link, ""
        if rifai and os.path.islink(link):   # un nostro collegamento vecchio (le cartelle sono cambiate): solo il link, mai la cartella
            os.remove(link)
            os.symlink(cart, link)
            return link, ""
        return link, "c'è già un file con questo nome"
    os.symlink(cart, link)   # nel Finder è una cartella con la freccina: doppio clic e si apre la cartella vera
    return link, ""


def main(rifai=False):
    rifai = rifai or "--rifai" in sys.argv
    if os.path.exists(SEGNO) and not rifai:
        print("COLLEGAMENTO GIA FATTO")
        return 0
    if not (cartelle.MAC or cartelle.WIN):
        print("COLLEGAMENTO NON RIUSCITO · solo Mac e Windows")
        return 1
    dove, fatti, errori = scrivania(), [], []
    nuovi = da_collegare()
    if rifai and os.path.exists(SEGNO):   # le cartelle sono cambiate: via i nostri collegamenti vecchi (solo i collegamenti)
        nomi = {os.path.join(dove, n) for n, _ in nuovi} | {os.path.join(dove, n) + ".lnk" for n, _ in nuovi}
        with open(SEGNO, encoding="utf-8") as f:
            vecchi = f.read().split("\n")
        for vecchio in vecchi:
            if vecchio and vecchio not in nomi and (os.path.islink(vecchio) or vecchio.endswith(".lnk")):
                try:
                    os.remove(vecchio)
                except OSError:
                    pass
    for nome, cart in nuovi:
        try:
            os.makedirs(cart, exist_ok=True)
            link, errore = collega(os.path.join(dove, nome), cart, rifai)
        except Exception as e:   # mai fermare lo studio per un collegamento
            link, errore = os.path.join(dove, nome), f"{type(e).__name__}: {e}"
        if errore:
            errori.append(f"{os.path.basename(link)}: {errore}")
        else:
            fatti.append(link)
            print(f"COLLEGAMENTO {link} -> {cart}")
    occupati = [e for e in errori if e.endswith("c'è già un file con questo nome")]
    if fatti or occupati == errori:   # fatto, o il nome è di un file del cliente: non riprovare a ogni controllo
        os.makedirs(cartelle.CASA, exist_ok=True)
        with open(SEGNO, "w", encoding="utf-8") as f:
            f.write("\n".join(fatti) + "\n")
    if not errori:
        return 0
    print("COLLEGAMENTO NON RIUSCITO · " + "; ".join(errori))
    return 0 if occupati == errori else 1


if __name__ == "__main__":
    sys.exit(main())
