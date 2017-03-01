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
        page_url = self.config['app']['comeon.story.url']
        # Initiate function result.
        notification_list = []
        if follow_list:
            for sid in follow_list:
                try:
                    # TODO should be able to inject page content according to execution environment
                    page = requests.get(page_url.format(str(sid)))
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
                    chapter_dates = CHAPTER_DATE_SELECTOR(chapter_table[0])
                    chapter_links = CHAPTER_LINK_SELECTOR(chapter_table[0])
                    if chapter_names:
                        # Chapter count
                        chapter_count = len(chapter_names)
                        # Chapter id list for checking deleted chapters.
                        chid_list = []
                        for i in range(0, chapter_count - 1):
                            chapter_url = chapter_links[i].attr['href']
                            chapter_name = chapter_names[i].text
                            chapter_date = chapter_dates[i].text
                            # Get chapter id.
                            story_ids = utility.extract_id(chapter_url)
                            chid = story_ids[1]
                            chid_list.append(chid)
                            # Check chapter status.
                            chapter_status = history.chapter_status(sid, chid)
                            if chapter_status == CHAP_STAT_NOT:
                                continue  # No update, continue to next chapter.
                            elif chapter_status == CHAP_STAT_NEW:
                                # Manage history, add new chapter.
                                history.add_chapter(sid, chid, chapter_name, chapter_date)
                            else:
                                # Manage history, update chapter.
                                history.upd_chapter(sid, chid, chapter_name, chapter_date)

                            # Build notification list.
                            notification_list.append(
                                Notification(title, chapter_name,
                                             self.config['app']['comeon.base.url'].format(chapter_url)))

                        # Manage history, find deleted chapter.
                        del_chids = history.find_deleted_chapter(chid_list)
                        if del_chids:
                            # Has chapter to delete.
                            [history.del_chapter(sid, del_chid) for del_chid in del_chids]  # Delete chapter.

        return notification_list


class Notification:

    def __init__(self, title, chapter, link, status):
        self.title = title
        self.chapter = chapter
        self.link = link
        self.status = status

    def get_title(self):
        return self.title

    def get_chapter(self):
        return self.chapter

    def get_link(self):
        return self.link

    def get_status(self):
        if self.status == CHAP_STAT_NOT:
            return 'No update'
        elif self.status == CHAP_STAT_NEW:
            return 'New chapter'
        elif self.status == CHAP_STAT_UPD:
            return 'Chapter updated'
        else:
            return 'Chapter deleted'


class History:
    def __init__(self, obj):
        self.obj = obj

    def has_sid(self, sid):
        """
        Check if the story exists in history.
        :param sid: story id
        :return: True if exists
        """
        return self.obj.get(sid) is None

    def has_chapter(self, sid, chid):
        """
        Check if the chapter exists in the story.
        :param sid: story id
        :param chid: chapter id
        :return: True if exists
        """
        if not self.has_sid(sid):
            return False
        return self.obj.get(chid) is None

    def add_chapter(self, sid, chid, chapter, date):
        """
        Add new chapter to the story, new story is created if not exists already.
        :param sid: story id
        :param chid: chapter id
        :param chapter: chapter title
        :param date: chapter update date
        :return:
        """
        if not self.has_sid(sid):
            self.obj[sid] = {}  # Initiate class structure for new story.
        if not self.has_chapter(chid):
            self.obj[sid][chid] = {}  # Initiate class structure for new chapter.
        self.obj[sid][chid]['chapter'] = chapter
        self.obj[sid][chid]['date'] = date

    def upd_chapter(self, sid, chid, chapter, date):
        """
        Update existing chapter history.
        :param sid: story id
        :param chid: chapter id
        :param chapter: chapter title
        :param date: chapter update date
        :return:
        """
        if self.has_sid(sid) and self.has_chapter(chid):
            # Do update
            self.obj[sid][chid]['chapter'] = chapter
            self.obj[sid][chid]['date'] = date

    def del_chapter(self, sid, chid):
        """
        Delete the chapter from history
        :param sid: story id
        :param chid: chapter id
        :return:
        """
        if self.has_chapter(sid, chid):
            self.obj.get(sid).pop(chid)

    def chapter_count(self, sid):
        """
        Count chapter in the given story id.
        :param sid: story id
        :return: Chapter count, zero if not found story
        """
        if not self.has_sid(sid):
            return 0
        else:
            return len(self.obj.get(sid))

    def chapter_status(self, sid, chid, chapter, date):
        """
        Check chapter status by checking with data in history.
        This function could check for 'New' or 'Updated' or 'No update' chapter only.
        :param sid: story id
        :param chid: chapter id
        :param chapter: chapter title
        :param date: chapter update date
        :return: chapter status
        """
        if not self.has_chapter(sid, chid):
            return CHAP_STAT_NEW  # chapter does not exist in history = new chapter.
        # chapter exists,
        his_chapter = self.obj.get(sid).get(chid).get('chapter')
        his_date = self.obj.get(sid).get(chid).get('date')
        if his_chapter != chapter or his_date != date:
            return CHAP_STAT_UPD  # chapter is updated.
        return CHAP_STAT_NOT

    def find_deleted_chapter(self, sid, chid_list):
        """
        Compare history and present chapter list and extract chapter that misses from history.
        :param sid: story id
        :param chid_list: chapter id
        :return: list of missing chapter from last check
        """
        # extract history chapter list
        his_chid_list = [e[1] for e in list(enumerate(self.obj.get(sid)))]
        return utility.diff_list(his_chid_list, chid_list)

    def get_history(self):
        """
        Get wrapped history object structure.
        :return: wrapped history object
        """
        return self.obj
