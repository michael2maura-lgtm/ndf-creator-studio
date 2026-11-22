# VSL orizzontale (16:9), versione semplice

Quando il cliente scrive "monta la mia VSL". Motore separato dai reel: `vsl_taglia.py`, `vsl_grafica.py`,
`vsl_monta.py`. I reel verticali (taglia.py, costruisci.py, grafica.py) non si toccano.

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
   - `riquadro`: 2-5 parole che riassumono la frase chiave, `*parola*` nel colore del brand. 3-4 secondi.
     Sulle promesse, sui numeri, sul nome del metodo. Una ogni 20-40 secondi al massimo: non su ogni frase.
   - `clip`: sopra la persona quando dice una cosa che si può far vedere (nel gancio soprattutto), 1,5-3 s.
     Prima il materiale del cliente, poi Pexels: `PY strumenti/clip.py <numero> <nome> --orizzontale` (1920x1080,
     fino a 8 s) e GUARDA i fotogrammi prima di usarla: deve mostrare quello che si dice, niente scritte in inglese.
     La persona resta in un riquadro piccolo in basso a destra (`"persona": false` per toglierla).
   - `numeri`: quando la persona elenca dei passi o dei punti. Le etichette sono le parole che dice lei nel video
     (da testo.txt), mai inventate né prese da altri video. Il riquadro della persona si adatta da solo (grande fino
     a 3 numeri, poi più piccolo); `"persona": "grande" / "media" / "piccola" / false` per sceglierlo. Una grafica per ogni passo detto, breve (4-6 s),
     con le voci già dette che restano (tempo prima di "da") e `"totale"` per tenere fermi i posti.
5. `PY strumenti/vsl_monta.py <nome> --anteprima` — foglio di fotogrammi presi dal montaggio vero
   (`controllo/foglio-vsl.jpg`). Guardalo TUTTO: scritte che coprono la bocca, testo tagliato, sottotitoli sopra le
   grafiche, tempi sbagliati. Correggi `vsl.json` e riprova: sono secondi, il video non si crea.
   Audio (di serie): musica bassa sotto tutta la VSL (22 dB sotto la voce, libreria DATI/musica; `"musica"` in
   vsl.json per un altro brano o false) e un "pop" quando compare ogni numero (`"suono_numeri"`).
   Colori: quelli del brand del cliente (DATI/profilo.json "colore"). Per una prova fatta per un cliente da questo
   computer: una cartella dati di prova con il suo colore e `NDF_STUDIO_DATI=<cartella>` davanti ai comandi, così
   il profilo di Michael resta com'è.
6. Solo quando il foglio è giusto: `PY strumenti/vsl_monta.py <nome>` — un render solo
   (`finale/<nome>-vN.mp4`, -14 LUFS, 8 Mbit/s). Per 15 minuti: circa 8-9 minuti di attesa.

Pochi token: niente render di prova del video intero. Si controlla sui fotogrammi, si crea una volta.

## Cosa manca (prossime sessioni)

- barra dei passaggi in basso con il passaggio attivo acceso
- "clicca il link qui sotto" alla fine
- materiali del cliente (testimonianze, chat, foto, numeri) a schermo
- la frase "monta la mia VSL" in SKILL.md
