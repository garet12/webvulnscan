import xml_parser
import re
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import socket
import cgi
import urllib2
import time


class Handler(BaseHTTPRequestHandler):

    def _default_page(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>BillionLaughsTest</title>
            </head>
            <body>
                <h1>BillionLaughsTest</h1>
                <form name="openid" action="/form" method="post">
                OpenID <input type="text" name="openid"></input>
                <input type="submit" value="Submit"></input>
                </form> 

            </body>
        </html>'''.encode("utf-8"))

    def _serve_request(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/":
            self._default_page()
        elif parsed_path.path == "/form":
            self.do_POST()
        else:
            self.send_error(404, "File not Found!")

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        for field in form.keys():
            self.wfile.write('\t%s=%s\n' % (field, form[field].value))
            if field == '':
                continue
            xrds_doc = self.get_XML(form[field].value)

        if xrds_doc is not None:
            res = xml_parser.get_xml_length(xrds_doc)
            time.sleep(res / 1000000)
            self.wfile.write('Result: %s\n' % res)

        else:
            self.wfile.write('XML document could not be found\n')

        return

    def get_XML(self, url):
        if "http://" not in url:
            url = "http://" + url
        headers = {'Accept': 'application/xrds+xml'}
        req = urllib2.Request(url, None, headers)

        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            self.wfile.write(
                '%s There was a problem with your request!\n' % e.code)
            return None
        except urllib2.URLError, e:
            self.wfile.write('%s' % e.args)
            return None

        html = response.read()
        xrds_loc = re.search(
            r'<meta\s+http-equiv="x-xrds-Location"\s+content="(?P<value>[^"]*)"\s*', html, re.IGNORECASE)

        if xrds_loc:
            xrds_url = xrds_loc.group('value')

            try:
                xrds_doc = urllib2.urlopen(xrds_url)
            except urllib2.HTTPError, e:
                self.wfile.write(
                    '%s There was a problem with your request!\n' % e.code)
                return None
            except urllib2.URLError, e:
                self.wfile.write('%s' % e.args)
                return None

            return xrds_doc.read()

        else:
            return None

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
    httpd = HTTPServer(("", 8000), Handler)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
