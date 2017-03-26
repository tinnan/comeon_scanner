import json
import logging
import os.path
import re
import requests
from lxml import html
from initialize import CONFIG, APP_SYSTEM_ENV
from src.scan import selectors
from src.util import utility

CHAP_STAT_NOT = 0  # Not changed
CHAP_STAT_NEW = 1  # New chapter
CHAP_STAT_UPD = 2  # Updated chapter
CHAP_STAT_DEL = 3  # Deleted chapter

mod_logger = logging.getLogger('src.scan.scanner')


def get_page(sid):
    """
    Get page contents.
    :param sid: story id
    :return: page contents as byte code
    """
    page_url = CONFIG.config['comeon.story.url']
    if os.environ.get(APP_SYSTEM_ENV) == 'prod':
        return requests.get(page_url.format(str(sid))).content
    return None  # TODO change to return dummy comeon-book story page.


class Scanner:

    def __init__(self):
        self.logger = logging.getLogger('src.scan.scanner.Scanner')
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
                    self.logger.debug('------------------------------------------------------')
                    self.logger.debug('Get story page content from URL: %s', page_url)
                    page = requests.get(page_url.format(str(sid)))
                except:
                    self.logger.warning('Something went wrong while the program trying to open the URL: %s', page_url)
                    continue

                tree = html.fromstring(page.content)
                title_e = selectors.TITLE_SELECTOR(tree)
                if title_e and title_e[0] is not None:
                    title = title_e[0].text
                    self.logger.debug('Found story: %s', title)
                else:
                    self.logger.warning('Story title not found for story ID: %s, '
                                        'it is assumed that this story page does not actually exist.', sid)
                    continue

                chapter_table = selectors.CHAPTER_ROW_TBL_SELECTOR(tree)

                if chapter_table:
                    chapter_names = selectors.CHAPTER_SELECTOR(chapter_table[0])
                    chapter_dates = selectors.CHAPTER_DATE_SELECTOR(chapter_table[0])
                    chapter_links = selectors.CHAPTER_LINK_SELECTOR(chapter_table[0])
                    if chapter_names:
                        # Chapter count
                        chapter_count = len(chapter_names)
                        self.logger.debug('Found %s chapter for story ID: %s', chapter_count, sid)
                        # Chapter id list for checking deleted chapters.
                        chid_list = []
                        for i in range(chapter_count):
                            chapter_url = chapter_links[i].attrib['href']
                            chapter_name = chapter_names[i].text
                            chapter_date = chapter_dates[i].text[:8]  # substring only first 8 characters (date part)
                            # Get chapter id.
                            chapter_ids = utility.extract_id(chapter_url)
                            chid = chapter_ids[1]
                            chid_list.append(chid)

                            self.logger.debug('Checking CHID: %s', chid)
                            # Check chapter status.
                            chapter_status = history.chapter_status(sid, chid, chapter_name, chapter_date)
                            if chapter_status == CHAP_STAT_NOT:
                                self.logger.debug('No update in this chapter.')
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
                                             ''.join([self.config['comeon.base.url'], '/',
                                                      chapter_url]), chapter_status))

                        # Manage history, find deleted chapter.
                        del_chids = history.find_deleted_chapter(sid, chid_list)
                        if del_chids:
                            self.logger.debug('------------------------------------------------------')
                            self.logger.info('Found %s deleted chapters.', len(del_chids))
                            # Has chapter to delete.
                            for del_chid in del_chids:
                                history.del_chapter(sid, del_chid)  # Delete chapter.
        self.logger.debug('------------------------------------------------------')
        self.logger.info('Found %s chapters to notify.', len(notification_list))
        return notification_list


class Notification:

    def __init__(self, title, chapter, link, status):
        logger = logging.getLogger('src.scan.scanner.Notification')
        logger.debug('Creating notification...')
        self.title = title
        self.chapter = chapter
        self.link = link
        self.status = status
        logger.debug('Title: %s', title)
        logger.debug('Chapter: %s', chapter)
        logger.debug('Chapter url: %s', link)
        logger.debug('Status: %s', self.get_status())

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
        self.logger = logging.getLogger('src.scan.scanner.History')
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
        self.logger.debug('Adding new chapter for SID: %s and CHID: %s', sid, chid)
        if not self.has_sid(sid):
            self.logger.debug('Creating structure for new story...')
            self.obj[sid] = {}  # Initiate class structure for new story.
        if not self.has_chapter(sid, chid):
            self.logger.debug('Creating structure for new chapter...')
            self.obj[sid][chid] = {}  # Initiate class structure for new chapter.
        self.logger.debug('Set chapter = %s', chapter)
        self.logger.debug('Set date = %s', date)

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
            self.logger.debug('Updating chapter of SID: %s and CHID: %s', sid, chid)
            self.logger.debug('Set chapter = %s', chapter)
            self.logger.debug('Set date = %s', date)

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
            self.logger.debug('Deleting chapter of SID: %s amd CHID: %s', sid, chid)
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
    mod_logger.info('Loading following list from: %s', path)
    pattern = re.compile(r"^\d+$")
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            contents = f.readlines()
        # remove leading and trailing whitespace characters
        contents = [c.strip() for c in contents]

        follow_list = list(filter(lambda l: pattern.match(l) is not None, contents))
        if len(follow_list) == 0:
            mod_logger.info('Following list is empty.')
            return None
        else:
            mod_logger.info('Following list loading completed.')
            return follow_list
    else:
        mod_logger.info('Following list file does not exist.')
        return None  # follow list file does not exist


def load_history():
    """
    Load scanning history from file.
    :return: Dict object of history, None if file does not exist
    """
    path = utility.get_history_path()
    mod_logger.info('Loading scanning history from: %s', path)
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as json_data:
            h = json.load(json_data, encoding='utf-8')
            mod_logger.info('Scanning history loading completed.')
            return h
    else:
        mod_logger.info('Scanning history file does not exist.')
        return {}  # history file does not exist


def write_history(history):
    """
    Write history dict object to JSON file.
    :param history: history dict object
    :return:
    """
    path = utility.get_history_path()
    mod_logger.info('Writing scanning history to file: %s', path)
    with open(path, 'w', encoding='utf-8') as out_file:
        json.dump(history, out_file, indent=2, ensure_ascii=False)
    mod_logger.info('Writing scanning history completed.')
