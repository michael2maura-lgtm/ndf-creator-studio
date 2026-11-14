"""Gli effetti (motion graphics) del motore "grafica": il catalogo che la pagina mostra, con le anteprime in
STUDIO/effetti/anteprime/<chiave>.mp4, e a quale elemento del piano corrisponde ognuno.

L'utente sceglie nella pagina quali effetti vuole nei suoi video (scelte.json "effetti"): Claude usa solo quelli,
e grafica.py salta, con una NOTA, un elemento del piano che non è tra gli scelti.
"""

# nomi generici degli effetti (Michael, 14/11/2026); "gruppo" = sezione della pagina Effetti
GRUPPI = ["Parole forti", "Numeri", "Elenchi", "Confronti", "Messaggi e app", "Mostrare qualcosa", "Tu", "Chiusura"]

CATALOGO = {
    "titolo": {"nome": "Titolo sul gancio", "gruppo": "Parole forti", "per": "Aprire il video, cambiare argomento",
               "descrizione": "Una riga bianca e una targa colorata che si decodificano lettera per lettera."},
    "gigante": {"nome": "Parola gigante", "gruppo": "Parole forti", "per": "Una svolta, una parola forte",
                "descrizione": "Fondo scuro, bande che passano e una parola enorme dentro una targa luminosa."},
    "chat": {"nome": "Chat che si scrive", "per": "Apri ChatGPT, scrivi, chiedi",
             "descrizione": "Entri in una cornice e sotto un messaggio si scrive da solo, lettera per lettera."},
    "passi": {"nome": "Passi", "per": "Un metodo, una sequenza",
              "descrizione": "Entri in una cornice e sotto una barra si riempie, un passo alla volta."},
    "contatore": {"nome": "Contatore", "per": "Un numero detto a voce",
                  "descrizione": "Un numero che sale fino a quello che dici, con le parole attorno."},
    "targhette": {"nome": "Targhette", "per": "Un elenco detto a voce",
                  "descrizione": "Etichette con un'icona che entrano una sotto l'altra mentre le nomini."},
    "dietro": {"nome": "Parola che sbatte", "gruppo": "Parole forti", "per": "Una frase che arriva a una parola forte",
               "descrizione": "La stanza si spegne, resti illuminato tu, la parola forte sbatte dietro la tua testa."},
    "adesivo": {"nome": "Adesivo di te", "gruppo": "Tu", "per": "Chiusura, invito all'azione, battuta",
                "descrizione": "L'immagine si ferma e diventi un adesivo su una pagina colorata, con le note scritte a mano."},
    "zoom": {"nome": "Zoom sul viso", "gruppo": "Tu", "per": "Ganci, parole forti, tenere l'attenzione",
             "descrizione": "Zoom che mirano al tuo viso: uno lento che entra, uno di scatto con la scia, uno che torna indietro."},
    "schermo": {"nome": "Sfondo dietro di me", "gruppo": "Mostrare qualcosa", "per": "Mostrare quello di cui parli",
                "descrizione": "Diventi piccolo in basso e dietro di te, a tutto schermo, c'è il video o la foto di cui parli."},
    "luce": {"nome": "Luce", "gruppo": "Parole forti", "per": "Un momento serio, una frase importante",
             "descrizione": "La stanza va al buio e fuori fuoco, resti tu nella luce e le parole importanti compaiono."},
    "commento": {"nome": "Commenta la parola", "gruppo": "Chiusura", "per": "Chiusura: commenta INFO",
                 "descrizione": "Sotto il mento la parola si scrive come un commento, parte con il cuore e arriva la tua risposta."},
    "numero": {"nome": "Numero gigante", "gruppo": "Numeri", "per": "Un numero importante",
               "descrizione": "Il numero che dici compare enorme sul petto, con una riga piccola sotto che cambia."},
    "etichette": {"nome": "Fermo con etichette", "gruppo": "Tu", "per": "Spiegare chi sei o cosa c'è in scena",
                  "descrizione": "L'immagine si ferma mentre continui a parlare e delle etichette numerate ti indicano."},
    "neon": {"nome": "Insegna al neon", "gruppo": "Parole forti", "per": "Una frase da ricordare",
             "descrizione": "La frase, scritta a mano, si accende come un neon sul muro accanto a te e la stanza si abbassa."},
    "percorso": {"nome": "Percorso", "gruppo": "Elenchi", "per": "Un metodo, dei passaggi",
                 "descrizione": "Si passa a un fondo scuro: un titolo in corsivo e i passi che scendono uno sotto l'altro, uniti da una linea."},
    "checklist": {"nome": "Lista che si spunta", "gruppo": "Elenchi", "per": "Passi detti uno dopo l'altro",
                  "descrizione": "Una scheda di vetro scuro: ogni passo si spunta in giallo quando lo dici, la barra si riempie."},
    "contachilometri": {"nome": "Numero che conta", "gruppo": "Numeri", "per": "Numeri: anni, clienti, risultati",
                        "descrizione": "Le cifre girano come un contachilometri fino al numero che dici, con l'etichetta sotto."},
    "pillole": {"nome": "Pillole", "gruppo": "Elenchi", "per": "Un elenco veloce",
                "descrizione": "Per ogni cosa che nomini compare una pillola con il bordo bianco, una accanto all'altra."},
    "prompt": {"nome": "Finestra che scrive", "gruppo": "Messaggi e app", "per": "Cosa scrivere a ChatGPT o a Claude",
               "descrizione": "Sul petto un riquadro di vetro e dentro si scrive da solo quello che dici di scrivere."},
    "telefono3d": {"nome": "Telefono", "gruppo": "Messaggi e app", "per": "Un'app, una chat, un risultato",
                   "descrizione": "Un telefono vero vola accanto a te e mostra la chat, con il bottone che viene toccato."},
    "orbita": {"nome": "Carte in orbita", "gruppo": "Mostrare qualcosa", "per": "Far vedere i tuoi reel, i tuoi lavori",
               "descrizione": "Le copertine dei tuoi reel ti girano attorno, passando dietro e davanti a te."},
    "caduta": {"nome": "Raffica di reel", "gruppo": "Mostrare qualcosa", "per": "A caso, in disordine, senza un piano",
               "descrizione": "Dei post finti cadono dall'alto accanto a te, girando, e restano storti come buttati lì."},
    "popup": {"nome": "Notifica", "gruppo": "Messaggi e app", "per": "Un'app, un messaggio, una cosa che nomini",
              "descrizione": "Scende una notifica come quelle del telefono, con l'icona, il nome e il messaggio, poi se ne va."},
    "bianconero": {"nome": "Bianco e nero", "gruppo": "Tu", "per": "Un momento serio, un prima e dopo",
                   "descrizione": "Il video perde i colori e resta in bianco e nero, poi i colori tornano con un lampo."},
    "targhetta": {"nome": "Targhetta in alto", "gruppo": "Parole forti", "per": "Dire subito di cosa parla il video",
                  "descrizione": "Sopra la testa un riquadro colorato con il tema del video su due righe, fisso fino alla fine."},
    "timbro": {"nome": "Timbro", "gruppo": "Parole forti", "per": "No, sbagliato, mito da smontare",
               "descrizione": "Un grosso timbro rosso sbatte storto sul petto con un colpo sordo: NO, A CASO, SBAGLIATO."},
    "segui": {"nome": "Segui", "gruppo": "Chiusura", "per": "Seguimi, finale del reel",
              "descrizione": "Sotto il mento spunta la scheda del tuo profilo con la tua foto: un tocco preme Segui e diventa Seguito."},
    "tessere": {"nome": "Tessere numerate", "gruppo": "Elenchi", "per": "Prima cosa, seconda cosa, 3 passi",
                "descrizione": "Per ogni punto dell'elenco una tessera con il numero grande spunta ad arco attorno alla testa."},
    "classifica": {"nome": "Classifica", "gruppo": "Confronti", "per": "Il modo migliore, cosa funziona di più",
                   "descrizione": "Una classifica S, A, B, C sotto il mento: sulla parola chiave la voce giusta vola su fino in cima."},
    "prima_dopo": {"nome": "Prima e dopo", "gruppo": "Confronti", "per": "Prima e dopo, com'era e com'è",
                   "descrizione": "Una linea bianca con la maniglia spazza lo schermo: dal prima, spento, al dopo, il tuo video vero."},
    "grafico": {"nome": "Grafico che sale", "gruppo": "Numeri", "per": "Crescita, risultati, contatti che salgono",
                "descrizione": "Dietro di te si disegna un grafico: la linea va piatta, poi sulla parola sale gialla fino in cima."},
    "muro": {"nome": "Muro di parole", "gruppo": "Mostrare qualcosa", "per": "Tutti ne parlano, tutti dicono che...",
             "descrizione": "Il muro dietro di te si riempie di titoli, chat e post che dicono tutti la stessa cosa."},
    "etichetta": {"nome": "Etichetta", "gruppo": "Tu", "per": "Il nome di una cosa, il tuo ruolo",
                  "descrizione": "Un cartellino giallo attaccato di fianco alla testa che ti segue quando ti muovi."},
    "mappa": {"nome": "Mappa", "gruppo": "Mostrare qualcosa", "per": "Dove si trova il tuo negozio o studio",
              "descrizione": "Dal basso sale una cartina vera della zona, il segnaposto rosso cade sul punto e sotto ci sono nome e indirizzo."},
    "barrate": {"nome": "Icone barrate", "gruppo": "Confronti", "per": "Senza questo, senza quello",
                "descrizione": "Spuntano i riquadri di alcuni programmi e una X disegnata a mano li cancella uno dopo l'altro."},
    "app": {"nome": "Davanti all'app", "gruppo": "Messaggi e app", "per": "Come si usa uno strumento: un'app, un sito, una chat",
            "descrizione": "Dietro di te scende lo schermo di un'app: il messaggio si scrive e parte, arriva la risposta, i passi si spuntano."},
    "telefono": {"nome": "Telefono", "per": "Instagram, storie, reel, app",
                 "descrizione": "Ti rimpicciolisci dentro lo schermo di un telefono, con i titoli sopra."},
    # nuovi (14/11/2026, strumenti/effetti_nuovi.py)
    "barra": {"nome": "Barra che si riempie", "gruppo": "Numeri", "per": "Posti limitati, quasi pieno, a che punto sei",
              "descrizione": "Una scheda con una barra del tuo colore che si riempie e la percentuale che sale."},
    "scontrino": {"nome": "Scontrino", "gruppo": "Numeri", "per": "Quanto costa, quanto risparmi, i conti",
                  "descrizione": "Sale uno scontrino: le voci compaiono una alla volta e il totale arriva in grande."},
    "carrello": {"nome": "Aggiungi al carrello", "gruppo": "Chiusura", "per": "Un prodotto, un corso, un'offerta con il prezzo",
                 "descrizione": "La scheda del prodotto con il prezzo: un dito tocca Aggiungi al carrello e diventa Aggiunto."},
    "sondaggio": {"nome": "Sondaggio", "gruppo": "Confronti", "per": "Lo fai anche tu? Domande al pubblico",
                  "descrizione": "Un sondaggio come quelli delle storie: le risposte si riempiono con le percentuali."},
    "voto": {"nome": "Voto con le stelle", "gruppo": "Numeri", "per": "Recensioni, quanto vale, il voto",
             "descrizione": "Le stelle si accendono una alla volta fino al voto."},
    "podio": {"nome": "Podio", "gruppo": "Elenchi", "per": "Terzo, secondo, primo: i migliori",
              "descrizione": "Salgono i gradini del podio dal terzo al primo, con i nomi sopra."},
    "top": {"nome": "Top 5 dal quinto al primo", "gruppo": "Elenchi", "per": "Classifica a posti, conto alla rovescia",
            "descrizione": "Di lato un elenco numerato che si accende dal quinto al primo mentre li dici."},
    "freccia": {"nome": "Freccia disegnata", "gruppo": "Tu", "per": "Io tre anni fa, guarda qui, sono io",
                "descrizione": "Una scritta a mano e una freccia che si disegna e ti indica."},
    "postit": {"nome": "Post-it", "gruppo": "Parole forti", "per": "Una regola, un promemoria, una frase da ricordare",
               "descrizione": "Un foglietto colorato si attacca storto e la frase si scrive a mano."},
    "citazione": {"nome": "Citazione", "gruppo": "Parole forti", "per": "Una frase famosa, una frase di un cliente",
                  "descrizione": "Una scheda con le virgolette grandi e la frase in corsivo elegante."},
}


# Doppioni: restano nel motore (lo Stile NDF Grafica pronto li usa, sono il suo aspetto) ma la pagina non li mostra,
# perché c'è la versione uguale al Creator Studio: passi -> checklist, contatore -> contachilometri / numero gigante,
# targhette -> pillole, chat -> prompt, telefono -> telefono 3D.
NASCOSTI = {"passi", "contatore", "targhette", "chat", "telefono"}


def chiave_di(elemento):
    """L'effetto a cui corrisponde un elemento del piano di grafica.py."""
    tipo = elemento["tipo"]
    if tipo == "cornice":
        return "passi" if elemento.get("passi") else "chat"
    return tipo
