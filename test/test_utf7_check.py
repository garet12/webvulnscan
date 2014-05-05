import unittest
import tutil
import webvulnscan.attacks.utf7_check


class UTF7_checkTest(unittest.TestCase):
    attack = webvulnscan.attacks.utf7_check

    @tutil.webtest(False)
    def test_utf7_check_static_site():
        return{
            '/': u'''<html></html>''',
        }

    @tutil.webtest(True)
    def test_utf7_check_dangerous():
        return{'/': (
            200, b'''<html></html>''',
            {'Content-Type': 'text/html; charset=UTF-7'}),
        }
