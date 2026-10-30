"""Gli effetti (motion graphics) del motore "grafica": il catalogo che la pagina mostra, con le anteprime in
STUDIO/effetti/anteprime/<chiave>.mp4, e a quale elemento del piano corrisponde ognuno.

L'utente sceglie nella pagina quali effetti vuole nei suoi video (scelte.json "effetti"): Claude usa solo quelli,
e grafica.py salta, con una NOTA, un elemento del piano che non è tra gli scelti.
"""

CATALOGO = {
    "titolo": {"nome": "Titolo", "per": "Aprire il video, cambiare argomento",
               "descrizione": "Una riga bianca e una targa colorata che si decodificano lettera per lettera."},
    "gigante": {"nome": "Parola gigante", "per": "Una svolta, una parola forte",
                "descrizione": "Fondo scuro, bande che passano e una parola enorme dentro una targa luminosa."},
    "chat": {"nome": "Chat che si scrive", "per": "Apri ChatGPT, scrivi, chiedi",
             "descrizione": "Entri in una cornice e sotto un messaggio si scrive da solo, lettera per lettera."},
    "passi": {"nome": "Passi", "per": "Un metodo, una sequenza",
              "descrizione": "Entri in una cornice e sotto una barra si riempie, un passo alla volta."},
    "contatore": {"nome": "Contatore", "per": "Un numero detto a voce",
                  "descrizione": "Un numero che sale fino a quello che dici, con le parole attorno."},
    "targhette": {"nome": "Targhette", "per": "Un elenco detto a voce",
                  "descrizione": "Etichette con un'icona che entrano una sotto l'altra mentre le nomini."},
    "dietro": {"nome": "Parola dietro la testa", "per": "Una frase che arriva a una parola forte",
               "descrizione": "La stanza si spegne, resti illuminato tu, la parola forte sbatte dietro la tua testa."},
    "adesivo": {"nome": "Adesivo", "per": "Chiusura, invito all'azione, battuta",
                "descrizione": "L'immagine si ferma e diventi un adesivo su una pagina colorata, con le note scritte a mano."},
    "zoom": {"nome": "Zoom sul viso", "per": "Ganci, parole forti, tenere l'attenzione",
             "descrizione": "Zoom che mirano al tuo viso: uno lento che entra, uno di scatto con la scia, uno che torna indietro."},
    "schermo": {"nome": "Schermo dietro di te", "per": "Mostrare quello di cui parli",
                "descrizione": "Diventi piccolo in basso e dietro di te, a tutto schermo, c'è il video o la foto di cui parli."},
    "luce": {"nome": "Luce", "per": "Un momento serio, una frase importante",
             "descrizione": "La stanza va al buio e fuori fuoco, resti tu nella luce e le parole importanti compaiono."},
    "telefono": {"nome": "Telefono", "per": "Instagram, storie, reel, app",
                 "descrizione": "Ti rimpicciolisci dentro lo schermo di un telefono, con i titoli sopra."},
}


def chiave_di(elemento):
    """L'effetto a cui corrisponde un elemento del piano di grafica.py."""
    tipo = elemento["tipo"]
    if tipo == "cornice":
        return "passi" if elemento.get("passi") else "chat"
    return tipo
