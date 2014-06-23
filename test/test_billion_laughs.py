import unittest
import cgi
import sys

import tutil
import webvulnscan.attacks.billion_laughs


class billion_laughs(unittest.TestCase):
    attack = webvulnscan.attacks.billion_laughs

    @tutil.webtest(False)
    def test_billion_laughs_static_site():
        return {
            '/': u'''<html></html>''',
        }
