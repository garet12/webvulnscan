import unittest
import tutil
import re
from collections import Counter


def XMLParser(xml):
    counter = 0
    entity = dict()
    if isinstance(xml, file):
        xml = xml.read()
    # Get the entity names and store them as keys
    entity_lines = re.findall(r"\<\!ENTITY(.*)\>", xml)
    print entity_lines
    # Get the entity values and count different elements of the value
    for elements in entity_lines:
        if "&" in elements.split(" ")[2] and ";" in elements.split(" ")[2]:
            keyvalues = re.findall(r"\&(\w+)\;", elements.split(" ")[2])
        else:
            keyvalues = re.findall(r"\"(\w+)\"", elements.split(" ")[2])
        entity.update({elements.split(" ")[1]: [keyvalues]})
        value_count = Counter(keyvalues)
        entity[elements.split(" ")[1]].append(value_count.items())
    print entity
    # print entity_lines
    # Go through every line of the XML File
    for lines in xml.split("\n"):
        print lines
        # Count every character
        counter += len(lines)
        # print entity
        for keys in entity.keys():
            # Check whether any of the stored keys can be found in one line
            linekeys = re.findall(r"\&(\w+)\;", lines)
            # If a stored key could be found in one of the lines and it is not
            # an entity declaration, it is probably an entity reference
            if keys in linekeys and "!ENTITY" not in lines:
                # Count the entity once again
                counter += len(entity[keys][0])
                for i in range(1, len(entity[keys])):
                    if entity[keys][i][0][0] in entity.keys():
                        current_key = entity[keys][i][0][0]
                        while current_key in entity.keys():
                            counter+=entity[keys][i][0][1]**entity[current_key][i][0][1]
                            current_key=entity[current_key][i][0][0]
                            # TODO Endlosschleife bei lol fixen
                            print current_key
                    print entity[keys][i][0][1]
    print counter


class BillionLaughsTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    # XMLParser("test test2 test3 lol23 232 3l123 <!--bla-->  <!DOCTYPE kaboom [<!ENTITY a \"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\">]>")
    f = open("testdoc", "r")
    XMLParser(f)
    f.close()
    # unittest.main()
    # Fuer mich relevant sind nur die ENTITYs und Kommentare, den Rest kann ich
    # einfach counten
