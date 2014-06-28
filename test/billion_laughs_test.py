import unittest
import re
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket
from urlparse import urlparse
import cgi
import urllib2
import time
import xml.etree.ElementTree as ET


def get_objects(xml_data, allow_entity_def=True):
    idx = 0
    while idx < len(xml_data):
        c = xml_data[idx]
        if c == '<' and allow_entity_def:
            m = re.match(r'''(?x)
                !ENTITY\s+
                (?P<name>[a-zA-Z0-9_-]+)\s+
                "(?P<value>[^"]*)"\s*
                >
            ''', xml_data[idx + 1:])
            if m:
                value = get_objects(m.group('value'), allow_entity_def=False)
                yield ('entity', (m.group('name'), value))
                idx += len(m.group(0)) + 1
                continue

        if c == '&':
            endpos = xml_data.find(';', idx + 1)
            yield ('entity_reference', xml_data[idx + 1:endpos])

            idx = endpos

        else:
            yield ('text', c)

        idx += 1


def get_xml_length(xml_data):
    object_stream = get_objects(xml_data)
    return _calc_xml_length(object_stream, {})


def _calc_xml_length(object_stream, entities):
    res = 0
    for otype, ovalue in object_stream:
        if otype == 'entity':
            ename, evalue = ovalue
            entities[ename] = _calc_xml_length(evalue, entities)
        elif otype == 'entity_reference':
            res += entities[ovalue]
        else:  # text
            res += len(ovalue)
    return res


def _make_list(gen):
    gen = list(gen)
    return [
        (key, (val[0], _make_list(val[1])))
        if key == 'entity'
        else (key, val)
        for key, val in gen]


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
                <form name="input" action="/form" method="post">
                OpenID <input type="text" name="URL"></input>
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
            if field =='':
                continue
            xrds_doc = self.get_XML(form[field].value)

        if xrds_doc is not None:
            res = get_xml_length(xrds_doc)
            #ET.fromstring(xrds_doc)
            time.sleep(res/1000000)
            print res
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


class BillionLaughsTest(unittest.TestCase):

    def test_entity_parsing(self):
        self.assertEqual(
            _make_list(get_objects(
                '''<!ENTITY x "y" >''')),
            [('entity', ('x', [('text', 'y')]))]
        )

        self.assertEqual(
            _make_list(get_objects(
                '''&y;x''')),
            [('entity_reference', 'y'), ('text', 'x')]
        )

        self.assertEqual(
            _make_list(get_objects(
                '''&ya;x''')),
            [('entity_reference', 'ya'), ('text', 'x')]
        )

    def test_empty(self):
        xml_str = ''''''
        res = get_xml_length(xml_str)
        self.assertEqual(res, 0)

    def test_invalid_reference(self):
        xml_str = '&a;'
        self.assertRaises(BaseException, get_xml_length, xml_str)

    def test_lol1(self):
        xml_str = '''
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<test>&lol1;</test>
'''
        res = get_xml_length(xml_str)
        self.assertTrue(res >= 30)

    def test_no_reference(self):
        xml_str = '''
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<test></test>
'''
        res = get_xml_length(xml_str)
        self.assertTrue(res < 30)

    def test_lol1_multiple(self):
        xml_str = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<test>&lol1;&lol1;&lol1;</test>
'''
        res = get_xml_length(xml_str)
        self.assertTrue(res >= 90)

    def test_lol1_missing_semicolon(self):
        xml_str = '''
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol&lol&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<test>&lol1;</test>
'''
        self.assertRaises(BaseException, get_xml_length, xml_str)

    def test_quadratic_blowup(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;</payload>
'''
        res = get_xml_length(xml_str)
        self.assertTrue(res >= 2000)

    def test_missing_bracket1(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA"
]>
<payload>&A;</payload>
'''
        self.assertRaises(BaseException, get_xml_length, xml_str)

    def test_missing_bracket2(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;</payload>
'''
        self.assertRaises(BaseException, get_xml_length, xml_str)

    def test_missing_semicolon(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A</payload>
'''
        self.assertRaises(BaseException, get_xml_length, xml_str)

    def test_missing_slash(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;<payload>
'''
        res = get_xml_length(xml_str)
        self.assertTrue(res >= 23)

    def test_missing_quotes(self):
        xml_str = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A AAAAAAAAAAAAAAAAAAAAAAA>
]>
<payload>&A;</payload>
'''
        self.assertRaises(BaseException, get_xml_length, xml_str)

if __name__ == '__main__':
    # f = open("testdoc", "r")
    # xml_data = f.read()
    # res = get_xml_length(xml_data)
    # print str(res) + " Byte"
    # res = res / float(2 ** 30)
    # print str(res) + " GB"
    # f.close()
    # unittest.main()
    main()
