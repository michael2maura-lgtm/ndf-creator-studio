"""Foto da Wikimedia Commons, per le cose PRECISE che su Pexels non ci sono (una pianta, un luogo, un oggetto con il suo
nome). Solo licenze sicure per un video che si vende: pubblico dominio e CC0 (nessun obbligo) e CC BY (va citato
l'autore). Scartate: CC BY-SA (chiede la stessa licenza per quello che ci costruisci sopra), GFDL, non commerciali.

    PY foto_wiki.py cerca "<cosa, meglio in inglese>" <nome>   fino a 6 candidate + foglio da guardare
    PY foto_wiki.py prendi <nome> <numero>                     tiene la candidata scelta: DATI/immagini/<nome>.jpg

cerca scrive DATI/immagini/candidati/<nome>-1.jpg ... e DATI/immagini/candidati/<nome>.jpg (il foglio: guardalo, la
foto deve mostrare proprio quella cosa). prendi scrive DATI/immagini/<nome>.jpg (1080x1920, come le foto di Pexels)
e DATI/immagini/<nome>.crediti.json; se la licenza chiede di citare l'autore, didascalia.py lo controlla da solo.
Righe:  CANDIDATA n | licenza | autore | titolo   /   FOTO <percorso> (crediti: <testo> | nessun obbligo)
"""
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comune import DATI, leggi, scrivi  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
AGENTE = "NDFCreatorStudio/1.0 (https://github.com/michael2maura-lgtm/ndf-creator-studio)"
IMMAGINI = os.path.join(DATI, "immagini")
CANDIDATI = os.path.join(IMMAGINI, "candidati")


def licenza_ok(nome):
    """(va bene, va citato l'autore) per il nome breve della licenza di Commons."""
    n = (nome or "").lower().replace("-", " ")
    if re.search(r"\b(sa|nc|nd)\b", n) or any(x in n for x in ("gfdl", "gpl", "fair use")):
        return False, False
    if "public domain" in n or n.startswith("pd") or "cc0" in n:
        return True, False
    if re.fullmatch(r"cc by \d(\.\d)?", n.strip()):
        return True, True
    return False, False


def chiedi(parametri):
    url = API + "?" + urllib.parse.urlencode(dict(parametri, format="json"))
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def pulito(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def scarica(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def cerca(cosa, nome):
    from PIL import Image, ImageDraw
    d = chiedi({"action": "query", "generator": "search", "gsrsearch": f"{cosa} filetype:bitmap", "gsrnamespace": 6,
                "gsrlimit": 40, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1200})
    pagine = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    os.makedirs(CANDIDATI, exist_ok=True)
    for f in os.listdir(CANDIDATI):
        if f.startswith(nome + "-"):
            os.remove(os.path.join(CANDIDATI, f))
    scelte = []
    for p in pagine:
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata", {})
        lic = pulito(m.get("LicenseShortName", {}).get("value"))
        ok, cita = licenza_ok(lic)
        if not ok or min(ii.get("width", 0), ii.get("height", 0)) < 700 or ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        k = len(scelte) + 1
        dest = os.path.join(CANDIDATI, f"{nome}-{k}.jpg")
        try:
            scarica(ii.get("thumburl") or ii["url"], dest + ".tmp")
            Image.open(dest + ".tmp").convert("RGB").save(dest, quality=90)
            os.remove(dest + ".tmp")
        except Exception:
            continue
        autore = pulito(m.get("Artist", {}).get("value")) or "autore sconosciuto"
        scelte.append({"n": k, "titolo": p["title"].replace("File:", ""), "licenza": lic, "cita": cita, "autore": autore,
                       "pagina": ii.get("descriptionurl", ""), "file": ii.get("url", ""), "anteprima": dest})
        print(f"CANDIDATA {k} | {lic} | {autore[:50]} | {scelte[-1]['titolo'][:60]}", flush=True)
        if len(scelte) == 6:
            break
    if not scelte:
        print("NIENTE: nessuna foto con una licenza sicura. Prova altre parole (in inglese) o Pexels.")
        return
    scrivi(os.path.join(CANDIDATI, f"{nome}.json"), scelte)
    # il foglio: le candidate con il numero e la licenza
    w, h = 300, 400
    foglio = Image.new("RGB", (w * len(scelte), h + 40), (20, 20, 22))
    dr = ImageDraw.Draw(foglio)
    for i, s in enumerate(scelte):
        im = Image.open(s["anteprima"])
        im.thumbnail((w - 10, h - 10))
        foglio.paste(im, (i * w + (w - im.width) // 2, 5 + (h - im.height) // 2))
        dr.text((i * w + 8, h + 8), f"{s['n']}  {s['licenza']}", fill=(255, 210, 80))
    foglio.save(os.path.join(CANDIDATI, f"{nome}.jpg"), quality=85)
    print(f"FOGLIO {os.path.join(CANDIDATI, nome + '.jpg')}")


def prendi(nome, n):
    from PIL import Image
    scelte = leggi(os.path.join(CANDIDATI, f"{nome}.json"))
    s = next(x for x in scelte if x["n"] == int(n))
    os.makedirs(IMMAGINI, exist_ok=True)
    grezzo = os.path.join(IMMAGINI, f"{nome}.originale")
    try:
        scarica(s["file"], grezzo)
        im = Image.open(grezzo).convert("RGB")
    except Exception:
        im = Image.open(s["anteprima"]).convert("RGB")
    finally:
        if os.path.exists(grezzo):
            os.remove(grezzo)
    # verticale 1080x1920 come le foto di Pexels (il centro, se è orizzontale)
    r = max(1080 / im.width, 1920 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - 1080) // 2, (im.height - 1920) // 2
    im.crop((x, y, x + 1080, y + 1920)).save(os.path.join(IMMAGINI, f"{nome}.jpg"), quality=92)
    testo = f"Foto: {s['autore']}, {s['licenza']}, Wikimedia Commons" if s["cita"] else ""
    scrivi(os.path.join(IMMAGINI, f"{nome}.crediti.json"), dict(s, testo=testo))
    print(f"FOTO {os.path.join(IMMAGINI, nome + '.jpg')} (crediti: {testo or 'nessun obbligo'})")


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "cerca":
        cerca(a[1], a[2])
    elif len(a) >= 3 and a[0] == "prendi":
        prendi(a[1], a[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
