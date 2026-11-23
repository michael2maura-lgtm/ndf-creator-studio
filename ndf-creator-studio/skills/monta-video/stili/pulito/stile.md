# Stile Pulito

Il modello più semplice (Michael, 2026-11-14): tutta l'attenzione sulla persona. Motore: strumenti/grafica.py.

- Di serie nel video ci sono solo: tagli netti, sottotitoli, zoom leggero, colore sistemato, sfumatura di luce.
- **Prima guarda scelte.json "effetti"**: se il cliente ha acceso degli effetti nella pagina, quelli si mettono SEMPRE
  (anche se questo stile di serie non ha grafiche): pochi, uno ogni 6-10 secondi, sulle frasi in cui c'entrano, e
  usandone di diversi tra quelli accesi, non sempre lo stesso. Se il piano non ne usa nessuno, costruisci.py si ferma.
  Il resto del video resta pulito.
- Se il cliente non ha acceso niente: nessuna grafica (niente pop-up, pillole, numeri, telefono, scene, titolo
  d'apertura, riquadri, mirino); "elementi" nel piano contiene solo lo zoom; niente "apertura".
- Parole chiave ("parole_chiave"): sì, poche (una ogni 2-3 frasi: la parola che porta il senso), restano dentro la riga,
  stessa grandezza, nel colore del brand della persona (Michael, 2026-11-14). Mai giganti, mai da sole.
- Sfumatura di luce ("transizioni": [secondi]) solo sui cambi veri di argomento, nella pausa prima della parte nuova:
  2-3 in un minuto, mai più di una ogni 12 secondi. Con il suo suono morbido (suoni/sfumatura.mp3).
- Zoom: regole/zoom.md, versione calma: lento, poco (1.0-1.12), senza scatti e senza rumori.
- Niente musica ("musica": false), niente suoni oltre a quello della sfumatura.
- Sottotitoli: quelli scelti nella pagina (di serie "Semplici"), sul petto sotto la bocca.
- Finale: quello scelto nella pagina (chiusura). Con "niente" il video finisce sulla persona che parla.
- Testo fisso in alto: solo se l'utente l'ha scritto nella pagina.
