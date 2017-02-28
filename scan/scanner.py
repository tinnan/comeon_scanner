import requests
from util import utility
from lxml import html
from scan.selectors import *


class Scanner:

    def __init__(self):
        self.config = utility.CONFIG

    def scan(self, follow_list, history):
        # Load page URL from config.
        url = self.config['app']['comeon.story.url']
        # Initiate function result.
        notification_list = []
        if follow_list:
            for sid in follow_list:
                try:
                    page = requests.get(url.format(str(sid)))
                except:
                    print('Something went wrong while the program trying to open the URL. Try again later.')
                    continue

                tree = html.fromstring(page.content)
                title_e = TITLE_SELECTOR(tree)
                if title_e and title_e[0] is not None:
                    title = title_e[0].text
                else:
                    print('No title, assume that this story page does not actually exist.')
                    continue

                chapter_table = CHAPTER_ROW_TBL_SELECTOR(tree)

                if chapter_table:
                    chapter_names = CHAPTER_SELECTOR(chapter_table[0])
                    chapter_links = CHAPTER_DATE_SELECTOR(chapter_table[0])
                    if chapter_names:
                        # Chapter count
                        chapter_count = len(chapter_names)
                        # History chapter count
                        his_chap_count = history.chapter_count(sid)

                        for i in range(0, chapter_count - 1):
                            chapter_name = chapter_names[i].text
                            chapter_link = chapter_links[i].text
                            notification_list.append(Notification(title, chapter_name, chapter_link))

        if notification_list:
            return notification_list
        else:
            print('Nothing to notify.')
            exit(0)


class Notification:

    def __init__(self, title, chapter, link):
        self.title = title
        self.chapter = chapter
        self.link = link

    def get_title(self):
        return self.title

    def get_chapter(self):
        return self.chapter

    def get_link(self):
        return self.link
