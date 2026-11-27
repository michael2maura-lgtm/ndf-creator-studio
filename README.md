# NDF Creator Studio

Claude monta i tuoi reel nel tuo stile. Registri il video, scrivi **"monta questo video"**, e ricevi il reel finito:
riprese sbagliate e pause tolte, sottotitoli in italiano, titoli, scene, suoni e musica, volume giusto per Instagram.

## Cosa ti serve
- Un computer **Mac** (macOS 13 o più recente) oppure **Windows** (10 o 11).
- **Claude Code**, dall'app Claude, scheda Code, con un piano **Pro o Max** (con il piano gratuito non funziona).
  L'app si scarica da claude.com/download.
- **Almeno 10 GB liberi** e internet per la prima installazione. Non serve installare nient'altro.

## Installazione nell'app Claude (una volta sola)

**Il modo più semplice:** apri l'app Claude, scheda **Code**, apri una chat nuova e incolla questo messaggio:

```
Installa per me lo studio video "NDF Creator Studio". Si trova su GitHub: michael2maura-lgtm/ndf-creator-studio. Se sul computer manca Git (succede su Windows), installalo prima tu con winget. Poi aggiungi il marketplace da GitHub (mai da un file ZIP) e installa il plugin ndf-creator-studio@ndf-creator-studio. Quando hai finito, dimmi solo: "Chiudi del tutto l'app Claude, riaprila, apri una chat nuova e scrivi: installa lo studio".
```

Clicca **Consenti** quando Claude chiede il permesso (su Windows, se compare "Vuoi consentire a questa app di
apportare modifiche?", clicca **Sì**). Poi chiudi del tutto l'app, riaprila, apri una chat nuova e scrivi
**installa lo studio**.

**Oppure con i pulsanti** (su Windows serve prima [Git](https://git-scm.com/download/win)):
1. Apri l'app Claude e vai nella scheda **Code**.
2. Clicca il **+** accanto alla casella dei messaggi, poi **Plugins**, poi **Browse plugins**.
3. In alto a destra clicca **Add**, poi **Add marketplace**, poi **Add from a repository**.
4. Incolla questo indirizzo e clicca **Sync**:

```
https://github.com/michael2maura-lgtm/ndf-creator-studio
```

5. Nella lista installa **NDF Creator Studio**.
6. Apri una **chat nuova** in Code e scrivi:

```
installa lo studio
```

Lo studio si prepara da solo: si scarica i suoi programmi (Python, Node e ffmpeg) in una cartella sua, senza
password e senza toccare il resto del computer. Poi ti fa due domande, dove metti le clip da montare e dove vuoi i
video finiti, e intanto scarica in sottofondo gli strumenti di montaggio (circa 2 GB, una volta sola). Quando Claude
chiede il permesso per i comandi dello studio, clicca **Consenti**.

Sulla Scrivania trovi l'icona **NDF Creator Studio**: doppio clic e si apre la pagina dove scegli il tuo stile.

## Il tuo primo reel
1. Metti il video nella cartella **NDF Creator Studio › 1 - Clip da montare** (nella tua cartella utente), oppure
   trascinalo direttamente nella chat.
2. Scrivi: **monta il video**.
3. In circa 10 minuti ricevi il reel. **Ascoltalo tu**: Claude non sente l'audio, e ti dice cosa controllare.
4. Vuoi cambiare qualcosa? Dillo con il secondo: "a 0:12 cambia la scritta", "togli la musica", "più veloce".
5. Quando lo approvi, il video, la copertina e la didascalia sono insieme in **NDF Creator Studio › 2 - Video
   finiti**.

## Per registrare bene
- **Spegni l'HDR** (iPhone: Impostazioni › Fotocamera › Registra video › Video HDR spento; Android: nelle
  impostazioni della fotocamera spegni l'HDR o "Video HDR10+"). Se te lo dimentichi,
  lo studio corregge i colori, ma senza è meglio.
- **Hai sbagliato una frase? Ripetila da capo** dopo un secondo di silenzio: lo studio tiene l'ultima presa buona.
- In verticale, con una luce costante. Se puoi, usa un microfono: la voce pulita fa metà della qualità.

## Se qualcosa non va
- **Qualcosa non funziona come prima**: scrivi **ripara lo studio**. Controlla tutto e rimette da solo quello che
  manca, senza toccare il tuo stile e i tuoi video.
- **Hai raggiunto il limite di utilizzo**: aspetta che si azzeri (l'app ti dice quando) e scrivi "continua".
- **Una frase è stata tagliata male**: dillo con il minuto, per esempio "a 0:05 manca 'e lo rifaccio'".

## Aggiornamenti
Quando esce una versione nuova, all'inizio di una chat Claude ti dice in una riga cosa cambia e ti chiede se
installarla. Rispondi sì, poi fai come ti dice Claude (chiudere e riaprire l'app). Puoi anche scrivere in qualsiasi
momento: **aggiorna lo studio**. Il tuo stile e i tuoi video restano dove sono.

## Installare dal Terminale (solo se usi Claude Code nel Terminale)
Incolla queste due righe nel Terminale (Mac) o in PowerShell (Windows), una alla volta, non dentro Claude. Su
Windows questa strada vuole prima [Git per Windows](https://git-scm.com/download/win).

```
claude plugin marketplace add michael2maura-lgtm/ndf-creator-studio
```

```
claude plugin install ndf-creator-studio@ndf-creator-studio
```

Poi apri Claude Code e scrivi **installa lo studio**.

---
NDF Creator Studio · Michael Maura, Networker del Futuro. Font inclusi con licenza SIL Open Font License.
Suoni e clip gratuiti scaricati da Mixkit, Pixabay e Pexels secondo le loro licenze.
