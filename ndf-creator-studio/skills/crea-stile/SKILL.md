---
name: crea-stile
description: Crea lo stile di montaggio personale (colori, font, chiamata all'azione) con un'intervista breve, una domanda alla volta, e mostra un'anteprima. Usala la prima volta che si usa NDF Creator Studio, quando l'utente dice "crea il mio stile", "cambia i miei colori", "voglio un altro stile", o quando "monta questo video" non trova nessuno stile.
---

# Crea il mio stile

Lo stile dice a NDF Creator Studio come devono apparire i reel di questa persona. Si fa una volta sola.
Parla semplice, frasi corte, niente gergo. **Una domanda per messaggio**, sempre con 3-5 risposte d'esempio
così si può rispondere in fretta; accetta anche risposte con parole sue. Se una risposta è vaga ("moderno",
"professionale"), fai una sola domanda in più con un esempio concreto. Se non sa rispondere, proponi tu 2-3
alternative ricavate da quello che ha già detto, e sceglie lui. Mai decidere al posto suo con gusti tuoi.

STUDIO = la cartella `../monta-video` accanto a questa. Lancia i comandi fuori dalla sandbox. PY = il Python dello
studio (su Mac `~/.studio-video/venv/bin/python`, su Windows `~/.studio-video/venv/Scripts/python.exe -X utf8`).

## Le domande, in quest'ordine
1. **Il nome** del brand o del profilo (diventa il nome dello stile, in minuscolo e senza spazi).
2. **Il colore principale**: il colore che deve "accendere" le parole chiave e i titoli. Codice esadecimale se lo
   sa; altrimenti chiedi una foto del logo o del profilo e proponi tu il colore, con il codice, prima di usarlo.
3. **Il fondo**: scuro (consigliato, risalta di più) o chiaro; proponi il colore di fondo in tinta con il principale.
4. **Il carattere**: chiedi come deve "suonare" (deciso, elegante, amichevole, tecnico) e proponi 2-3 coppie da
   Google Fonts: uno in grassetto per i titoli e uno in corsivo per le frasi piccole. Esempi: Plus Jakarta Sans +
   Instrument Serif; Archivo + Fraunces; Space Grotesk + Cormorant Garamond. Non proporre Inter, Poppins o
   Montserrat se non li chiede lui.
5. **La chiamata all'azione** che usa di solito alla fine dei reel (es. "COMMENTA INFO", "SCRIVIMI IN DM",
   "CLICCA QUI SOTTO").
6. **Un reel che ama** (link o file), e cosa gli piace di lui: colori, scritte, ritmo, scene. Serve solo come
   nota per il montaggio, non si copia.
7. **Cosa non vuole vedere mai** (es. emoji, troppe scritte, musica, certi colori).

Prima di creare, controlla che non ci siano contraddizioni (es. "pacato" ma vuole ritmo velocissimo) e chiedi
quale vince.

## Creare e mostrare
`PY STUDIO/strumenti/nuovo_stile.py <nome> --accento "#..." --luce "#..." --testo "#..." --scuro "#..."
--font-titoli "..." --font-corsivo "..." --finale "..." --note "<risposte 6 e 7, con le sue parole>"`

`--luce` è una versione più chiara del colore principale; `--testo` il colore delle scritte (bianco caldo su fondo
scuro, quasi nero su fondo chiaro). Mostra `anteprima.png` (stampato alla fine) e chiedi: **"Cosa non ti somiglia?"**
Correggi e rilancia (`--anteprima` rifà solo l'immagine dopo aver cambiato `stile.json`) finché dice che è suo.

## I suoni (facoltativo, dopo)
Lo stile parte con una transizione, un colpo, la tastiera e una musica di base. Se vuole sceglierli:
`PY STUDIO/strumenti/catalogo_suoni.py` crea un video con tutti i suoni numerati;
mandaglielo, e copia quelli che sceglie in `stili/<nome>/suoni/` con i nomi transizione, colpo, tastiera, musica.

Alla fine di' in una riga che lo stile è pronto e che adesso basta scrivere "monta questo video".
