import unittest
import re
import urllib2
import billion_laughs_test_app
import tutil
import webvulnscan.attacks.billion_laughs
import time
import xml.etree.ElementTree as ET


def get_XML(url):
        if "http://" not in url:
            url = "http://" + url
        headers = {'Accept': 'application/xrds+xml'}
        req = urllib2.Request(url, None, headers)

        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print(
                '%s There was a problem with your request!\n' % e.code)
            return None
        except urllib2.URLError, e:
            print('%s' % e.args)
            return None

        html = response.read()
        xrds_loc = re.search(
            r'<meta\s+http-equiv="x-xrds-Location"\s+content="(?P<value>[^"]*)"\s*', html, re.IGNORECASE)

        if xrds_loc:
            xrds_url = xrds_loc.group('value')

            try:
                xrds_doc = urllib2.urlopen(xrds_url)
            except urllib2.HTTPError, e:
                print(
                    '%s There was a problem with your request!\n' % e.code)
                return None
            except urllib2.URLError, e:
                print('%s' % e.args)
                return None

            return xrds_doc.read()

        else:
            return None


def form_client(vuln=False):
    form = u'''<html><form action="./send" method="post">
                    <input name="openid" type="text">
                    <input type="submit" value="submit" >
                </form></html>'''

    def result(req):
        if 'openid' in req.parameters:
            xml = get_XML(req.parameters['openid'])
            if xml is not None:
                res = billion_laughs_test_app.get_xml_length(xml)
                if vuln == True:
                    # ET.fromstring(xml)
                    time.sleep(res / 10000)
                return u'<html>%s</html>' % res
            else:
                return u'<html>XML document could not be found!</html>'
        else:
            return u'<html>There is no input!</html>'

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

