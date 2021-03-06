from __future__ import unicode_literals
import unittest
import re
import xml_parser
import tutil
import webvulnscan.attacks.billion_laughs
import socket
import time


try:
    from urllib.request import Request, URLError, HTTPError, urlopen
except ImportError:
    from urllib2 import Request, URLError, HTTPError, urlopen


def get_XML(url):
    if "http://" not in url:
        url = "http://" + url
    headers = {'Accept': 'application/xrds+xml'}
    req = Request(url, None, headers)

    try:
        response = urlopen(req)
    except (HTTPError, URLError):
        print(
            'There was a problem with your request!\n')
        return None

    html = response.read()
    xrds_loc = re.search(
        r'<meta\s+http-equiv="x-xrds-Location"\s+content="(?P<value>[^"]*)"\s*', html.decode(), re.IGNORECASE)

    if not xrds_loc:
        return None

    xrds_url = xrds_loc.group('value')

    try:
        xrds_doc = urlopen(xrds_url)
    except (HTTPError, URLError):
        print(
            'There was a problem with your request!\n')
        return None

    return xrds_doc.read()


def form_client(vulnerable=False):
    form = u'''<html><form action="./send" method="post">
                    <input name="openid" type="text">
                    <input type="submit" value="submit" >
                </form></html>'''

    def result(request):
        if 'openid' not in request.parameters:
            return u'<html>There is no input!</html>'

        xml = get_XML(request.parameters['openid'])

        if xml is None:
            return u'<html>XML document could not be found!</html>'

        res = xml_parser.get_xml_length(xml)

        timeout = getattr(request, 'timeout', None)
        if vulnerable:
            if not timeout:
                time.sleep(res / 100000)
            elif timeout < res:
                raise socket.timeout()

        return u'<html>%s</html>' % res

    return {
        '/': form,
        '/send': result,
    }


class billion_laughs(unittest.TestCase):
    attack = webvulnscan.attacks.billion_laughs

    @tutil.webtest(False)
    def test_billion_laughs_static_site():
        return {
            '/': u'''<html></html>''',
        }

    @tutil.webtest(False)
    def test_billion_laughs_form():
        return form_client()

    @tutil.webtest(True)
    def test_billion_laughs_dangerous():
        return form_client(True)
