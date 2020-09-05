import http.server
import socket
import socketserver
from IPy import IP


IP_SERVER = '131.114.192.146'
#'146.48.99.33' for virtual machine

#this function transform a row of a database in a dictionary type data
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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

key = input("Insert your key: ")

#it inserts the key in a paragraph of a 'index.html' file
page_content = "<html>\
                    <head>\
                        <title>IP01 challenge</title>\
                    </head>\
                    <body>\
                        <h3>The script was executed correctly. Please refresh your page for results.</h3>\
                        <!--{}-->\
                    </body>\
                </html>".format(key)

#this function get the ip address by the system
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page_content.encode("utf-8"))
        if (self.client_address[0] == IP_SERVER):
            print("Verification executed. Refresh your own page and check for results.")
            print("Press Ctrl+C to exit")

def run():
    IP = get_ip_address()
    print("Your IP: ", IP)
    PORT = 2323

    wanna_change = input("Port will be setted to 2323 by default, do you want to change it? (Y/n)\n")
    while wanna_change != 'y' and wanna_change != 'Y' and wanna_change != 'n' and wanna_change != 'N':
        print("Please click 'y' or 'n'")
        wanna_change = input("Port will be setted to 2323 by default, do you want to change it? "
                             "(Y/n)\n")
    if wanna_change == 'y' or wanna_change == 'Y':
        PORT = input("Insert port: ")
        checkIP(IP,int(PORT))

    # An instance of TCPServer describes a server that uses the TCP protocol to send and receive messages
    # it needs of the TCP address (IP address and a port number) and the handler
    # Passing an empty string as the ip address means that the server will be listening on
    # any network interface (all available IP addresses).
    try:
        with socketserver.TCPServer((IP, int(PORT)), MyHandler) as httpd:
            # serve_forever is a method on the TCPServer instance that starts the server and begins
            # listening and responding to incoming requests.
            # SimpleHTTPRequest is a default handler that search in the corrent directory a 'index.html' file
            # and serves it.
            print('\nStarting httpd...')
            print('Ongoing check...')
            print('This may take a few minutes (not more 30)')
            print('Please, be patient')
            print("We suggest you to try to access to the following page from an external "
                  "web net (e.g. 4G): http://{}:{}".format(IP, int(PORT)))
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            httpd.server_close()
            print('Stopping httpd...')
    except PermissionError:
        print("Permission denied. Try with another port.")

if __name__ == '__main__':
    run()