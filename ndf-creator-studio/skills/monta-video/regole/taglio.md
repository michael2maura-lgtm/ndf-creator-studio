# Taglio: come si sceglie cosa tenere

Dopo `prepara.py` leggi `trascrizione.txt` e guarda `foglio.jpg`, poi scrivi `tagli.json`.

- Via tutto quello che è fuori onda: commenti, frasi dette prima di partire, il braccio che avvia o ferma la registrazione.
- Frase ripetuta: tieni l'ultima ripresa completa e pulita.
- Via le pause morte tra un punto e l'altro. Le pause corte per respirare dentro una frase restano.
- **Inizio di un pezzo:** dove finisce il silenzio (elenco PAUSE), meno 0,06 s. Non usare l'inizio della parola di Whisper: può essere in ritardo di 0,1-0,3 s e si mangia la prima lettera (successo: "Sento" diventato "Tanto").
- **Fine di un pezzo:** dove inizia il silenzio dopo l'ultima parola.
- Mai togliere parole o frasi intere senza chiederlo.
- **Ritmo dinamico** (video completi, o quando l'utente chiede "più veloce"): togli anche le pause dentro le frasi
  sopra 0,2 s (silencedetect -35 dB), lasciando 0,05 s ai bordi. Più tagli = più zoom a scatti.
- Se rifai il taglio dopo aver scritto il piano: `cp segmenti.json segmenti-vecchi.json`, poi `taglia.py`,
  poi `strumenti/rimappa.py NOME segmenti-vecchi.json` sposta da solo tutti i tempi del piano.

Dopo `taglia.py`:
- `parole.py`: confronta il testo con quello che è stato detto. Se manca una parola vicino a un taglio, sposta il taglio. Se manca in mezzo a un pezzo, riascolta quel pezzo da solo: spesso è Whisper che l'ha saltata.
- `controlla_tagli.py`: guarda `controllo/tagli.jpg`. Ogni "dopo" deve essere pulito, niente braccia a metà movimento strano o occhi chiusi.
