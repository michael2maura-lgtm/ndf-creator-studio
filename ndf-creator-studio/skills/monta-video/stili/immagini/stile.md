# Stile Con immagini

Il modello del B-roll (Michael, 2026-11-17): la persona parla e, mentre racconta, il video stacca sulle immagini di
quello che dice, poi torna su di lei. Nato da un reel di esempio (esempi/es-broll-1): si copiano ritmo e struttura,
mai le immagini, la voce o le parole. Motore: strumenti/grafica.py, grafiche in strumenti/effetti_piu.py ed effetti_sopra.py.

- Le immagini del cliente prima di tutto (Michael, 2026-11-17): con questo modello, prima di montare chiedi UNA volta
  "Hai foto o video tuoi di quello che racconti (il locale, i prodotti, il lavoro)? Trascinali qui." Quelli che dà
  vanno in DATI/immagini e DATI/clip (con il nome di cosa mostrano) e restano per i video dopo: usali per primi.
  Se dice di no, o per una frase di cui non ha immagini, le scegli tu da Pexels. Non richiederlo a ogni video.
- B-roll ("broll"): clip vere da Pexels (strumenti/clip.py, nome dell'oggetto) o foto, in una finestra arrotondata su
  fondo sfumato scuro ("broll_finestra"). Ogni stacco 1,5-4 s, su una frase che nomina una cosa che si può far vedere.
  Nei racconti (una storia, un problema del cliente) anche 2-3 stacchi di fila, ognuno sulla sua frase.
  In tutto il B-roll copre circa un terzo del video; mai nei primi 1,5 s (il gancio è la persona) né sulla chiusura.
  Ogni clip: GUARDA il .jpg che crea clip.py e usala solo se mostra davvero quello che si dice. Niente clip giusta,
  niente stacco.
- Domanda a tutto schermo ("schermata", colore del brand): sulla domanda che apre un pezzo nuovo ("ti chiedi
  perché?"), 1-2 volte in un minuto, 1-1,5 s, parole dette.
- Spunte ("spunte", nel colore del brand): sui punti di forza detti uno dopo l'altro (2-4 voci, le parole dette).
- Zoom leggero sui tagli (regole/zoom.md). Sfumatura di luce solo sui cambi veri di argomento.
- Sottotitoli: quelli scelti nella pagina (di serie una parola alla volta), continuano sopra il B-roll.
- Suoni: un passaggio morbido sullo stacco, pop sulle spunte, colpo sulla domanda; niente musica di serie.
- Mai due grafiche insieme. Finale: quello scelto nella pagina.
