"""L'icona "NDF Creator Studio" sulla scrivania: doppio clic e si apre la pagina "Scegli il tuo stile",
senza chiederlo a Claude. Apre sempre la versione più nuova dello studio installata (gli aggiornamenti valgono da soli).

    PY icona.py        crea (o rifà) l'icona sulla scrivania, su Mac e su Windows

Come funziona: l'icona lancia apri_pagina.py (nella casa dello studio, vedi cartelle.py) con il Python dello studio; quello cerca l'ultima
versione dello studio tra i plugin installati e accende la sua pagina (che si spegne da sola quando la chiudi).
"""
import os
import platform
import shutil
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from cartelle import CASA, PY  # noqa: E402
NOME = "NDF Creator Studio"
VERSIONE_ICONA = "2"   # si alza quando cambia il modo di fare l'icona: il controllo la rifà da solo (2 = senza pythonw.exe se manca)

APRI = r'''# Scritto da icona.py: apre la pagina dello studio dalla versione più nuova installata.
import glob, os, re, subprocess, sys
casa = os.path.expanduser("~")
cart = glob.glob(os.path.join(casa, ".claude", "plugins", "cache", "*", "ndf-creator-studio", "*", "skills", "monta-video"))
def ver(p):
    v = os.path.basename(os.path.dirname(os.path.dirname(p)))
    return [int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", v)]
cart = sorted(cart, key=ver)
studio = cart[-1] if cart else %r
subprocess.Popen([sys.executable, os.path.join(studio, "strumenti", "scegli.py")], cwd=studio)
'''


PNG = os.path.join(os.path.dirname(QUI), "pagina", "icona.png")   # il logo dell'icona, 1024 px


def icona_mac(app):
    """Mette il logo (pagina/icona.png) sull'app: tutte le misure in un .icns al posto dell'icona di serie."""
    if not os.path.exists(PNG):
        return
    tmp = os.path.join(CASA, "icona.iconset")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    for n in (16, 32, 128, 256, 512):
        for k, suf in ((1, ""), (2, "@2x")):
            subprocess.run(["sips", "-z", str(n * k), str(n * k), PNG, "--out", os.path.join(tmp, f"icon_{n}x{n}{suf}.png")],
                           check=True, capture_output=True)
    subprocess.run(["iconutil", "-c", "icns", tmp, "-o", os.path.join(app, "Contents", "Resources", "applet.icns")], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    # le versioni nuove del Mac prendono l'icona da Assets.car: lo togliamo, così vale applet.icns
    car = os.path.join(app, "Contents", "Resources", "Assets.car")
    if os.path.exists(car):
        os.remove(car)
    subprocess.run(["/usr/libexec/PlistBuddy", "-c", "Delete :CFBundleIconName", os.path.join(app, "Contents", "Info.plist")],
                   check=False, capture_output=True)
    subprocess.run(["xattr", "-cr", app], check=False)
    subprocess.run(["codesign", "--force", "--deep", "-s", "-", app], check=False, capture_output=True)   # firma di nuovo
    subprocess.run(["touch", app], check=False)   # il Finder rilegge l'icona


def scrivania():
    casa = os.path.expanduser("~")
    if platform.system() == "Windows":   # la scrivania vera (spesso dentro OneDrive): la chiediamo a Windows
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
                               capture_output=True, text=True, timeout=20)
            p = r.stdout.strip()
            if p and os.path.isdir(p):
                return p
        except Exception:
            pass
    for p in (os.path.join(casa, "Desktop"), os.path.join(casa, "OneDrive", "Desktop"), os.path.join(casa, "Scrivania")):
        if os.path.isdir(p):
            return p
    return casa


def dove_sta():
    """Il percorso dell'icona sulla scrivania, se c'è (None se manca)."""
    dove = scrivania()
    for est in (".app", ".lnk", ".bat"):
        if os.path.exists(os.path.join(dove, NOME + est)):
            return os.path.join(dove, NOME + est)
    return None


def main():
    segno = os.path.join(CASA, "icona-fatta.txt")
    if "--c-e" in sys.argv:   # solo il controllo: esce con 0 se l'icona c'è ed è fatta da questa versione dell'icona
        fatta = os.path.exists(segno) and open(segno, encoding="utf-8").read().strip() == VERSIONE_ICONA
        sys.exit(0 if dove_sta() and fatta else 1)
    os.makedirs(CASA, exist_ok=True)
    apri = os.path.join(CASA, "apri_pagina.py")
    with open(apri, "w", encoding="utf-8") as f:
        f.write(APRI % os.path.dirname(QUI))
    dove = scrivania()
    if platform.system() == "Darwin":
        py = PY
        app = os.path.join(dove, NOME + ".app")
        if os.path.exists(app):
            shutil.rmtree(app)
        comando = f"'{py}' '{apri}' > /dev/null 2>&1 &"
        script = 'do shell script "' + comando.replace("\\", "\\\\").replace('"', '\\"') + '"'
        subprocess.run(["osacompile", "-o", app, "-e", script], check=True)
        icona_mac(app)
        print("ICONA", app)
    elif platform.system() == "Windows":
        # pythonw.exe (senza finestra) va solo se c'è anche nel Python dello studio: su un PC l'antivirus l'aveva tolto e
        # l'icona dava "No Python at ...pythonw.exe" (27/11/2026). Senza, si usa python.exe con la finestra ridotta a icona.
        pyw = os.path.join(os.path.dirname(PY), "pythonw.exe")
        base_w = os.path.join(CASA, "python", "pythonw.exe")
        stile = ""
        if not (os.path.exists(pyw) and os.path.exists(base_w)):
            pyw, stile = PY, "$s.WindowStyle=7;"
        ico = os.path.join(CASA, "icona.ico")
        try:
            from PIL import Image
            Image.open(PNG).save(ico, sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)])
        except Exception:
            ico = ""
        lnk = os.path.join(dove, NOME + ".lnk")   # collegamento con il logo (un .bat non può avere un'icona)
        ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}');$s.TargetPath='{pyw}';"
              f"$s.Arguments='\"{apri}\"';" + stile + (f"$s.IconLocation='{ico}';" if ico else "") + "$s.Save()")
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)
        if r.returncode != 0 or not os.path.exists(lnk):   # ripiego: il .bat, senza logo
            lnk = os.path.join(dove, NOME + ".bat")
            with open(lnk, "w", encoding="utf-8") as f:
                f.write(f'@echo off\r\nstart "" "{pyw}" "{apri}"\r\n')
        print("ICONA", lnk)
    if platform.system() in ("Darwin", "Windows"):
        with open(segno, "w", encoding="utf-8") as f:
            f.write(VERSIONE_ICONA)
    else:
        sys.exit("Lo studio funziona su Mac e su Windows.")


if __name__ == "__main__":
    main()
