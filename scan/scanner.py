import requests
from util import utility
from lxml import html
from scan.selectors import *

CHAP_STAT_NOT = 0  # Not changed
CHAP_STAT_NEW = 1  # New chapter
CHAP_STAT_UPD = 2  # Updated chapter
CHAP_STAT_DEL = 3  # Deleted chapter


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

        return notification_list


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


class History:
    def __init__(self, obj):
        self.obj = obj

    def has_sid(self, sid):
        return self.obj.get(sid) is None

    def has_chapter(self, sid, chid):
        if not self.has_sid(sid):
            return False
        return self.obj.get(chid) is None

    def add_chapter(self, sid, chid, chapter, date):
        if not self.has_sid(sid):
            self.obj[sid] = {}  # Initiate class structure for new story.
        if not self.has_chapter(chid):
            self.obj[sid][chid] = {}  # Initiate class structure for new chapter.
        self.obj[sid][chid]['chapter'] = chapter
        self.obj[sid][chid]['date'] = date

    def del_chapter(self, sid, chid):
        if self.has_chapter(sid, chid):
            self.obj.get(sid).pop(chid)

    def chapter_count(self, sid):
        if not self.has_sid(sid):
            return 0
        else:
            return len(self.obj.get(sid))

    def chapter_status(self, sid, chid, chapter, date):
        if not self.has_chapter(sid, chid):
            return CHAP_STAT_NEW  # chapter does not exist in history = new chapter.
        # chapter exists,
        his_chapter = self.obj.get(sid).get(chid).get('chapter')
        his_date = self.obj.get(sid).get(chid).get('date')
        if his_chapter != chapter or his_date != date:
            return CHAP_STAT_UPD

    def find_deleted_chapter(self, sid, chid_list):
        # extract history chapter list
        his_chid_list = [e[1] for e in list(enumerate(self.obj.get(sid)))]
        return utility.diff_list(his_chid_list, chid_list)

    def get_history(self):
        return self.obj
