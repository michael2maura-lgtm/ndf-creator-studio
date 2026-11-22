# VSL orizzontale (16:9), versione semplice

Quando il cliente scrive "monta la mia VSL". Motore separato dai reel: `vsl_taglia.py`, `vsl_grafica.py`,
`vsl_monta.py`. I reel verticali (taglia.py, costruisci.py, grafica.py) non si toccano.

Modo di lavorare preso dalla VSL di riferimento (solo il modo, mai il suo aspetto: colori e font del cliente):
- **Gancio (primo minuto) movimentato**: lampo di apertura, clip che cambiano ogni 2-4 secondi su quello che dice,
  una grafica sopra di lei sul numero forte, clip sul risultato sognato. Circa metà clip/grafiche, metà lei.
- **Dopo il gancio** la persona quasi sempre in video; il ritmo lo danno gli stacchi con lo zoom a ogni taglio.
- Grafiche solo nei momenti decisivi: metodo, passaggi, numeri. Barra dei passaggi in basso per tutto il capitolo.
- Chiusura con la sua frase ("clicca il pulsante qui sotto") in un riquadro bianco, lei nella cornice al centro.

Com'è la versione semplice: la persona quasi sempre in video, sottotitoli in basso parola per parola, zoom leggeri
sulla faccia ai tagli, scritte in un riquadro sopra la persona sulle frasi chiave, grafiche a schermo pieno solo nei
momenti decisivi (con la persona in un riquadro piccolo a destra). Durata tipica: 10, al massimo 15 minuti.

## Passi (PY = ~/.studio-video/venv/bin/python)

0. **Cartella dei materiali** (decisa da Michael). All'installazione non si crea niente. Quando il cliente scrive
   "monta la mia VSL": `PY strumenti/vsl_materiali.py "<nome VSL>"` crea `DATI/<nome VSL> - materiali`, la APRE da
   sola sullo schermo (Finder sul Mac, Esplora file su Windows) e stampa la riga da dire al cliente: cosa trascinarci
   (foto delle clienti, chat, foto o video del prodotto, la sua musica se ne ha una) e dove si trova, in parole
   semplici: "La trovi in Documenti → NDFCreatorStudio → <nome VSL> - materiali".
   Quando scrive "fatto": `PY strumenti/vsl_materiali.py "<nome VSL>" --guarda` elenca cosa c'è. Guarda i file
   (le foto e un fotogramma dei video) e chiedi SOLO quello che manca, legato a quello che dice nel video, una
   domanda per messaggio: "Parli di Paola al minuto 4: hai la sua foto?". Il materiale del cliente viene prima
   delle clip di Pexels; la sua musica, se c'è, prima della libreria dello studio.
1. `PY strumenti/prepara.py "<video>" <nome>` — trascrizione di tutto il grezzo (20 minuti di grezzo: circa 6 minuti).
2. Leggi `trascrizione.txt` e scrivi `tagli.json`: l'ultima ripresa buona di ogni frase, come per i reel.
   Le VSL hanno molte frasi ripetute più volte: tieni la ripresa intera e pulita, mai mezza frase di una e mezza
   dell'altra. Whisper mette l'inizio delle parole un po' prima della voce: parti 0,1-0,2 s prima della prima parola.
3. `PY strumenti/vsl_taglia.py <nome>` — taglio, pause tolte, voce pulita (DeepFilterNet), zoom, parole sui tempi del
   taglio. Scrive `testo.txt`. Correggi a mano in `parole.json` le parole sentite male (nomi, numeri).
4. Leggi `testo.txt` e scrivi `vsl.json` con le grafiche (tempi in secondi del video tagliato):
   - `lampo`: 0,4 s di luce del brand all'apertura (o a un cambio di capitolo).
   - `riquadro`: 2-5 parole che riassumono la frase chiave, `*parola*` nel colore del brand. 3-4 secondi.
     Sulle promesse, sui numeri, sul nome del metodo. Una ogni 20-40 secondi al massimo: non su ogni frase.
     `"stile"`: "scuro" (di serie), "chiaro" (bianco, testo scuro), "forte" (nel colore del brand, per la parola più forte).
   - `contatore`: il numero forte che sale da 0 accanto alla persona, con la scritta che si scrive e le figure
     che si moltiplicano (`"numero": 297, "testo": "donne aiutate"`; `"x"`, `"y"` per spostarlo dalla faccia).
   - `frase`: una frase decisiva bianca su schermo pieno, parole che entrano una dopo l'altra (3-4 s).
   - `barra`: `"passi": [...]`, `"attivo": [[secondo, indice], ...]`; resta per tutto il capitolo, le grafiche a
     schermo pieno ci passano sopra. Con la barra i sottotitoli salgono da soli.
   - `chiusura`: `"testo"` = le parole che dice la persona per la chiamata finale.
   - `clip`: sopra la persona quando dice una cosa che si può far vedere (nel gancio soprattutto), 1,5-3 s.
     Prima il materiale del cliente, poi Pexels: `PY strumenti/clip.py <numero> <nome> --orizzontale` (1920x1080,
     fino a 8 s) e GUARDA i fotogrammi prima di usarla: deve mostrare quello che si dice, niente scritte in inglese.
     La persona resta in un riquadro piccolo in basso a destra (`"persona": false` per toglierla); `"nome"` mette
     l'etichetta in basso a sinistra (chi parla in una testimonianza). 
   - `numeri`: quando la persona elenca dei passi o dei punti. Le etichette sono le parole che dice lei nel video
     (da testo.txt), mai inventate né prese da altri video. Il riquadro della persona si adatta da solo (grande fino
     a 3 numeri, poi più piccolo); `"persona": "grande" / "media" / "piccola" / false` per sceglierlo. Una grafica per ogni passo detto, breve (4-6 s),
     con le voci già dette che restano (tempo prima di "da") e `"totale"` per tenere fermi i posti.
5. `PY strumenti/vsl_monta.py <nome> --anteprima` — foglio di fotogrammi presi dal montaggio vero
   (`controllo/foglio-vsl.jpg`). Guardalo TUTTO: scritte che coprono la bocca, testo tagliato, sottotitoli sopra le
   grafiche, tempi sbagliati. Correggi `vsl.json` e riprova: sono secondi, il video non si crea.
   Colori: quelli del brand del cliente (DATI/profilo.json "colore"). Per una prova fatta per un cliente da questo
   computer: una cartella dati di prova con il suo colore e `NDF_STUDIO_DATI=<cartella>` davanti ai comandi, così
   il profilo di Michael resta com'è.
6. Solo quando il foglio è giusto: `PY strumenti/vsl_monta.py <nome>` — un render solo
   (`finale/<nome>-vN.mp4`, 8 Mbit/s). Per 15 minuti: circa 8-9 minuti di attesa. Alla fine stampa volume e picco
   vero: devono stare intorno a -16 LUFS e sotto -1 dBTP.

## Ritmo: se la persona è lenta, la VSL si fa più dinamica da sola

Lo decide lo studio, il cliente non deve chiederlo. `vsl_taglia.py` misura sulla trascrizione delle riprese scelte
le parole al minuto e la pausa media tra le frasi, e scrive `ritmo.json`. È "lenta" sotto 165 parole al minuto o
con pause medie sopra 0,5 s (la personal trainer della prova: 158 parole al minuto, pause di 0,41 s).
Se è lenta:
- velocità +5-8% (quanto basta per arrivare a circa 168 parole al minuto, mai oltre l'8%: i reel arrivano al 12%,
  in una VSL la voce deve restare naturale). Voce e video insieme, il tono della voce non cambia. `--velocita 1`
  per lasciarla com'è;
- pause tra le frasi corte (stringi.py, già di serie: dopo il taglio restano circa 0,2 s);
- zoom sulla faccia più spessi (al massimo ogni 1,8 s invece di 2,5);
- nei tratti piatti più clip o grafiche: mai più di circa 15-20 secondi di fila senza una clip, una scritta o una
  grafica (invece di 30-40). Le clip mostrano quello che dice in quel momento (cibo su "alimentazione",
  allenamento in casa su "movimenti da fare a casa");
- musica con più energia: lo studio prende da solo il brano più ritmato della libreria (lo misura) e lo tiene
  2 dB più presente (15 dB sotto la voce invece di 17).
L'energia della voce NON si tocca: niente filtri, equalizzatori o compressori per "ravvivarla". Se il tono è piatto,
la spinta la danno il montaggio e la musica.

## Misure e audio

Decise con Michael e misurate sulle sue VSL di riferimento ("VSL Michael DEF" -16,5 LUFS, "fatto da me"
-16,6 LUFS; la VSL di un altro creator sta a -18,1 con picchi sopra 0 dB, cioè satura: da non imitare).
Vengono dalle misure e dal mestiere, non da regole di altri programmi.
- 1920x1080, con gli stessi fotogrammi al secondo del girato (25 o 30): mai convertiti.
- Voce finale intorno a -16 LUFS integrati, picco vero sotto -1 dBTP, loudnorm in due passate.
- Musica sotto: solo dalla libreria gratuita dello studio (DATI/musica), mai canzoni commerciali. Molto sotto la
  voce (17 dB, misurate tutte e due): si sente ma non copre, e quando la voce parla scende ancora da sola.
  Cambio di brano solo a un cambio di argomento, all'inizio di una frase:
  `"musica": [{"da": 0, "file": "rilassante-natura.mp3"}, {"da": 35.35, "file": "rilassante-country.mp3"}]`
  (un brano solo: `"musica": "file.mp3"`; niente musica: `false`; `"musica_sotto"` per cambiare i 17 dB).
- Suoni pochi, solo sulle grafiche: i numeri che compaiono, il contatore, il pulsante finale. Niente whoosh
  sulle clip e sui lampi. `"suono": false` in una grafica lo toglie, `"suono": "file.wav"` lo cambia.

Pochi token: niente render di prova del video intero. Si controlla sui fotogrammi, si crea una volta.

## Cosa manca (prossime sessioni)

- momenti in bianco e nero e lampi caldi a metà video
- nuvoletta col dubbio del cliente sotto la sua foto tonda
- icone semplici che si costruiscono (folla che cresce, freccia "da ... a ...", piramide)
- materiali del cliente (testimonianze, chat, foto, numeri) a schermo
- la frase "monta la mia VSL" in SKILL.md (con il passo 0: SKILL.md ha ancora vecchie modifiche non salvate, da sistemare prima)
