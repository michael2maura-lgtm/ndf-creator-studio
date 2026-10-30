---
name: monta-video
description: Monta un reel parlato in verticale (taglio, sottotitoli italiani parola per parola, titoli, scene, suoni e musica nello stile salvato, volume per Instagram) partendo dal girato grezzo. Usala quando l'utente dice "monta questo video", "monta il reel", "edita questo video", "installa lo studio", o indica un girato da trasformare in reel.
---

# Monta video

L'utente dice "monta questo video" e riceve il reel finito. Tu fai tutti i passaggi di fila, senza chiedere conferme.
Ti fermi solo se un controllo fallisce o se una parola è dubbia (un nome, una frase che Whisper ha sentito male).
Parla semplice, frasi corte, niente nomi di file o errori tecnici.

STUDIO = la cartella di questo file. DATI = `Documenti/NDFCreatorStudio` nella cartella utente (lavori, stili,
suoni e clip di chi usa lo studio: gli aggiornamenti non li toccano). Lancia tutto fuori dalla sandbox.
PY = il Python dello studio: su Mac `~/.studio-video/venv/bin/python`, su Windows
`~/.studio-video/venv/Scripts/python.exe -X utf8`. Tutti i comandi qui sotto usano PY, mai `python3` o `python`.
NOME = nome breve del lavoro (es. `video-lunedi`); i suoi file stanno in `DATI/lavori/NOME/`.

## Passo 0, ogni volta (in silenzio se va tutto bene)
- Manca `~/.studio-video/pronto.json`, o l'utente dice "installa lo studio": chiedi il permesso una volta sola
  ("Installo alcuni programmi gratuiti nella tua cartella utente, circa 3 GB, la prima volta 10-20 minuti. Posso?").
  Poi, se `uv` non c'è, installalo: Mac `curl -LsSf https://astral.sh/uv/install.sh | sh`; Windows
  `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`. Poi
  `uv run --python 3.12 --no-project STUDIO/strumenti/installa.py` (uv è in `~/.local/bin` se non lo trova).
  Se una riga dice MANCA, rilancialo una volta; se resta, di' in una riga cosa manca.
- `PY STUDIO/strumenti/aggiornamenti.py`: se dice che c'è una versione nuova, dillo in una riga e chiedi se
  aggiornare (`/plugin update ndf-creator-studio`, poi riaprire Claude Code).
- Nessuno stile in `DATI/stili/`: prima fai l'intervista (abilità `crea-stile`), poi torna qui.

## I passaggi, sempre in quest'ordine
1. `PY STUDIO/strumenti/prepara.py "<video>" NOME --nomi "<nomi detti nel video>"`
   Leggi `trascrizione.txt` e guarda `foglio.jpg`.
2. Scrivi `tagli.json` seguendo `regole/taglio.md`, poi `PY STUDIO/strumenti/taglia.py NOME`.
3. `PY STUDIO/strumenti/parole.py NOME --nomi "..."`: confronta il testo con quello detto (regole/taglio.md).
   `PY STUDIO/strumenti/controlla_tagli.py NOME` e guarda `controllo/tagli.jpg`.
4. `PY STUDIO/strumenti/faccia.py NOME` e guarda `controllo/faccia.jpg`: il riquadro deve stare sulla faccia.
5. Leggi le ultime 5 righe di `stili/<stile>/registro.md` e scegli scene, clip e pose diverse da quelle.
   Decidi che video è. **Completo**: ogni 3-6 secondi una scena a tutto schermo di 1-3 secondi, poi si torna sulla
   persona; zoom, transizioni, suoni degli oggetti, musica. **Parlato** (spiega un concetto, annuncio semplice):
   sottotitoli, titoli e finale, niente musica. Se l'utente lo dice, vale quello.
   Scrivi `piano.json` (formato in cima a `strumenti/costruisci.py`, `scene.py`, `suoni_reel.py`, `split.py`)
   seguendo `stili/<stile>/stile.md` e `regole/suoni.md`. Scene: `testo`, `capitolo` (01 02 03), `clip` (clip vere in
   `DATI/clip/`, "x" per la X rossa), `omino` (in_piedi, spallucce, braccia_su, scrivania; "chiaro", "croce",
   "numero"), `chat`, `telefono` ("storia" o "reel"), `schema`; sopra la persona `titoli`, `liste`, `parole_chiave`.
   Ogni scena nasce da una frase detta in quel momento, con le parole dette.
   Clip vere: prima guarda quelle che ci sono in `DATI/clip/`. Se manca quella giusta, cercala sul web
   ("pexels video <cosa, in inglese> vertical"), prendi un link pexels.com/video/...-<numero>/ e scaricala con
   `PY STUDIO/strumenti/clip.py <link> <nome>`; guarda il `.jpg` che crea e usala solo se mostra davvero quello che
   si dice. Dai alla clip il nome dell'oggetto quando c'è (soldi, porta, festa, sveglia, ufficio, fabbrica,
   bollette...): così prende da sola il suo suono. Foto a tutto schermo (scena `immagine`, es. un corpo, un
   prodotto, un luogo): stesso modo, con un link pexels.com/photo/...; finiscono in `DATI/immagini/`.
   Entrate delle scene, campo "entrata": `lampo` (flash bianco all'entrata e al ritorno sulla persona: per clip e
   immagini), `scorri` (entra da destra: per passaggi numerati in fila), `carta` (morbida, sfocata: momenti calmi).
   Senza "entrata" è un taglio netto. Varia tra un video e l'altro (registro). Esempi approvati in `esempi/`:
   un racconto (omini, clip, capitoli) e una spiegazione (chat, telefono, schema, ritmo dinamico).
   Stile con `"motore": "grafica"` nel suo stile.json: il piano è diverso (motion graphics sopra la persona:
   titoli che si decodificano, targhette, parola gigante, cornice, telefono, contatore). Formato in cima a
   `strumenti/grafica.py`, quando usare cosa nello `stile.md` dello stile, esempio approvato in `esempi/grafica.json`.
   Ogni 4-8 secondi una grafica, sempre nata da una frase detta in quel momento.
6. `PY STUDIO/strumenti/costruisci.py NOME --zone`, poi `PY STUDIO/strumenti/foto.py NOME <6-8 momenti>`
   e guarda il foglio: niente nelle zone rosse, niente sulla faccia, niente righe orfane.
7. `PY STUDIO/strumenti/costruisci.py NOME` (senza zone), poi `PY STUDIO/strumenti/rendi.py NOME`.
8. `PY STUDIO/strumenti/controlla_tagli.py NOME finale/NOME-vN.mp4 --telefono`: guarda i fotogrammi del video
   FINITO e il volume. Manda all'utente la copia per il telefono.
9. `PY STUDIO/strumenti/registro.py <stile> "NOME | scene: ... | clip: ... | omini: ... | suoni: ..."` con
   quello che hai usato davvero. Di' in poche righe cosa hai fatto, se hai messo la musica e perché, e cosa deve
   ascoltare o controllare (le parole corrette a intuito, con il secondo). Tu non senti l'audio: dillo.

Stili in `DATI/stili/` (quelli dell'utente) e `STUDIO/stili/` (quelli pronti). L'utente può dire quale
("monta questo in stile X"); se non lo dice, usa quello di `DATI/scelte.json` (la pagina qui sotto), se no il suo.

## La pagina "Scegli il tuo look"
L'utente dice "scegli il look", "apri la pagina", "voglio cambiare suoni / musica", o non sa che stile usare:
lancia `PY STUDIO/strumenti/scegli.py` in sottofondo e di' in una riga che si è aperta nel browser.
Tre strade: stile pronto, replica un reel (l'utente ti manda il link in chat: lo studi con l'abilità `crea-stile`
e ne fai uno stile nuovo, che poi compare nella pagina), crea il tuo (parte da uno stile e cambia suoni e musica).
Quando scrive `SCELTE SALVATE`, di' in una riga cosa ha scelto. Le scelte le usa `costruisci.py` da solo: tu nel piano
scrivi lo stile scelto e basta. Un'anteprima di uno stile è `anteprima.mp4` (il video intero, 540 px di larghezza, con l'audio)
nella sua cartella: falla quando crei uno stile nuovo, dal primo video approvato.

## Correzioni dell'utente
Una correzione per questo video si fa nel `piano.json` o nel `tagli.json` di questo video, poi si rifà dal passaggio
che è cambiato e si crea la versione dopo (v2, v3: le vecchie restano). Tagli cambiati dopo il piano:
`regole/taglio.md` spiega come spostare il piano da solo (`rimappa.py`).
Cambiati solo suoni o musica: `costruisci.py NOME` e poi `rendi.py NOME --solo-audio` (secondi, non minuti).
Rifai un video alla volta, quello chiesto, con un solo controllo rapido: l'utente non vuole aspettare né sprecare.
Una correzione entra nello stile o nelle regole SOLO se l'utente dice "sempre" o "d'ora in poi", e con il suo ok.
