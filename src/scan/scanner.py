import json
import os.path
import re
import requests
from src.util import utility
from lxml import html
from src.scan import selectors
from main import CONFIG, get_environ_param

CHAP_STAT_NOT = 0  # Not changed
CHAP_STAT_NEW = 1  # New chapter
CHAP_STAT_UPD = 2  # Updated chapter
CHAP_STAT_DEL = 3  # Deleted chapter


def get_page(sid):
    """
    Get page contents.
    :param sid: story id
    :return: page contents as byte code
    """
    page_url = CONFIG.config['comeon.story.url']
    if get_environ_param() == 'prod':
        return requests.get(page_url.format(str(sid))).content
    return None  # TODO change to return dummy comeon-book story page.


class Scanner:

    def __init__(self):
        self.config = CONFIG

    def scan(self, follow_list, history):
        """
        Scan all followed thread in the following list.
        :param follow_list: following list
        :param history: scanning history object
        :return: notification list, the list could be blank
        """
        # Load page URL from config.
        page_url = self.config['comeon.story.url']
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
                title_e = selectors.TITLE_SELECTOR(tree)
                if title_e and title_e[0] is not None:
                    title = title_e[0].text
                else:
                    print('No title, assume that this story page does not actually exist.')
                    continue

                chapter_table = selectors.CHAPTER_ROW_TBL_SELECTOR(tree)

                if chapter_table:
                    chapter_names = selectors.CHAPTER_SELECTOR(chapter_table[0])
                    chapter_dates = selectors.CHAPTER_DATE_SELECTOR(chapter_table[0])
                    chapter_links = selectors.CHAPTER_LINK_SELECTOR(chapter_table[0])
                    if chapter_names:
                        # Chapter count
                        chapter_count = len(chapter_names)
                        # Chapter id list for checking deleted chapters.
                        chid_list = []
                        for i in range(chapter_count):
                            chapter_url = chapter_links[i].attrib['href']
                            chapter_name = chapter_names[i].text
                            chapter_date = chapter_dates[i].text[:8]  # substring only first 8 characters (date part)
                            # Get chapter id.
                            story_ids = utility.extract_id(chapter_url)
                            chid = story_ids[1]
                            chid_list.append(chid)
                            # Check chapter status.
                            chapter_status = history.chapter_status(sid, chid, chapter_name, chapter_date)
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
                                             ''.join([self.config['comeon.base.url'], '/', chapter_url]), chapter_status))

                        # Manage history, find deleted chapter.
                        del_chids = history.find_deleted_chapter(sid, chid_list)
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
        return self.obj.get(sid) is not None

    def has_chapter(self, sid, chid):
        """
        Check if the chapter exists in the story.
        :param sid: story id
        :param chid: chapter id
        :return: True if exists
        """
        if not self.has_sid(sid):
            return False
        return self.obj.get(sid).get(chid) is not None

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
        if not self.has_chapter(sid, chid):
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
        if self.has_sid(sid) and self.has_chapter(sid, chid):
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


def load_follow_list():
    """
    Load following list from file.
    :return: following list, None of there is none or file does not exist
    """
    path = utility.get_follow_list_path()
    pattern = re.compile(r"^\d+$")
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            contents = f.readlines()
        # remove leading and trailing whitespace characters
        contents = [c.strip() for c in contents]

        follow_list = list(filter(lambda l: pattern.match(l) is not None, contents))
        if len(follow_list) == 0:
            return None
        else:
            return follow_list
    else:
        return None  # follow list file does not exist


def load_history():
    """
    Load scanning history from file.
    :return: Dict object of history, None if file does not exist
    """
    path = utility.get_history_path()
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as json_data:
            return json.load(json_data, encoding='utf-8')
    else:
        return {}  # history file does not exist


def write_history(history):
    """
    Write history dict object to JSON file.
    :param history: history dict object
    :return:
    """
    path = utility.get_history_path()
    with open(path, 'w', encoding='utf-8') as out_file:
        json.dump(history, out_file, indent=2, ensure_ascii=False)
