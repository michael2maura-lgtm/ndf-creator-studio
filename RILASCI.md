# Come esce una versione dello studio

Regole decise con Michael il 25/11/2026, per far finire i problemi quotidiani dei clienti.

## Stop alle funzioni nuove
Finché la base non è stabile (installazione, aggiornamenti, disco, render) **non si aggiungono funzioni nuove**:
niente modelli, effetti o pagine nuove. Si correggono solo problemi veri dei clienti e si lavora sulla base.
Lo stop finisce quando Michael lo decide.

## Ogni versione passa dal robot di prova
1. Il lavoro si fa su un ramo che non è `main` (per esempio `prova-…`) e si manda su GitHub.
2. GitHub lancia da solo il robot (`ci/prova.py`, `.github/workflows/robot-di-prova.yml`) su un Mac Apple Silicon
   e su un PC Windows "vuoti" (senza Python, Node, ffmpeg):
   - installazione da zero con il programma di avvio (avvio.sh / avvio.ps1), come un cliente nuovo: Python, Node e
     ffmpeg propri, pezzi grandi, primo avvio con le due cartelle;
   - il controllo silenzioso della chat dopo (deve essere veloce e non scaricare niente);
   - la riparazione: toglie apposta una musica, l'icona e il modello della faccia, e il controllo li rimette;
   - un reel Pulito e un reel Chiaro con la scritta dietro la testa, sul video di prova dello studio;
   - lo stesso reel Chiaro con il disco quasi pieno (il modo "poco spazio");
   - copertina, consegna in "2 - Video finiti" (con la versione di prima in "Versioni vecchie"), controllo del
     video finito, controllo degli aggiornamenti;
   - aggiornamento: la versione dei clienti (main) installata nelle cartelle vere di un cliente, poi la versione
     nuova **senza reinstallare**: il controllo deve spostare lavori e modelli nella casa nuova e montare un reel.
3. Solo se tutto è verde, e con l'ok di Michael, si porta su `main`: da lì arriva ai clienti. Prima si cambia il
   numero in `plugin.json` e si scrive in `novita.json` la riga di novità di quel numero (una frase semplice: è
   quella che il cliente legge quando lo studio gli chiede se aggiornare).

## Provare un aggiornamento senza toccare i clienti
Lo studio segue il ramo del suo marketplace (`aggiornamenti.py`). In una cartella Claude di prova:
`CLAUDE_CONFIG_DIR=<cartella> claude plugin marketplace add michael2maura-lgtm/ndf-creator-studio#<ramo>` e
`claude plugin install ndf-creator-studio@ndf-creator-studio`; poi si manda sul ramo una versione con il numero più
alto che non cambia niente, e il controllo di quella installata deve dire `DISPONIBILE` con la riga di novità;
`aggiornamenti.py --installa` deve dire `FATTO`.

## Lo studio deve restare leggero
Il programma si copia intero sul computer del cliente a ogni versione. Dopo aver aggiunto o cambiato uno stile o
un'anteprima:
- `python3 ci/una_copia.py`: suoni e font uguali tra gli stili restano una volta sola;
- `python3 ci/sposta_anteprime.py`: le anteprime video vanno in `anteprime/` (fuori dal programma); la pagina le
  prende solo quando le mostra.

Sul proprio computer: `python3 ci/prova.py` (usa una casa e dati di prova suoi in `ci/`: lo studio vero e i lavori
veri non si toccano). Risultati e video in `ci/uscita/`.

Cosa il robot non prova: un computer con 8 GB di memoria (GitHub non li ha), iCloud/OneDrive, l'app Claude.
Per questi, prima di main, una prova a mano su un computer piccolo quando la versione tocca render o installazione.
