from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

'''
page_html = "<html>\
                        <head>\
                            <title>IP01 challenge</title>\
                        </head>\
                        <body>\
                            <p>Your IP is not verified yet.</p>\
                            <p>Your key is: {} </p>\
                        </body>\
                    </html>".format(key)
'''


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()


    def do_POST(self):
        key = input("Insert your key: ")
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self.wfile.write("Your IP address is not verified yet\n".format(key).encode('utf-8'))
        self.wfile.write("Your key is: {}\n".format(key).encode('utf-8'))
        self.wfile.write("".encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()