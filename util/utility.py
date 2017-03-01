from configparser import ConfigParser, ExtendedInterpolation


CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
try:
    CONFIG.read('../conf/application.ini')
except:
    print('Application configuration file read failed.')
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
