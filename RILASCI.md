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
   - installazione da zero, come un cliente nuovo;
   - un reel Pulito e un reel Chiaro con la scritta dietro la testa, sul video di prova dello studio;
   - lo stesso reel Chiaro con il disco quasi pieno (il modo "poco spazio");
   - copertina, controllo del video finito, controllo degli aggiornamenti;
   - aggiornamento: la versione dei clienti (main) installata, poi la versione nuova **senza reinstallare**, con
     un reel (un aggiornamento non rilancia l'installazione: se la versione nuova ha bisogno di un programma
     nuovo, qui si vede).
3. Solo se tutto è verde si porta su `main` (cambiando il numero in `plugin.json`): da lì arriva ai clienti.

Sul proprio computer: `python3 ci/prova.py --senza-installa` (usa lo studio già installato, dati di prova a parte,
i lavori veri non si toccano). Risultati e video in `ci/uscita/`.

Cosa il robot non prova: un computer con 8 GB di memoria (GitHub non li ha), iCloud/OneDrive, l'app Claude.
Per questi, prima di main, una prova a mano su un computer piccolo quando la versione tocca render o installazione.
