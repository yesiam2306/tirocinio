import requests
from bs4 import BeautifulSoup, Comment
import sqlite3
import socket

#this function transform a row of a database in a dictionary type data
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def run():
    print(get_ip_address())
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
        try:
            iport = ip["IP_address"].split(":")
            PORT = int(iport[1])
        except IndexError:
            url = url + ':2323'
        print(url)

        try:
            # open with GET method
            resp = requests.get(url)
        except requests.exceptions.ConnectionError:
            continue
        # http_response 200 means OK status
        if resp.status_code == 200:
            print("Successfully opened the web page")

            # we need a parser,Python built-in HTML parser is enough .
            soup = BeautifulSoup(resp.text, 'html.parser')

            # l is the list which contains all the text
            for comments in soup.findAll(text=lambda text: isinstance(text, Comment)):
                c = comments.extract()
            #print(c)
            #print("{}".format(ip["script_key"]))

            # l contains the text of the page. If it's equal to the script key stored in the database
            # the verification have been successful
            if str(c) == "{}".format(ip["script_key"]):
                #print("yes")
                #update the row setting `verification` and `trusted` attributes
                query = "UPDATE `IP_addresses` SET `verification` = CURRENT_DATE WHERE `script_key` = '{}'".format(
                    ip["script_key"])
                cur.execute(query)
                #conn.commit()
                query = "UPDATE `IP_addresses` SET `trusted` = 1 WHERE `script_key` = '{}'".format(
                    ip["script_key"])
                cur.execute(query)
                conn.commit()
        else:
            print("Error")


if __name__ == '__main__':
    run()