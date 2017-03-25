import os
import re
import main


def diff_list(first, second):
    """
    ** Data type of elements in both list must matches.
    Ex 1.
        first = ['00001', '00002']
        second = ['00001']
        diff_list(first, second) -> ['00002']

    Ex 2.
        first = ['00001', '00002']
        second = ['00001', '00003']
        diff_list(first, second) -> ['00002']

    Ex 3.
        first = ['00001', '00002']
        second = ['00003', '00004']
        diff_list(first, second) -> ['00001', '00002']

    :param first: first list
    :param second: second list
    :return: diff list
    """
    second = set(second)
    return [item for item in first if item not in second]


def extract_id(chapter_url):
    """
    Extract story id and chapter id from chapter URL.
    :param chapter_url: chapter URL ex. /substory.php?SID=31321&SubID=64858
    :return: List, [0] = story id, [1] = chapter id | None
    """
    if chapter_url is None:
        return None
    chapter_pattern = re.compile(r"^.*=(\d+).*=(\d+)$")
    matched = chapter_pattern.match(chapter_url)
    if matched is None:
        return None
    ret = [matched.group(1), matched.group(2)]
    return ret


def get_onedrive_dir():
    return main.CONFIG['file.dir'].format(os.getlogin())


def get_follow_list_path():
    return get_onedrive_dir() + "/{}".format(main.CONFIG['file.name.follow_list'])


def get_history_path():
    return get_onedrive_dir() + "/{}".format(main.CONFIG['file.name.history'])
