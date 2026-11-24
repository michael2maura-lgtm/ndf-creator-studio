# Stile Diviso forte

Schermo diviso che spiega: in alto un titolo grosso e, sotto, un disegno che fa vedere la frase detta; una riga di
sottotitoli; la persona sotto, in una cornice. Approvato da Michael il 24/11/2026 (lavoro di prova zz-diviso-nuovo).
Si copia l'aspetto di un reel di esempio, mai immagini, parole o marchio. Motore: strumenti/grafica.py, elemento
"pannello"; stile.json "forte": true con "riquadro": true.

## Aspetto
- Fondo scuro su tutto lo schermo, con raggi del colore d'accento che partono dal centro della grafica
- Titoli grossi e stretti (font dei titoli: Anton, o quello scelto nella pagina) in maiuscolo; la parola importante
  su una fascia del colore d'accento, un po' storta ("stile": "accento")
- Una riga di sottotitoli ("riga-forte": Poppins grassetto, maiuscolo, parola chiave colorata) tra grafica e cornice
- La persona in una cornice larga con gli angoli arrotondati e il bordo del colore d'accento
- Sempre fisso: niente grafiche a tutto schermo, niente transizioni
- A ogni cambio di frase (ogni nuovo "pannello") il lampo bianco leggero e lo scatto della persona più vicina, poi
  torna al suo posto: lo fa da solo, non va scritto nel piano

## Il piano: un "pannello" per frase, attaccati uno all'altro
Ogni frase detta ha il suo pannello, da quando comincia a quando comincia la frase dopo (niente buchi: se no il
pannello resta vuoto). Le parole sulla grafica sono quelle dette, accorciate.
- `titolo`: frase forte senza un oggetto da mostrare (gancio, "non serve saper montare", la frase finale).
  2-3 righe: una "forte", una "accento" (la parola che conta), "forte piccolo" per una riga lunga. I sottotitoli
  spariscono da soli sotto il titolo.
- Tutti gli altri con `"testa"`: 1-2 righe di titolo in alto (`[{"testo": "MANDA IL VIDEO", "stile": "forte", "da": s},
  {"testo": "E SCRIVI", "stile": "accento", "da": s}]`) e il disegno sotto:
  - `icone` con la x: "niente X, niente Y, niente Z" (icone barrate nel momento in cui le dici)
  - `schede` con "voci": un elenco detto ("tre cose", "primo... secondo...")
  - `scrivi`: quando la persona dice cosa scrivere o mandare (una chat, un messaggio, un comando): la frase si scrive
    nella casella, il tasto d'invio si colora, "ok" per il bollino verde del risultato
  - `confronto`: prima / adesso, due numeri o due situazioni ("prima tre ore, adesso cinque minuti"): niente "testa"
  - `numero`: un numero da solo detto con forza
  - `lista`: passaggi o cose da fare in fila
  - `telefoni`: SOLO quando si parla di video, reel o montaggi da mostrare ("montaggi così, così o così"): tre telefoni
    con le anteprime degli stili dello studio, uno per ogni volta che lo dici. Per altri argomenti mai
  - `cta`: la chiusura scelta nella pagina (segui, commenta la parola): bottone con la parola, il mouse che clicca
- Non tutte le frasi uguali: alterna titolo e disegni, mai due volte di fila lo stesso disegno.

## Suoni (Michael, 24/11/2026)
Ogni momento il suo, dai suoni di Impact: fascia arancione = impatto; righe bianche = nessun suono; telefoni, icone,
schede = colpetto; barra rossa = glitch; tastiera mentre si scrive, clic sull'invio, din sul bollino; "5 min" che si
accende = livello. Mai il fruscio (transizione) sulle grafiche: "non si può sentire". Musica bassa del Diviso.
