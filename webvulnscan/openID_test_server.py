import socket
import multiprocessing
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

IP = "localhost"
PORT = 50161


class Handler(BaseHTTPRequestHandler):

    def _default_page(self, pageState="serverxml"):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>OpenID Test Server</title>
                <meta http-equiv="X-XRDS-Location" content="http://%s:%i/%s">
            </head>
            <body>
                <h1>OpenID Test Server</h1>
            </body>
        </html>'''.encode("utf-8") % (IP, PORT, pageState))

    def _serve_request(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/":
            self._default_page("serverxml")
        elif parsed_path.path == "/db":
            self._default_page("serverxml_dangerous_billion")
        elif parsed_path.path == "/dq":
            self._default_page("serverxml_dangerous_quadratic")
        elif parsed_path.path == "/serverxml":
            self.showServerXML(None)
        elif parsed_path.path == "/serverxml_dangerous_billion":
            self.showServerXML("dangerous_billion")
        elif parsed_path.path == "/serverxml_dangerous_quadratic":
            self.showServerXML("dangerous_quadratic")
        else:
            self.send_error(404, "File not Found!")

    def showServerXML(self, xmlState=None):
        self.send_response(200)
        self.send_header('Content-type', 'application/xrds+xml')
        self.end_headers()

        if xmlState is None:
            self.wfile.write('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type></Type>
      <URI></URI>
    </Service>

  </XRD>

</xrds:XRDS>
'''.encode("utf-8"))

        elif xmlState == "dangerous_billion":
            self.wfile.write('''\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ELEMENT lolz (#PCDATA)>
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>

    <Service priority="0">
      <Type></Type>
      <test>&lol9;</test>
      <URI></URI>
    </Service>

  </XRD>

</xrds:XRDS>
    '''.encode("utf-8"))
        else:  # quadratic blowup
            ent_a = "AAA" * 99999
            ref_a = "&A;" * 99999
            self.wfile.write('''\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE payload [
<!ENTITY A "%s">
]>
<payload>%s</payload>
'''.encode("utf-8") % (ent_a, ref_a))

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                return

            self._serve_request()
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return


def main():
    httpd = HTTPServer(("", PORT), Handler)
    httpd.serve_forever()


class OpenIDServer():

    class create_server():

        def __init__(self, config):
            # Random Port bei lokalem Test -> Wie bekomme ich den Port dann raus ?
            self.config = config
            if self.config:
                global IP, PORT
                IP = self.config[0]
                PORT = int(self.config[1])
            self.server = None
            self.benign_url = "http://%s:%i" % (IP, PORT)
            self.evil_urls = ("http://%s:%i/db" %
                             (IP, PORT), "http://%s:%i/dq" % (IP, PORT))

        def __enter__(self):
            self.server = multiprocessing.Process(target=main)
            self.server.start()
            self.server.join(0.001)
            return self

        def __exit__(self, type, value, traceback):
            self.server.terminate()


if __name__ == '__main__':
    main()
