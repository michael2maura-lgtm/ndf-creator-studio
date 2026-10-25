# Suoni: come si scelgono (vale per tutti gli stili)

La libreria è in `suoni/` (kit, mixkit, hyperframes). L'elenco numerato con il gruppo di ogni suono è
`suoni/catalogo-suoni.txt`. I preferiti dello stile stanno in `stili/<stile>/suoni/` e vincono sulla libreria.

Si sceglie in base a quello che viene detto e a quello che si vede in quel momento:
- **Transizioni:** la transizione dello stile, una volta sola quando entra ogni scena
  a tutto schermo: mai prima, mai al ritorno sulla persona.
- **Colpo basso:** solo nei 2-3 momenti più forti (il titolo del gancio, la frase chiave, il finale).
- **Suono di un oggetto:** ogni scena con un oggetto ha il suo suono, (chi guarda se ne accorge subito):
  soldi = cassa + monete, festa, porta, orologio = tic tac, ufficio/scrivania = tastiera, fabbrica, bollette = triste,
  domande e contatti = notifica, braccia in alto = "livello", X rossa = errore, schema = pop su ogni riquadro,
  elenchi = "livello" su ogni parola. Si mettono da soli (`strumenti/suoni_reel.py`); nel piano una scena può avere
  "suoni": [[file, ritardo, volume]] per sceglierli, o "suoni": [] per non averne.
- **Musica: dipende dal tipo di video, decidi tu.**
  - Video completo (scene a tutto schermo, transizioni, ritmo veloce): musica sotto per tutto il video, finale
    compreso, bassa. La voce resta sempre davanti.
  - Video parlato (la persona spiega un concetto in camera, solo sottotitoli e titoli): niente musica, e suoni
    pochissimi o nessuno.
  - Se l'utente lo dice ("con la musica", "senza musica", "monta semplice"), vale quello. Nel messaggio finale
    di' in una riga cosa hai scelto, così può cambiarlo.
- Mai due suoni forti nello stesso istante, mai un suono sopra una parola importante.

Volumi: effetti circa 7 dB sotto la voce, musica molto più bassa; il volume finale lo sistema `rendi.py` (-14 LUFS).

Se all'utente non piace un suono, si cambia solo quello, in quel video. Diventa una regola dello stile solo se dice
"sempre" o "d'ora in poi".
