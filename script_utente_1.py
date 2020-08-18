import http.server
import socketserver
from IPy import IP


def checkIP(ip, port):
    try:
        IP(ip)
        if port > 65535 or port < 0:
            print("Error format in PORT parameter")
            exit(1)
        return True
    except ValueError:
        print("Error format in IP parameter")
        exit(1)

def run():
    key = input("Insert your key: ")

    #it inserts the key in a paragraph of a 'index.html' file
    page_content = "<p>{}</p>".format(key)
    f = open("index.html", "w")
    f.write(page_content)
    f.close()

    insert = input("insert IP address (ip:port) : ")
    try:
        iport = insert.split(":")
        IP = iport[0]
        PORT = int(iport[1])
        checkIP(IP,PORT)
    except IndexError:
        print("You should insert an IP in the format ip:port (e.g. 127.0.0.1:5000)")
        exit(1)


    # An instance of TCPServer describes a server that uses the TCP protocol to send and receive messages
    # it needs of the TCP address (IP address and a port number) and the handler
    # Passing an empty string as the ip address means that the server will be listening on
    # any network interface (all available IP addresses).
    with socketserver.TCPServer((IP, PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        # serve_forever is a method on the TCPServer instance that starts the server and begins
        # listening and responding to incoming requests.
        # SimpleHTTPRequest is a default handler that search in the corrent directory a 'index.html' file
        # and serves it.
        print('\nStarting httpd...')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print('Stopping httpd...')

if __name__ == '__main__':
    run()