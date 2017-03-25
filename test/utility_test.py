import unittest
from src.util.utility import *
from main import CONFIG


class TestChapterIdsExtractor(unittest.TestCase):

    def test_none_url(self):
        url = None
        ret = extract_id(url)
        self.assertIsNone(ret)

    def test_blank_url(self):
        url = ''
        ret = extract_id(url)
        self.assertIsNone(ret)

    def test_no_match(self):
        url = '/substory.php?SID=&SubID='
        ret = extract_id(url)
        self.assertIsNone(ret)

    def test_matches(self):
        url = '/substory.php?SID=31321&SubID=64858'
        ret = extract_id(url)
        self.assertEqual(ret[0], '31321')
        self.assertEqual(ret[1], '64858')


class TestListDiffFunction(unittest.TestCase):

    def test_same_list(self):
        f = ['00001', '00002']
        s = ['00001', '00002']
        self.assertEqual(len(diff_list(f, s)), 0)

    def test_second_miss_from_first(self):
        f = ['00001', '00002']
        s = ['00001']
        d = diff_list(f, s)
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0], '00002')

    def test_second_has_more_than_first(self):
        f = ['00001', '00002']
        s = ['00001', '00002', '00003']
        d = diff_list(f, s)
        self.assertEqual(len(d), 0)

    def test_element_seq_is_irrelevant(self):
        f = ['00001', '00002', '00003']
        s = ['00002', '00003', '00001']
        d = diff_list(f, s)
        self.assertEqual(len(d), 0)


class TestConfigParser(unittest.TestCase):

    def test_load_complete(self):
        mail_to = CONFIG['mail.to']
        self.assertEqual(mail_to, 'ntin.nan@gmail.com,tin_nan@hotmail.com')


class TestGetOneDriveDir(unittest.TestCase):

    def test_get_onedrive_dir(self):
        dir = get_onedrive_dir()
        self.assertEqual(dir, "C:/Users/{}/OneDrive/comeon_scan".format(os.getlogin()))

    def test_get_follow_list_path(self):
        path = get_follow_list_path()
        self.assertEqual(path, "C:/Users/{}/OneDrive/comeon_scan/comeon_list.txt".format(os.getlogin()))

    def test_get_history_path(self):
        path = get_history_path()
        self.assertEqual(path, "C:/Users/{}/OneDrive/comeon_scan/comeon_history.json".format(os.getlogin()))

if __name__ == '__main__':
    unittest.main()
