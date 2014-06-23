from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket
from urlparse import urlparse

PORT = 8080


class Handler(BaseHTTPRequestHandler):

    def _default_page(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>OpenID Test Server</title>
                <meta http-equiv="X-XRDS-Location" content="http://localhost:%i/serverxml">
            </head>
            <body>
                <h1>OpenID Test Server</h1>
            </body>
        </html>'''.encode("utf-8") % PORT)

    def _serve_request(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/":
            self._default_page()
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
        else: #quadratic blowup
            self.wfile.write(''' 
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;</payload>
'''.encode("utf-8"))

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

if __name__ == '__main__':
    main()
