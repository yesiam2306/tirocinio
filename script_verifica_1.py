import requests
from bs4 import BeautifulSoup
import sqlite3

#this function transform a row of a database in a dictionary type data
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def run():

    #establishes a connection with the database
    conn = sqlite3.connect('HTTP01_challenge_db.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    #query to select the targets to delete
    query = "SELECT * " \
            "FROM IP_addresses " \
            "WHERE (verification = '' " \
                "AND trusted = 0 " \
                "AND datetime(creation, '+3 day') < datetime('now'))" \
                "OR (verification <> '' " \
                    "AND trusted = 0 " \
                    "AND datetime(verification, '+3 day') < datetime('now'))"
    to_delete = cur.execute(query).fetchall()
    #print(to_delete) #to debug
    for ip in to_delete:
        query = "DELETE FROM IP_addresses WHERE script_key = '{}'".format(ip["script_key"])
        cur.execute(query)
        conn.commit()

    #query to select the targets to verify
    query = "SELECT * FROM `IP_addresses` WHERE `verification` = ''"
    to_verify = cur.execute(query).fetchall()
    #print(to_verify) #to debug

    #for each result it goes to the URL of its IP address, and controls what it contains
    for ip in to_verify:
        # the target we want to open
        url = 'http://{}'.format(ip["IP_address"])

        # open with GET method
        resp = requests.get(url)

        # http_response 200 means OK status
        if resp.status_code == 200:
            print("Successfully opened the web page")

            # we need a parser,Python built-in HTML parser is enough .
            soup = BeautifulSoup(resp.text, 'html.parser')

            # l is the list which contains all the text
            l = soup.find("p")

            # l contains the text of the page. If it's equal to the script key stored in the database
            # the verification have been successful
            if str(l) == "<p>{}</p>".format(ip["script_key"]):
                #debug print("yes")

                #update the row setting `verification` and `trusted` attributes
                query = "UPDATE `IP_addresses` SET `verification` = CURRENT_DATE WHERE `script_key` = '{}'".format(
                    ip["script_key"])
                cur.execute(query)
                conn.commit()
                query = "UPDATE `IP_addresses` SET `trusted` = 1 WHERE `script_key` = '{}'".format(
                    ip["script_key"])
                cur.execute(query)
                conn.commit()

                '''---debug----
                query = "SELECT * FROM `IP_addresses`"
                debug = cur.execute(query).fetchall()
                print(debug)
                #------------'''
        else:
            print("Error")


if __name__ == '__main__':
    run()