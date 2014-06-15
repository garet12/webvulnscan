import unittest
import tutil
import re
import time


def get_objects(xml_data):
    idx = 0
    while idx < len(xml_data):
        c = xml_data[idx]
        if c == '<' and re.match(r'!ENTITY', xml_data[idx + 1:]):
            ename = re.search(
                r'\s(\w+)', xml_data[idx + 1:]).group(1)
            evalue = re.search(r'"(.*)"', xml_data[idx + 1:]).group(1)
            endpos = xml_data.find('>', idx + 1)
            yield ('entity', (ename, evalue))

            idx += (endpos - idx)

        elif c == '&':
            endpos = xml_data.find(';', idx + 1)
            yield ('entity_reference', xml_data[idx + 1:endpos])

            idx += (endpos - idx)

        else:
            yield ('text', c)

        idx += 1


def get_xml_length(xml_data, entities={}):
    res = 0
    for otype, ovalue in get_objects(xml_data):
        if otype == 'entity':
            ename, evalue = ovalue
            entities[ename] = get_xml_length(evalue, entities)
        elif otype == 'entity_reference':
            res += entities[ovalue]
        else:  # text
            res += len(ovalue)
    return res


class BillionLaughsTest(unittest.TestCase):

    def test_empty(self):
        xml_doc = ''''''
        res = get_xml_length(xml_doc)
        self.assertEqual(res, 0)

    def test_lol1(self):
        xml_doc = '''
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<test>&lol1;</test>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(res >= 30)

    def test_no_reference(self):
        xml_doc = '''
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<test></test>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(res < 30)

    def test_lol1_multiple(self):
        xml_doc = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<test>&lol1;&lol1;&lol1;</test>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(res >= 90)

    def test_quadratic_blowup(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;&A;</payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(res >= 2000)

    def test_missing_bracket1(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA"
]>
<payload>&A;</payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(False)

    def test_missing_bracket2(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;</payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(False)

    def test_missing_semicolon(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A</payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(False)

    def test_missing_slash(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A "AAAAAAAAAAAAAAAAAAAAAAA">
]>
<payload>&A;<payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(False)

    def test_missing_quotes(self):
        xml_doc = '''
<?xml version="1.0"?>
<!DOCTYPE payload [
<!ENTITY A AAAAAAAAAAAAAAAAAAAAAAA>
]>
<payload>&A;</payload>
'''
        res = get_xml_length(xml_doc)
        self.assertTrue(False)

if __name__ == '__main__':
    f = open("testdoc", "r")
    xml_data = f.read()
    res = get_xml_length(xml_data)
    print str(res) + " Byte"
    res = res / float(2 ** 30)
    print str(res) + " GB"
    f.close()
    unittest.main()
