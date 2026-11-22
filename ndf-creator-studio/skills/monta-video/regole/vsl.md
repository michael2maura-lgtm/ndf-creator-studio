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
- la frase "monta la mia VSL" in SKILL.md
