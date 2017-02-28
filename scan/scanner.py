import requests
from lxml import html
from scan.selectors import *

pageId = 31304

try:
    page = requests.get("http://www.comeon-book.com/comeonv3/story.php?SID=" + str(pageId))
except:
    print("Something went wrong while the program trying to open the URL. Try again later.")
    exit(1)

tree = html.fromstring(page.content)
title = TITLE_SELECTOR(tree)
if title and title[0] is not None:
    print("Title=" + title[0].text)
else:
    print("No title, assume that this story page does not actually exist.")
    exit(1)

chapterTable = CHAPTER_ROW_TBL_SELECTOR(tree)
if chapterTable:
    [print(e2.text) for e2 in CHAPTER_SELECTOR(chapterTable[0])]
    [print(e3.text) for e3 in CHAPTER_DATE_SELECTOR(chapterTable[0])]
