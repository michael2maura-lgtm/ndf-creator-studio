---
name: monta-video
description: Monta un reel parlato in verticale (taglio, sottotitoli italiani parola per parola, titoli, scene, suoni e musica nello stile salvato, volume per Instagram) partendo dal girato grezzo. Usala quando l'utente dice "monta questo video", "montami il video", "monta il reel", "edita questo video", "installa lo studio", "aggiorna lo studio", "installa l'aggiornamento", "aggiorna il plugin", "facciamo il mio brand", "cambia i miei colori", o indica un girato da trasformare in reel. Anche per la VSL orizzontale: "monta la mia VSL", "montami la VSL", "fai la VSL".
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
- **Aggiornamenti:** `PY STUDIO/strumenti/aggiornamenti.py`, fuori dalla sandbox, con un tempo lungo (mai interromperlo).
  Fa tutto il programma: tu non lanci mai comandi `claude plugin` a mano e non scegli le parole. Righe:
  `AGGIORNATO` o nessuna riga → niente da dire. `NUOVA VERSIONE` → una riga sola: "C'è una versione nuova dello studio,
  la installo? Ci vuole un minuto." `DA CARTELLA` → niente domanda, vai avanti come con un sì.
  Con un sì, o quando l'utente dice "aggiorna lo studio", "installa l'aggiornamento", "aggiorna il plugin" o simili
  (vuole la versione nuova, NON cambiare lo studio: non chiedere cosa modificare, non toccare nessun file):
  `PY STUDIO/strumenti/aggiornamenti.py --installa`. Di' al cliente la frase della riga `DI':` parola per parola e
  fermati lì: il resto si fa nella sessione nuova, con la versione nuova. Con un no vai avanti e non chiederlo più in
  questa chat. `RIAVVIA` (la versione nuova è già scaricata) → di' subito la frase della riga `DI':`, senza lanciare altro.
  Su Mac lo stesso programma (e ogni strumento) riprende da iCloud i file dello studio che il Mac ha spostato lì col
  disco pieno. Righe: `ICLOUD OK` → niente da dire; `ICLOUD BLOCCATO` → di' in parole semplici di aprire il Finder,
  Documenti, clic destro su NDFCreatorStudio, "Mantieni scaricato", e controlla internet; `DISCO PIENO` → dillo in una
  riga (con il disco pieno i video vanno più lenti e il Mac sposta i file su iCloud). Una pagina o un montaggio che resta
  fermo senza motivo: rilancia `aggiornamenti.py` prima di tutto.
- Manca il colore in `DATI/profilo.json` (brand mai fatto): prima di montare fai il brand in chat (sezione "Il brand",
  qui sotto), poi monta. L'intervista `crea-stile` si fa solo se l'utente la chiede.
- L'utente non dice quale video ("montami il video", senza file): non chiedere MAI il percorso del file e non chiedere
  i nomi in anticipo. Prima guarda `DATI/video-pagina.json`: se c'è, è il video che l'utente ha caricato nella pagina
  "Scegli il tuo look" (campo "file"): monta quello e di' in una riga "Monto il video che hai caricato nella pagina". Si usa una volta sola: a montaggio
  fatto rinomina il file in `video-pagina-usato.json`, così la volta dopo non rimonti lo stesso video.
  Se manca, cercalo tu: i video (mp4, mov, m4v) degli ultimi 3 giorni in Download, Scrivania, Filmati/Video
  e nella cartella del Rullino o di AirDrop, dal più nuovo (su Windows Download, Desktop, Video). Uno solo: montalo e
  di' in una riga quale hai preso ("Monto il video di oggi alle 10:42, quello da 1 minuto"). Più di uno: una domanda
  sola, con al massimo 3 video per nome, ora e durata ("Quale monto?"). Nessuno: "Trascina il video qui in chat e lo
  monto". I nomi detti nel video non si chiedono: si usano se l'utente li ha scritti, e una parola dubbia si chiede
  dopo la trascrizione, una alla volta.

## I passaggi, sempre in quest'ordine
1. `PY STUDIO/strumenti/prepara.py "<video>" NOME --nomi "<nomi detti nel video>"`
   Stampa `SCELTE DEL CLIENTE: ...`: scrivilo SUBITO al cliente in una riga semplice, prima di andare avanti
   ("Monto in Pulito, con i sottotitoli Semplici e i tuoi 5 effetti: ..."; se non c'è uno stile salvato, diglielo).
   Se vuole altro, si cambia ora. Poi leggi `trascrizione.txt` e guarda `foglio.jpg`.
2. Scrivi `tagli.json` seguendo `regole/taglio.md`, poi `PY STUDIO/strumenti/taglia.py NOME`. Tu scegli QUALI frasi
   tenere; le pause le toglie da solo (`stringi.py`, dentro taglia.py): il reel non si ferma mai. `--respiri` solo se
   l'utente vuole un ritmo calmo.
3. `PY STUDIO/strumenti/parole.py NOME --nomi "..."`: confronta il testo con quello detto (regole/taglio.md).
   `PY STUDIO/strumenti/controlla_tagli.py NOME` e guarda `controllo/tagli.jpg`.
   `PY STUDIO/strumenti/controlla_audio.py NOME`: il controllo dei tagli a orecchio (parola mozzata, sillaba in più,
   pausa lunga, ripetizione), con il pezzo e il secondo dell'originale da sistemare. Sistema `tagli.json`, rifai
   taglia.py, parole.py e il controllo, al massimo 3 giri: finché non dice `DA SISTEMARE: 0` non passi al piano
   (una ripetizione voluta va bene). Se resta qualcosa, nel messaggio finale di' il secondo da ascoltare.
   Lo zoom cambia da solo a ogni taglio (largo, stretto, largo, più stretto, sulla faccia): non scriverlo nel piano.
4. `PY STUDIO/strumenti/faccia.py NOME` e guarda `controllo/faccia.jpg`: il riquadro verde deve stare sulla faccia (quelli blu sono le mani: lo studio le segue per non coprirle).
5. Leggi le ultime 5 righe di `stili/<stile>/registro.md` e scegli scene, clip e pose diverse da quelle.
   **Prima di tutto il gancio** (primi 2-5 s), in ogni stile: segui `regole/gancio.md` (titolo corto vicino agli
   occhi, testo-immagine-voce uguali, un cambio ogni 1-2 s solo lì).
   Decidi che video è. **Completo**: ogni 3-6 secondi una scena a tutto schermo di 1-3 secondi, poi si torna sulla
   persona; zoom, transizioni, suoni degli oggetti, musica. **Parlato** (spiega un concetto, annuncio semplice):
   sottotitoli, titoli e finale, niente musica. Se l'utente lo dice, vale quello.
   **La musica la scegli dal tono del video** se il video ha la musica (non i video Parlato né gli stili senza
   musica, come Pulito) e la riga SCELTE DEL CLIENTE dice "musica: dal tono del video"
   (se dice "quella del modello", "nessuna" o il nome di un brano, vale quello e non scegli niente):
   `PY STUDIO/strumenti/musiche.py scegli <tono>` e nel piano `"musica": "<il percorso che stampa>"`. Toni:
   `calma` (storia personale, racconto, riflessione), `positiva` (consigli, spiegazioni, presentazioni),
   `morbida` (bellezza, cura di sé, benessere), `carica` (sport, sfida, motivazione), `energica` (annunci, ritmo
   alto). Sono musiche di pubblico dominio (`musica/libere.json`): non serve citarle. Non ripete i brani degli
   ultimi video. Se stampa MANCA si usa la musica dello stile. Nel resoconto di' quale tono hai scelto e perché.
   Scrivi `piano.json` (formato in cima a `strumenti/costruisci.py`, `scene.py`, `suoni_reel.py`, `split.py`)
   seguendo `stili/<stile>/stile.md` e `regole/suoni.md`. Scene: `testo`, `capitolo` (01 02 03), `clip` (clip vere in
   `DATI/clip/`, "x" per la X rossa), `omino` (in_piedi, spallucce, braccia_su, scrivania; "chiaro", "croce",
   "numero"), `chat`, `telefono` ("storia" o "reel"), `schema`; sopra la persona `titoli`, `liste`, `parole_chiave`.
   Ogni scena nasce da una frase detta in quel momento, con le parole dette.
   Clip vere: con il modello "Con immagini" la prima volta chiedi al cliente le sue foto e i suoi video (lo dice
   `stili/immagini/stile.md`); prima guarda quelle che ci sono in `DATI/clip/` e `DATI/immagini/`. Se manca quella giusta, cercala sul web
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
   Effetti nuovi (barra, scontrino, carrello, sondaggio, voto, podio, top, freccia, postit, citazione): formato in cima
   a `strumenti/effetti_nuovi.py`; parole sparse, pallini, copertina di rivista, schede con le barre, cartellini
   legati, parole giganti dietro, nomi colpiti, B-roll a tutto schermo (sparse, pallini, rivista, schede, cartellini, scritte, colpiti, broll):
   formato e quando usarli in cima a `strumenti/effetti_piu.py`; sfondo che si apre, sfondo sfocato con scritta, luce
   dietro la testa, collage di carta, il video in un reel (dentro, sfocato, raggi, collage, reel): in cima a
   `strumenti/effetti_scena.py`; scritta che si cancella, lettere che cadono, carte a ventaglio, polaroid, messaggio
   vocale (cancella, lettere, ventaglio, polaroid, vocale): in cima a `strumenti/effetti_carte.py`; scritta che si
   colora, carosello, tasti che piovono, fumetto, cartello (colora, carosello, tasti, fumetto, cartello): in cima a
   `strumenti/effetti_parole.py`; elenco che si accende, le cose dal basso, muro di reel, capitolo, nastro che scorre
   (elenco, scalata, mosaico, capitolo, nastro): in cima a `strumenti/effetti_liste.py`; le immagini dietro di me,
   lista che scorre, messaggio in arrivo, apertura tipografica (immagini, scorri, messaggio, fondale): in cima a
   `strumenti/effetti_sfondi.py`. Usa solo gli effetti accesi nella pagina Effetti (scelte.json "effetti"): dove
   metterli lo decidi tu, sulla frase che li giustifica, con numeri e nomi veri detti nel video (mai inventati).
   Zoom: decidilo sempre tu, in ogni video, seguendo `regole/zoom.md` (l'utente non deve chiederlo).
   **Poche cose fatte bene**: una grafica alla volta, mai lampi, adesivi o pillole su ogni parola. Se un elemento non
   aiuta a capire o a sentire, toglilo.
   Una grafica o una scena NUOVA (che non c'è nel catalogo, una scena disegnata, un modello nuovo): prima leggi le guide
   per animare in `riferimenti/motion/LEGGIMI.md` (dice quali e quando) e falla seguendo quelle regole.
   **Scena piena dal primo fotogramma**: una scena a tutto schermo non si apre mai su uno sfondo vuoto (anche mezzo
   secondo fa sembrare il reel in ritardo). Gli elementi principali ci sono già, tenui, e si accendono sulla parola
   detta; dal nulla compaiono solo gli accenti (un timbro, un cerchio, un oggetto che vola).
   **Strumenti e marchi veri**: se nel video si nomina un'app, un sito o un marchio, si mostra il suo logo vero (dal
   sito ufficiale) o la sua pagina vera, mai un disegno generico o un logo inventato.
   **Mai più di due scene costruite allo stesso modo** in un video, e mai due di fila: si alterna.
   **La faccia ha lo stesso colore in tutto il video**: i filtri colore vanno sulle clip e sulle foto, mai sulle
   riprese della persona (anche quando è ritagliata o dentro un riquadro).
6. `PY STUDIO/strumenti/costruisci.py NOME --zone`, poi `PY STUDIO/strumenti/foto.py NOME <6-8 momenti>`
   e guarda il foglio: niente nelle zone rosse, niente sulla faccia, niente righe orfane. Una riga `NOTA MANI` dice che
   un titolo sul petto copre a lungo le mani che gesticolano, o che un fermo immagine cade con una mano sulla faccia:
   sposta l'elemento ai secondi indicati, o dove le mani sono giù, se il gesto conta.
7. `PY STUDIO/strumenti/costruisci.py NOME` (senza zone), poi `PY STUDIO/strumenti/rendi.py NOME`.
8. `PY STUDIO/strumenti/controlla_tagli.py NOME finale/NOME-vN.mp4 --telefono`: guarda i fotogrammi del video
   (e fai il controllo "in silenzio" dei primi 5 secondi di `regole/gancio.md`)
   FINITO e il volume. Se stampa DA GUARDARE (nero, o due cambi di immagine troppo vicini), guarda `nascosti.jpg`:
   se è un errore vero (un fotogramma di un'altra scena, un buco nero) correggilo e rifai il video prima di mandarlo;
   se è un passaggio voluto (lampo, transizione) vai avanti. Manda all'utente la copia per il telefono.
   **Copertina e didascalia, sempre, con ogni reel:** `PY STUDIO/strumenti/copertina.py NOME --titolo "2-6 PAROLE
   con la *parola chiave* tra asterischi"` (il gancio o la promessa del video, con le sue parole) e guarda
   `controllo/copertina.jpg`: occhi aperti, espressione buona, titolo leggibile; se no rilancia con `--t <secondo>`.
   Poi scrivi la didascalia in `finale/NOME-didascalia.txt` seguendo `regole/didascalia.md` e controllala con
   `PY STUDIO/strumenti/didascalia.py NOME` finché dice DIDASCALIA OK. Manda all'utente la copertina e il testo
   della didascalia in chat, pronto da copiare. Se nel video c'è una frase rischiosa per il network (soldi promessi,
   effetti medici), diglielo in una riga con il secondo.
   **Il critico, prima di mandare il video:** `PY STUDIO/strumenti/critico.py NOME`, poi lancia un subagente (strumento
   Agent, tipo general-purpose) con il prompt: "Sei il critico di un reel. Leggi <il percorso LEGGIMI.md che ha
   stampato> e segui le istruzioni: guarda tutte le immagini e rispondi solo nel formato richiesto." Non dirgli
   cosa hai fatto tu: deve guardare con occhi nuovi. Correggi le righe GRAVE che sono davvero problemi (un giro
   solo: piano o tagli, poi la versione dopo), le PICCOLO solo se si sistemano in un attimo; se una GRAVE secondo te
   è sbagliata, lasciala ma dillo nel resoconto. Se lo strumento Agent non c'è, fai tu questi controlli con
   `regole/critico.md`. Al cliente non serve sapere del critico: digli solo cosa hai sistemato.
9. `PY STUDIO/strumenti/registro.py <stile> "NOME | scene: ... | clip: ... | omini: ... | suoni: ..."` con
   quello che hai usato davvero. Di' in poche righe cosa hai fatto, se hai messo la musica e perché, e cosa deve
   ascoltare o controllare (le parole corrette a intuito, con il secondo). Tu non senti l'audio: dillo.
10. Apri la pagina di revisione: `PY STUDIO/strumenti/revisione.py NOME`, in sottofondo, e di' in una riga: "Ti ho
   aperto la pagina del video: fermalo dove vuoi cambiare qualcosa, premi Nota qui, e alla fine Correggi oppure
   Approva. Se preferisci, scrivimelo qui." Quando la pagina si chiude, la sua ultima riga dice cosa ha scelto
   (CORREGGI o APPROVATO): vedi "Correzioni dell'utente".

Modelli rifatti da zero (quelli che la pagina mostra al passo 1, stile.json "modello": true), per ora tre: **Pulito** (`pulito`: solo la persona, tagli netti, sottotitoli, zoom leggero, sfumatura di luce sui cambi di argomento; niente grafiche, titoli, musica: vedi il suo stile.md) ed **Energia** (`energia`: tutto il testo sopra la testa, parole giganti e targhe inclinate a due colori, elenchi che si costruiscono, sfondi nuovi dietro la persona staccata, disegni animati sulle parole che si possono disegnare, l'orbita dei reel; elementi in `strumenti/effetti_sopra.py`, regole nel suo stile.md). In Energia l'inventiva è il format: ogni parola che si può far vedere diventa un disegno o una grafica. **Chiaro** (`chiaro`: il livello di mezzo, va bene per tutti: titolo sul gancio con la parola chiave in corsivo, poi una grafica ogni 7-8 secondi tra parola chiave elegante e scheda numerata sotto il mento; zoom ogni pochi secondi, sfumatura sui cambi di argomento; elementi in `strumenti/effetti_chiaro.py`, regole nel suo stile.md). Se l'utente non sa quale scegliere, consiglia Chiaro.
Stili pronti, cinque: **Glow** (`glow`: Impact semplice, sfumatura e pop-up, per i contenuti organici), **Scene** (tu che parli e tra una frase e l'altra la scena giusta: clip e foto nella finestra,
lavagna, lavagna bianca a schede "bianca"; niente omini), **Impact** (`ndf-grafica`, lo stile Notech dei reel di esempio 01 e 04: grafiche sopra la persona e, per numeri e prima/dopo, le scene animate "scena" della pasta; poche per un video
semplice, con la sfumatura come passaggio, tante per un video d'impatto) **Diviso** (pannello in alto, persona sotto) e **Diviso forte** (`diviso-forte`: titolo grosso in alto e un disegno per ogni frase, la persona in una cornice, sempre fisso; quando usare ogni disegno in `stili/diviso-forte/stile.md`; le foto vere degli oggetti nominati le scegli e le scarichi da solo, senza chiedere).
NDF e Linee sono in Scene, Racconto e Luce in Impact, Ads è solo un finale: la pagina non li mostra ("nascosto": true) ma si
usano ancora per nome. Ads non è uno stile: se il video è per le ads, finale "CLICCA QUI SOTTO", mai "commenta".
"Come il 22" (Michael) non è uno stile ma un modo di montare, in qualsiasi stile: grafica forte nei primi 15-20 s,
poi persona pulita, finale forte sul "commenta". Scheda in `DATI/esempi/come-il-22/analisi.md` (solo sul computer di Michael).
Stili in `DATI/stili/` (quelli dell'utente) e `STUDIO/stili/` (quelli pronti). L'utente può dire quale
("monta questo in stile X"); se non lo dice, usa quello di `DATI/scelte.json` (la pagina qui sotto), se no il suo.

## La pagina "Scegli il tuo look"
L'utente dice "scegli il look", "apri la pagina", "voglio cambiare suoni / musica", o non sa che stile usare:
lancia `PY STUDIO/strumenti/scegli.py` in sottofondo e di' in una riga che si è aperta nel browser.
L'utente dice "non vedo l'icona sul desktop" o "rifai l'icona": `PY STUDIO/strumenti/icona.py` e di' dove l'ha messa
(la riga ICONA); se ancora non la vede, la pagina si apre comunque con "apri la pagina".
Icona sulla scrivania "NDF Creator Studio" (doppio clic, si apre la pagina dall'ultima versione): la crea l'installazione.
Se manca `~/.studio-video/apri_pagina.py`, o l'utente chiede l'icona, lancia `PY STUDIO/strumenti/icona.py` in silenzio.
Tre strade: stile pronto, replica un reel (l'utente ti manda il link in chat: lo studi con l'abilità `crea-stile`
e ne fai uno stile nuovo, che poi compare nella pagina), crea il tuo (parte da uno stile e cambia suoni e musica).
Quando scrive `SCELTE SALVATE`, di' in una riga cosa ha scelto.
La pagina (telefono con anteprima e 8 passi) salva in `DATI/scelte.json` anche queste scelte, che applichi TU nel piano
di ogni reel (valgono finché non le cambia):
- `modello`: pulito, chiaro, energia, glow, scene, impact, diviso, ads, animato. **ads** = stile Impact, gancio forte nei primi 2 s,
  ritmo veloce, finale "CLICCA QUI SOTTO" (mai "commenta").
- `accento`: il colore del brand. Nel piano del motore grafica `"colori": {"accento": "<accento>"}`; negli altri sulle
  parole chiave e sui titoli.
- `chiusura` (commenta / segui / clicca / niente), `parola` (la parola da commentare) e `ricevi` (cosa riceve chi
  commenta): il finale del reel. **commenta**: "COMMENTA" + la parola sul bottone, e se c'è `ricevi` la riga
  "PER RICEVERE <ricevi>" (motore grafica: `finale_testo`, `finale_bottone`, `finale_sopra`; altri: `finale_testo`
  "COMMENTA <PAROLA>", `finale_sotto` "per ricevere <ricevi>"). **segui**: il tasto Segui del profilo. **clicca**:
  "CLICCA QUI SOTTO" con la freccia (scopri di più). **niente** (o nessuna scelta): nessun finale, il reel chiude
  sull'ultima frase. Se l'utente lo dice in chat per un video, vale quello. La parola da commentare cambia a ogni
  video: se nel video la dice ("commentate GUIDA"), usa quella; se no quella della pagina; se manca anche lì e il
  finale è "commenta", chiedila una volta in chat. Mai una parola fissa per tutti i video.
- `durata`: secondi massimi. Se il tagliato è più lungo, proponi all'utente le frasi da togliere prima di tagliarle.
- `punti`: [{"quando": parole dette, "effetto": chiave, "testo": scritta}] = in quel punto esattamente quell'effetto
  (trova le parole in `parole.json`); se il testo è vuoto usa le parole dette. È un obbligo, non spostarlo.
- `testo_fisso`: una targhetta in alto per tutto il reel (elemento `targhetta`).
- `note`: richieste libere dell'utente per i suoi reel: valgono più delle altre scelte.
Le 3 caselle "stili salvati" stanno in `DATI/stili-salvati.json`: le usa la pagina, non serve toccarle. I 20 sottotitoli a scelta stanno in
`strumenti/sottotitoli.py`; le loro anteprime le rifà `anteprima_sottotitoli.py` (solo se ne cambi o aggiungi uno).
Colore del girato: `strumenti/colore.py` (6 look, la pelle resta naturale). Quello scelto nella pagina lo applica
`costruisci.py` da solo; per un video solo scrivi "colore" nel piano. Se l'utente chiede "che colore ci sta?",
`PY STUDIO/strumenti/colore.py proposte NOME` e mostragli `controllo/look.jpg`.
Effetti (motion graphics del motore grafica): catalogo in `strumenti/effetti.py`. Ogni
stile ha i suoi pochi effetti accesi (stile.json "effetti"); nella pagina l'utente accende quelli che gli piacciono
(scelte.json "effetti"). Nel piano usa SOLO gli effetti accesi, e solo dove c'entrano con la frase detta (lo stile.md
dice quando): grafica.py salta gli altri con una NOTA. Gli effetti che l'utente ha acceso nella pagina vincono sempre
sullo stile: anche se lo stile.md dice "niente grafiche" (Pulito, Luce), se scelte.json "effetti" ne ha di accesi li
metti nel reel, pochi (uno ogni 6-10 secondi) e sulle frasi giuste. Se nessuno c'entra con quello che dice, nel
riepilogo finale di' in una riga quali hai saltato e perché: l'utente deve sapere che li hai visti. L'utente non sceglie niente reel per reel. Le scelte le usa `costruisci.py` da solo: tu nel piano
scrivi lo stile scelto (scelte.json "stile"; se è vuoto, "pulito") e basta. Un altro stile solo se il cliente
l'ha chiesto in chat, con "stile_chiesto": true nel piano: se no costruisci.py si ferma (STILE DIVERSO). Tasto Segui ("segui"): solo su una frase che invita a seguire, e solo se c'è
`DATI/profilo.json` ({"nome": nome Instagram, "sotto": riga sotto, "foto": "profilo.jpg"} con la foto in DATI); se manca,
chiedi una volta il link del profilo Instagram, prendi foto e nome dalla pagina pubblica e salvali lì. Un'anteprima di uno stile è `anteprima.mp4` (il video intero, 540 px di larghezza, con l'audio) più la sua copertina
`anteprima.jpg` (un fotogramma con la faccia ferma e una scritta, mai una mano davanti)
nella sua cartella: falla quando crei uno stile nuovo, dal primo video approvato.
Velocità: ogni reel finito va il 5% più veloce (comune.VELOCITA); nella pagina l'utente sceglie Normale, Svelta o
Veloce, e `rendi.py` la usa da solo. Per un reel diverso: "velocita" nel piano (1 = com'è girato).
Transizioni (stili del motore grafica): nel piano scrivi "transizioni": [secondi], SOLO sui cambi di argomento (2-3 in
un minuto, nella pausa prima della parte nuova). Il tipo (sfumatura di luce, bande, taglio netto) è quello dello stile
o quello scelto nella pagina: tu scrivi solo i secondi.

Pagina Stile (come si sceglie il look): modello, look del video, font dei titoli (grandezza, grassetto, corsivo,
maiuscolo, ombra), sottotitoli (stile, font del testo, font delle parole in evidenza, lettere, colori), chiusura e
durata, testo fisso in alto, note. Finiscono in scelte.json ("titoli", "sott", "testo_fisso", "fisso") e le applica
`strumenti/ritocchi.py` da solo, in qualsiasi stile: tu nel piano non scrivi niente. Il colore del brand non è nella
pagina: sta in `DATI/profilo.json` ("colore": "#RRGGBB"), fatto in chat all'inizio ("Il brand"). Gli effetti hanno la loro
pagina (scheda Effetti): il cliente accende quelli che gli piacciono, dove metterli lo decidi tu.

## Il brand (in chat, una volta sola)
Si fa in chat, mai con una pagina. Parte da solo la prima volta (manca il colore in `DATI/profilo.json`) o quando
l'utente dice "facciamo il mio brand", "cambia i miei colori", "cambia il mio logo". Strumento: `PY STUDIO/strumenti/brand.py`.
1. Una domanda sola: "Hai già il tuo brand? Allegalo qui, oppure mandami il logo e il link della tua landing o del tuo
   Instagram. Se non hai niente, ti faccio io qualche domanda." Quello che arriva vale tutto:
   - un brand già fatto (anche con Claude, un PDF, un file, delle immagini): lo leggi e prendi colori, font, tono, frasi;
   - il logo: `brand.py colori LOGO` dà i colori vivi più presenti;
   - la landing o il sito: leggi la pagina (testi, colori, font usati) e prendi tono, frasi sue e colori;
   - Instagram: dalla pagina pubblica nome, riga sotto il nome e foto profilo.
2. Chiedi SOLO quello che manca, una domanda per messaggio e al massimo tre: di solito il tono ("come parli ai tuoi
   clienti?") e le frasi che non vuoi dire mai. Mai chiedere codici di colore o nomi di font, né la parola da commentare
   (cambia a ogni video: vedi `chiusura`).
3. Scegli tu: UN colore che accende titoli e parole importanti (quello più acceso del brand, non lo scuro); il font
   dei titoli e quello del testo tra quelli dello studio (`brand.py font`), il più simile a quelli del brand (un font
   che lo studio non ha: `prendi_font.py`, se no il più simile).
4. Scrivi `DATI/brand.md`, la scheda del brand in parole semplici: chi è e cosa fa, a chi parla, tono di voce, frasi
   sue da usare, frasi e parole mai, colori con il loro uso, font,
   cosa evitare nelle grafiche, da dove l'hai preso. Poi `brand.py salva` con un json (colore, nome, sotto,
   parole speciali, logo, foto, font_titoli, font_testo): scrive `DATI/profilo.json` e i font in `scelte.json`.
5. `brand.py prova` fa `DATI/brand-prova.jpg` (titolo, sottotitolo, scheda Segui e bottone con il suo brand): mostralo
   e chiedi "Ti piace così?". Se cambia qualcosa, lo correggi a parole e rifai la prova. Poi in una riga: "Fatto, da
   ora ogni video esce con il tuo brand."
Da lì in poi non si chiede più: il colore lo prende `comune.con_le_scelte` in ogni stile, le parole speciali entrano da
sole in `prepara.py` e `parole.py` (tu aggiungi con --nomi solo i nomi di QUEL video). Ogni volta che scrivi titoli, scritte o la chiusura di un reel, rileggi `DATI/brand.md`:
tono e parole del cliente, mai le frasi della lista "mai". I font scelti nella pagina Stile vincono su quelli del brand.

## Copiare lo stile di un reel ("replica questo reel", "voglio uno stile come questo")
L'utente manda un link, un file o descrive un aspetto: quello è il brief. Non lo avvicini allo stile più simile che
c'è: ne rifai l'aspetto, movimenti compresi, sul video dell'utente. Si copiano l'ASPETTO e la STRUTTURA (tipo di
carattere, maiuscolo, colori, targhe, posizioni, ritmo dei sottotitoli, movimenti, ritmo dei tagli, tipo di grafiche,
carattere dei suoni). Mai le immagini, la musica, la voce, il logo, il nome o le parole di chi l'ha fatto, e mai dire
che il risultato è fatto con lui. Caratteri: quello gratuito più vicino; se lo studio non ce l'ha,
`PY STUDIO/strumenti/prendi_font.py "<nome>" --stile <stile>` lo scarica (solo licenze libere; se dice NON C'È usa il
più simile che c'è). Di' quale usi al posto dell'originale. Mai un font a pagamento.
1. **Prendi e studia ogni esempio.** `PY STUDIO/strumenti/prendi_esempio.py "<link o file>" [altri] --nome <nome>`,
   poi `PY STUDIO/strumenti/studia.py <nome>` per ognuno. Se dice SERVE LOGIN chiedi il permesso di usare l'accesso del
   browser (le parole sono nello strumento); solo con un sì rilancia con `--browser chrome`. GUARDA tutti i fogli,
   `tagli.jpg`, tutte le strisce di movimento e 2-3 fotogrammi grandi: i fogli dicono COSA c'è, le strisce COME si
   muove. I salti di suono sono le tue orecchie: controlla ogni salto sul fotogramma di quel secondo.
   Più esempi: un messaggio solo, "di ognuno ho visto questo (una riga): cosa prendi da quale?".
   Solo un'immagine (foto, screenshot, pin): prendi_esempio e studia la accettano (foto.png, dettagli.jpg, colori).
   Non dice ritmo, movimento e suono: una domanda, o scelte calme e lo dici.
2. **Crea lo stile e scrivilo.** `PY STUDIO/strumenti/stile_da_esempio.py <nome> --base <pulito, chiaro o energia: il più vicino>
   --esempio <nome>[,<altro>]`, poi compila `stile.md` (una riga per aspetto, niente "come nell'esempio") e cambia
   `stile.json` (colori, font, sottotitoli, transizione, mirino, finale, effetti).
3. **Rifallo sul video dell'utente**: le sue parole, le sue riprese, la sua durata. Si copia il ritmo, non i tempi.
   Monta con `"stile": "<nome>"` come sempre (passaggi 1-7).
4. **Confronta.** `PY STUDIO/strumenti/confronta.py <esempio> <lavoro> --a <secondi dell'esempio> --tuo <secondi
   del suo reel>`: a coppie, lo stesso tipo di momento (un titolo sotto un titolo), anche a metà di un'entrata dalle
   strisce. Esempio sopra, il suo reel sotto. Correggi quello che non torna, una volta.
   Poi dagli il foglio e una lista semplice: cosa è uguale, cosa non si è potuto rifare. Mai fingere.
5. **Sistemalo con lui e salvalo.** Le sue correzioni vanno nello stile. Quando gli piace: anteprima dello stile da
   quel reel (`anteprima.mp4` + `anteprima.jpg`), e di': "Salvato come Stile <nome>: lo trovi nella pagina; la
   prossima volta basta monta questo video." Stili salvati: `PY STUDIO/strumenti/stili.py elenco`; se dice "usa
   sempre questo", `stili.py usa "<nome>"`; per cambiargli nome, `stili.py rinomina "<nome>" "<nuovo>"`.
Limiti da dire chiari: la musica dell'esempio non si prende (c'è quella dello stile); niente effetti 3D o
rallentamenti dentro il video se lo studio non li ha.

## La VSL ("monta la mia VSL", "montami la VSL", "fai la VSL")
Video di vendita orizzontale (16:9) da un girato lungo: motore a parte (`vsl_*.py`), i reel non si toccano.
Il cliente scrive solo la frase: niente prompt da incollare, niente domande sullo stile. Il modo di lavorare, le
grafiche, il ritmo, la musica e le misure sono in `regole/vsl.md`: leggilo tutto prima di cominciare e seguilo.
Durata finale 10, al massimo 15 minuti. Colori e font sono quelli del suo brand (passo 0: manca il brand, prima quello).
1. **Materiali.** NOME = nome breve della VSL. `PY STUDIO/strumenti/vsl_materiali.py "NOME"`: crea la cartella, la
   apre da sola sullo schermo e stampa la riga da dirgli (cosa metterci e dove si trova): dilla così. Intanto trova il
   girato come per i reel (il video lungo più recente) e fai partire la trascrizione (passo 2), che è lunga.
   Quando scrive "fatto": `vsl_materiali.py "NOME" --guarda`, guarda i file e chiedi SOLO quello che manca e che
   serve a quello che dice nel video, una domanda per messaggio. Se non ha niente, si va avanti con le clip.
2. **Trascrizione e tagli.** `PY STUDIO/strumenti/prepara.py "<video>" NOME` in background (20 minuti di grezzo:
   circa 6 minuti). Poi `tagli.json` (regole/vsl.md, passo 2) e `PY STUDIO/strumenti/vsl_taglia.py NOME`. Leggi
   `testo.txt` tutto: frasi doppie, parole sentite male (correggile in `parole.json`), durata.
3. **Grafiche.** Scrivi `vsl.json` con le regole di regole/vsl.md (gancio movimentato, riquadri, numeri, barra,
   frase, chiusura, clip prima dai suoi materiali poi da Pexels, musica dalle basi energiche).
4. **Controllo sui fotogrammi.** `PY STUDIO/strumenti/vsl_monta.py NOME --anteprima` e guarda tutto il foglio.
   Correggi `vsl.json` e riguarda solo i fotogrammi cambiati (`--anteprima --tempi 12.5,40`), finché è giusto.
5. **Un render solo.** `PY STUDIO/strumenti/vsl_monta.py NOME` in background (15 minuti di VSL: circa 8-9 minuti).
   Controlla le misure stampate (-16 LUFS, picco sotto -1 dBTP), mettigli il video in Download con un nome chiaro e
   di' in una riga quanto dura e dove si trova.
**Correzioni** solo sul pezzo che ha detto: cambi quella grafica o quel taglio, riguardi solo quei fotogrammi, poi un
render. Cambiata solo la musica: `vsl_monta.py NOME --solo-audio` (secondi). Tagli cambiati: rifai `vsl_taglia.py`
e sposta i tempi di `vsl.json` dopo il pezzo cambiato.

## Correzioni dell'utente
Dalla pagina di revisione (riga `CORREGGI n note`): leggi `lavori/NOME/note.json`; ogni nota con "fatta": false ha
il testo, `t` (il secondo del video finito, quello che ha visto) e `t_piano` (lo stesso momento nei tempi del piano:
usa questo). Correggi tutte le note in una volta sola, fai la versione dopo, poi in note.json metti a ogni nota
"fatta": true e in "risposta" una riga su cosa hai fatto ("tolta la scritta", "foto degli oli cambiata"); se una
nota non si può fare, dillo nella risposta e in chat. Poi riapri la pagina sulla versione nuova (revisione.py NOME),
con le note fatte che si vedono spuntate. `APPROVATO vN`: il video è finito; se ha note, leggile comunque.
Una correzione per questo video si fa nel `piano.json` o nel `tagli.json` di questo video, poi si rifà dal passaggio
che è cambiato e si crea la versione dopo (v2, v3: le vecchie restano). Tagli cambiati dopo il piano:
`regole/taglio.md` spiega come spostare il piano da solo (`rimappa.py`).
Cambiati solo suoni o musica: `costruisci.py NOME` e poi `rendi.py NOME --solo-audio` (secondi, non minuti).
Rifai un video alla volta, quello chiesto, con un solo controllo rapido: l'utente non vuole aspettare né sprecare.
Una correzione entra nello stile o nelle regole SOLO se l'utente dice "sempre" o "d'ora in poi", e con il suo ok.
