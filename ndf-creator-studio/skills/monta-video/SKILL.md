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
   Clip e foto stanno di serie in una finestra arrotondata su fondo scuro (i sottotitoli continuano sopra, se la scena
   non ha "grande"); "finestra": false solo se serve il tutto schermo.
   Entrate delle scene, campo "entrata": `lampo` (flash bianco all'entrata e al ritorno sulla persona: per clip e
   immagini), `scorri` (entra da destra: per passaggi numerati in fila), `carta` (morbida, sfocata: momenti calmi).
   Senza "entrata" è un taglio netto. Varia tra un video e l'altro (registro). Esempi approvati in `esempi/`:
   un racconto (omini, clip, capitoli) e una spiegazione (chat, telefono, schema, ritmo dinamico).
   Stile con `"motore": "grafica"` nel suo stile.json: il piano è diverso (motion graphics sopra la persona:
   titoli che si decodificano, targhette, parola gigante, cornice, telefono, contatore). Formato in cima a
   `strumenti/grafica.py`, quando usare cosa nello `stile.md` dello stile, esempio approvato in `esempi/grafica.json` (Impact semplice, approvato da Michael: `esempi/impact-semplice.json`).
   Ogni 4-8 secondi una grafica, sempre nata da una frase detta in quel momento.
   Zoom: decidilo sempre tu, in ogni video, seguendo `regole/zoom.md` (l'utente non deve chiederlo).
   **Poche cose fatte bene**: una grafica alla volta, mai lampi, adesivi o pillole su ogni parola. Se un elemento non
   aiuta a capire o a sentire, toglilo.
6. `PY STUDIO/strumenti/costruisci.py NOME --zone`, poi `PY STUDIO/strumenti/foto.py NOME <6-8 momenti>`
   e guarda il foglio: niente nelle zone rosse, niente sulla faccia, niente righe orfane.
7. `PY STUDIO/strumenti/costruisci.py NOME` (senza zone), poi `PY STUDIO/strumenti/rendi.py NOME`.
8. `PY STUDIO/strumenti/controlla_tagli.py NOME finale/NOME-vN.mp4 --telefono`: guarda i fotogrammi del video
   FINITO e il volume. Manda all'utente la copia per il telefono.
9. `PY STUDIO/strumenti/registro.py <stile> "NOME | scene: ... | clip: ... | omini: ... | suoni: ..."` con
   quello che hai usato davvero. Di' in poche righe cosa hai fatto, se hai messo la musica e perché, e cosa deve
   ascoltare o controllare (le parole corrette a intuito, con il secondo). Tu non senti l'audio: dillo.

Stili pronti, tre: **Scene** (tu che parli e tra una frase e l'altra la scena giusta: clip e foto nella finestra,
omini, lavagna, scene animate di Racconto), **Impact** (`ndf-grafica`, lo stile Notech dei reel di esempio 01 e 04: grafiche sopra la persona; poche per un video
semplice, con la sfumatura come passaggio, tante per un video d'impatto) e **Diviso** (pannello in alto, persona sotto).
NDF, Racconto, Linee, Luce e Ads sono uniti in Scene e Impact: la pagina non li mostra ("nascosto": true) ma si
usano ancora per nome. Ads non è uno stile: se il video è per le ads, finale "CLICCA QUI SOTTO", mai "commenta".
Stili in `DATI/stili/` (quelli dell'utente) e `STUDIO/stili/` (quelli pronti). L'utente può dire quale
("monta questo in stile X"); se non lo dice, usa quello di `DATI/scelte.json` (la pagina qui sotto), se no il suo.

## La pagina "Scegli il tuo look"
L'utente dice "scegli il look", "apri la pagina", "voglio cambiare suoni / musica", o non sa che stile usare:
lancia `PY STUDIO/strumenti/scegli.py` in sottofondo e di' in una riga che si è aperta nel browser.
Tre strade: stile pronto, replica un reel (l'utente ti manda il link in chat: lo studi con l'abilità `crea-stile`
e ne fai uno stile nuovo, che poi compare nella pagina), crea il tuo (parte da uno stile e cambia suoni e musica).
Quando scrive `SCELTE SALVATE`, di' in una riga cosa ha scelto. I 20 sottotitoli a scelta stanno in
`strumenti/sottotitoli.py`; le loro anteprime le rifà `anteprima_sottotitoli.py` (solo se ne cambi o aggiungi uno).
Colore del girato: `strumenti/colore.py` (6 look, la pelle resta naturale). Quello scelto nella pagina lo applica
`costruisci.py` da solo; per un video solo scrivi "colore" nel piano. Se l'utente chiede "che colore ci sta?",
`PY STUDIO/strumenti/colore.py proposte NOME` e mostragli `controllo/look.jpg`.
Effetti (motion graphics del motore grafica): catalogo in `strumenti/effetti.py`. Come nel Creator Studio, ogni
stile ha i suoi pochi effetti accesi (stile.json "effetti"); nella pagina l'utente accende quelli che gli piacciono
(scelte.json "effetti"). Nel piano usa SOLO gli effetti accesi, e solo dove c'entrano con la frase detta (lo stile.md
dice quando): grafica.py salta gli altri con una NOTA. L'utente non sceglie niente reel per reel. Le scelte le usa `costruisci.py` da solo: tu nel piano
scrivi lo stile scelto e basta. Un'anteprima di uno stile è `anteprima.mp4` (il video intero, 540 px di larghezza, con l'audio) più la sua copertina
`anteprima.jpg` (un fotogramma con la faccia ferma e una scritta, mai una mano davanti)
nella sua cartella: falla quando crei uno stile nuovo, dal primo video approvato.
Velocità: ogni reel finito va il 12% più veloce (comune.VELOCITA); nella pagina l'utente sceglie Normale, Svelta o
Veloce, e `rendi.py` la usa da solo. Per un reel diverso: "velocita" nel piano (1 = com'è girato).
Transizioni (stili del motore grafica): nel piano scrivi "transizioni": [secondi], SOLO sui cambi di argomento (2-3 in
un minuto, nella pausa prima della parte nuova). Il tipo (sfumatura di luce, bande, taglio netto) è quello dello stile
o quello scelto nella pagina: tu scrivi solo i secondi.

## Copiare lo stile di un reel ("replica questo reel", "voglio uno stile come questo")
L'utente manda un link, un file o descrive un aspetto: quello è il brief. Non lo avvicini allo stile più simile che
c'è: ne rifai l'aspetto, movimenti compresi, sul video dell'utente. Si copiano l'ASPETTO e la STRUTTURA (tipo di
carattere, maiuscolo, colori, targhe, posizioni, ritmo dei sottotitoli, movimenti, ritmo dei tagli, tipo di grafiche,
carattere dei suoni). Mai le immagini, la musica, la voce, il logo, il nome o le parole di chi l'ha fatto, e mai dire
che il risultato è fatto con lui. Caratteri: quello gratuito più vicino (Google Fonts); di' quale usi al posto
dell'originale. Mai un font a pagamento.
1. **Prendi e studia ogni esempio.** `PY STUDIO/strumenti/prendi_esempio.py "<link o file>" [altri] --nome <nome>`,
   poi `PY STUDIO/strumenti/studia.py <nome>` per ognuno. Se dice SERVE LOGIN chiedi il permesso di usare l'accesso del
   browser (le parole sono nello strumento); solo con un sì rilancia con `--browser chrome`. GUARDA tutti i fogli,
   `tagli.jpg`, tutte le strisce di movimento e 2-3 fotogrammi grandi: i fogli dicono COSA c'è, le strisce COME si
   muove. I salti di suono sono le tue orecchie: controlla ogni salto sul fotogramma di quel secondo.
   Più esempi: un messaggio solo, "di ognuno ho visto questo (una riga): cosa prendi da quale?".
   Solo un'immagine (screenshot): non dice ritmo, movimento e suono: una domanda, o scelte calme e lo dici.
2. **Crea lo stile e scrivilo.** `PY STUDIO/strumenti/stile_da_esempio.py <nome> --base <stile pronto più vicino>
   --esempio <nome>`, poi compila `stile.md` (una riga per aspetto, niente "come nell'esempio") e cambia
   `stile.json` (colori, font, sottotitoli, transizione, mirino, finale, effetti).
3. **Rifallo sul video dell'utente**: le sue parole, le sue riprese, la sua durata. Si copia il ritmo, non i tempi.
   Monta con `"stile": "<nome>"` come sempre (passaggi 1-7).
4. **Confronta.** `PY STUDIO/strumenti/confronta.py <esempio> <lavoro>` (anche `--a` con secondi a metà di
   un'entrata, dalle strisce): esempio sopra, il suo reel sotto. Correggi quello che non torna, una volta.
   Poi dagli il foglio e una lista semplice: cosa è uguale, cosa non si è potuto rifare. Mai fingere.
5. **Sistemalo con lui e salvalo.** Le sue correzioni vanno nello stile. Quando gli piace: anteprima dello stile da
   quel reel (`anteprima.mp4` + `anteprima.jpg`), e di': "Salvato come Stile <nome>: lo trovi nella pagina; la
   prossima volta basta monta questo video."
Limiti da dire chiari: la musica dell'esempio non si prende (c'è quella dello stile); niente effetti 3D o
rallentamenti dentro il video se lo studio non li ha.

## Correzioni dell'utente
Una correzione per questo video si fa nel `piano.json` o nel `tagli.json` di questo video, poi si rifà dal passaggio
che è cambiato e si crea la versione dopo (v2, v3: le vecchie restano). Tagli cambiati dopo il piano:
`regole/taglio.md` spiega come spostare il piano da solo (`rimappa.py`).
Cambiati solo suoni o musica: `costruisci.py NOME` e poi `rendi.py NOME --solo-audio` (secondi, non minuti).
Rifai un video alla volta, quello chiesto, con un solo controllo rapido: l'utente non vuole aspettare né sprecare.
Una correzione entra nello stile o nelle regole SOLO se l'utente dice "sempre" o "d'ora in poi", e con il suo ok.
