from configparser import ConfigParser, ExtendedInterpolation
import re
import os


def get_environ_param():
    """
    Get execution environment from system param 'COMEON_ENV'.
    :return: execution environment
    """
    return os.environ.get('COMEON_ENV')

# Simplified configuration dict.
# Contains only key-value, no need to specify section as sections are union together.
# Key-values from 'app' section are loaded first and they will be replaced by the same key-values
# from other section(depends on execution environment.
CONFIG = None
try:
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    parser.read('../conf/application.ini')
    CONFIG = parser['app']
    # Get OS environment for execution environment, which will be set in .BAT file.
    env_param = get_environ_param()
    if env_param is not None:
        env_section = parser[env_param]
        # Iterate through all config in the environment section.
        for e in list(enumerate(env_section)):
            key = e[1]
            value = env_section[key]
            CONFIG[key] = value  # Existing value will be replaced.
except:
    print('Application configuration file read failed.')
    exit(1)

# Secret configuration.
SECRET_CONFIG = ConfigParser()
try:
    SECRET_CONFIG.read('../conf/secret.ini')
except:
    print('Secret configuration file read failed. Make sure to run secret_setup.bat before starting the application.')
    exit(1)


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
