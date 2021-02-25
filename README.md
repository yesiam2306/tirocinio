# tirocinio

da settare prima di iniziare

---------------------------------------------------------------------------------------------------------------
#se  si vuole modificare l'indirizzo a cui far arrivare le richieste GET e POST
FILE script_utente_1.py:riga 7
IP_SERVER = '<INDIRIZZO_SERVER>'

FILE settings.py:riga 2
FLASK_SERVER_NAME = '<INDIRIZZO_SERVER>'
---------------------------------------------------------------------------------------------------------------
#se si vuole impostare una porta default diversa dalla 2323
FILE app.py:riga 194 / FILE script_utente_1.py:righe 60,62 / FILE script_verifica_1.py:riga 54:
port = <PORTA_DEFAULT>
---------------------------------------------------------------------------------------------------------------
#se si vuole cambiare il limite massimo di tempo entro cui registrare N indirizzi IP
FILE app.py:riga 214  FILE script_verifica_1.py:riga 34:
"AND datetime(creation, '<TEMPO_LIMITE*>') > datetime('now')".format(username)).fetchall()

FILE script_verifica_1.py:riga 31:
"AND datetime(creation, '<TEMPO_LIMITE*>') < datetime('now'))"

FILE script_verifica_1.py:riga 34:
"AND datetime(verification, '<TEMPO_LIMITE*>') < datetime('now'))"

*la sintassi di sqlite3 prevede [+-][INT][unità temporale scritta al singolare] ad esempio '+3 day' però ho trovato commenti discordanti quindi un dubbio che per qualche 
caso come ad esempio secondi o millisecondi ci vada messo il plurale mi rimane lo stesso.
---------------------------------------------------------------------------------------------------------------
#se si vuole cambiare il limite massimo di indirizzi da poter registrare entro un certo lasso di tempo
FILE app.py:riga 215
if request and len(results) >= <NUM_MAX_INDIRIZZI>:
---------------------------------------------------------------------------------------------------------------
#se si vuole cambiare il nome al database, bisogna rimpiazzare ogni volta il nome "HTTP01_challenge_db.db'
FILE app.py:righe 159, 200, 231 / FILE script_verifica_1.py:riga 22
conn = sqlite3.connect('<DATABASE_NAME>')
---------------------------------------------------------------------------------------------------------------
#se si vuole togliere qualche altro carattere dai possibili per creare la key:
FILE app.py:riga 45:
key_characters = key_characters.replace("<CARATTERE>", "") #carattere di escape: \
---------------------------------------------------------------------------------------------------------------
#se si vuole modificare la lunghezza massima dell'username
FILE app.py:righe 155, 185: 
if type(username) != str or len(username) > LUNGHEZZA_MASSIMA:
---------------------------------------------------------------------------------------------------------------
#se si volesse modificare la lunghezza della chiave
FILE app.py:riga 221 
key = get_random_key(<LUNGHEZZA_CHIAVE>)
---------------------------------------------------------------------------------------------------------------
#se si volesse modificare il link per lo script
FILE app.py:riga 240
link = <LINK>
---------------------------------------------------------------------------------------------------------------
#se si volesse modificare il contenuto della pagina per l'utente 
riga 31
modificare il contenuto HTML
---------------------------------------------------------------------------------------------------------------


