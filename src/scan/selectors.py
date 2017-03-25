from lxml.cssselect import CSSSelector

TITLE_SELECTOR = CSSSelector('table:nth-child(5) '
                             'table:first-child '
                             'table:first-child '
                             'table:first-child '
                             'tr:first-child '
                             'td:first-child '
                             'b:first-child')
CHAPTER_ROW_TBL_SELECTOR = CSSSelector('table:nth-child(5) '
                               'table:first-child '
                               'table:first-child '
                               'table:first-child '
                               'tr:nth-child(2) '
                               'table')
CHAPTER_SELECTOR = CSSSelector('td:first-child > a > font')
CHAPTER_DATE_SELECTOR = CSSSelector('td:nth-child(2)')
CHAPTER_LINK_SELECTOR = CSSSelector('td:first-child > a')
