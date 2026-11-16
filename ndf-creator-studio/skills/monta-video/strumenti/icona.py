"""L'icona "NDF Creator Studio" sulla scrivania: doppio clic e si apre la pagina "Scegli il tuo stile",
senza chiederlo a Claude. Apre sempre la versione più nuova dello studio installata (gli aggiornamenti valgono da soli).

    PY icona.py        crea (o rifà) l'icona sulla scrivania, su Mac e su Windows

Come funziona: l'icona lancia ~/.studio-video/apri_pagina.py con il Python dello studio; quello cerca l'ultima
versione dello studio tra i plugin installati e accende la sua pagina (che si spegne da sola quando la chiudi).
"""
import os
import platform
import shutil
import subprocess
import sys

CASA = os.path.join(os.path.expanduser("~"), ".studio-video")
QUI = os.path.dirname(os.path.abspath(__file__))
NOME = "NDF Creator Studio"

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


def scrivania():
    casa = os.path.expanduser("~")
    for p in (os.path.join(casa, "Desktop"), os.path.join(casa, "OneDrive", "Desktop"), os.path.join(casa, "Scrivania")):
        if os.path.isdir(p):
            return p
    return casa


def main():
    os.makedirs(CASA, exist_ok=True)
    apri = os.path.join(CASA, "apri_pagina.py")
    with open(apri, "w", encoding="utf-8") as f:
        f.write(APRI % os.path.dirname(QUI))
    dove = scrivania()
    if platform.system() == "Darwin":
        py = os.path.join(CASA, "venv", "bin", "python")
        app = os.path.join(dove, NOME + ".app")
        if os.path.exists(app):
            shutil.rmtree(app)
        comando = f"'{py}' '{apri}' > /dev/null 2>&1 &"
        script = 'do shell script "' + comando.replace("\\", "\\\\").replace('"', '\\"') + '"'
        subprocess.run(["osacompile", "-o", app, "-e", script], check=True)
        print("ICONA", app)
    elif platform.system() == "Windows":
        pyw = os.path.join(CASA, "venv", "Scripts", "pythonw.exe")
        bat = os.path.join(dove, NOME + ".bat")
        with open(bat, "w", encoding="utf-8") as f:
            f.write(f'@echo off\r\nstart "" "{pyw}" "{apri}"\r\n')
        print("ICONA", bat)
    else:
        sys.exit("Lo studio funziona su Mac e su Windows.")


if __name__ == "__main__":
    main()
