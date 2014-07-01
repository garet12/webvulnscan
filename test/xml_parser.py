import unittest
import re


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

if __name__ == '__main__':
    unittest.main()


class XMLParser_test(unittest.TestCase):

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
