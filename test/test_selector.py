import requests
from xml.dom import minidom
from xml.etree import ElementTree
from src.scan import selectors
from lxml import html
from lxml.cssselect import CSSSelector

if __name__ == '__main__':
    page = requests.get('http://www.comeon-book.com/comeonv3/story.php?SID={}'.format(31571))
    tree = html.fromstring(page.content)
    selector = CSSSelector('table:nth-child(5) '
                'table:first-child '
                'table:first-child '
                'table:first-child '
                'tr:nth-child(2) ')
    el = selector(tree)

    for e in el:
        print(minidom.parseString(ElementTree.tostring(e)).toprettyxml(indent="   "))
        for i in selectors.CHAPTER_SELECTOR(e):
            print(i.text)
