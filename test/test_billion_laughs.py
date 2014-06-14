import unittest
import tutil
import re
from collections import Counter


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
    pass

if __name__ == '__main__':
    f = open("testdoc", "r")
    xml_data = f.read()
    res = get_xml_length(xml_data)
    print str(res) + " Byte"
    res = res / float(2 ** 30)
    print str(res) + " GB"
    f.close()
    # unittest.main()
