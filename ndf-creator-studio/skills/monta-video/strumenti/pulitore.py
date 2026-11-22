"""DeepFilterNet: pulitore della voce gratuito (licenza MIT/Apache, si può rivendere), lavora sul computer, senza
internet. Scelto da Michael il 22/11/2026 ascoltando 4 versioni dello stesso girato. Un programma solo, circa 28 MB.
Solo libreria standard e nessun effetto all'import: lo usano sia installa.py sia taglia.py."""
import os
import platform
import shutil
import subprocess
import urllib.request

VERSIONE = "0.5.6"
_BIN = os.path.join(os.path.expanduser("~"), ".studio-video", "bin")
_FILE = {("Darwin", "arm64"): "aarch64-apple-darwin", ("Darwin", "x86_64"): "x86_64-apple-darwin",
         ("Windows", "AMD64"): "x86_64-pc-windows-msvc.exe", ("Windows", "x86_64"): "x86_64-pc-windows-msvc.exe"}


def deepfilter():
    """Dove sta DeepFilterNet; se manca lo scarica una volta (anche per chi aveva già lo studio). None se non si può:
    allora lo studio usa la pulizia di prima, senza fermarsi."""
    win = platform.system() == "Windows"
    dest = os.path.join(_BIN, "deep-filter.exe" if win else "deep-filter")
    if os.path.exists(dest):
        return dest
    nome = _FILE.get((platform.system(), platform.machine()))
    if not nome:
        return None
    url = f"https://github.com/Rikorose/DeepFilterNet/releases/download/v{VERSIONE}/deep-filter-{VERSIONE}-{nome}"
    tmp = dest + ".parziale"
    try:
        os.makedirs(_BIN, exist_ok=True)
        with urllib.request.urlopen(url, timeout=180) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        if os.path.getsize(tmp) < 5_000_000:   # una pagina d'errore, non il programma
            raise OSError("download incompleto")
        if not win:
            os.chmod(tmp, 0o755)
            subprocess.run(["xattr", "-c", tmp], capture_output=True)
        os.replace(tmp, dest)
        return dest
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return None


def pulisci(entrata_wav, uscita_wav):
    """Pulisce un wav (48 kHz) con DeepFilterNet. True se è andata, False se si deve usare la pulizia di prima."""
    df = deepfilter()
    if not df:
        return False
    cartella = os.path.join(os.path.dirname(uscita_wav), "_deepfilter")
    os.makedirs(cartella, exist_ok=True)
    r = subprocess.run([df, "-D", "-o", cartella, entrata_wav], capture_output=True, text=True)
    fatto = os.path.join(cartella, os.path.basename(entrata_wav))
    if r.returncode != 0 or not os.path.exists(fatto):
        return False
    os.replace(fatto, uscita_wav)
    shutil.rmtree(cartella, ignore_errors=True)
    return True
