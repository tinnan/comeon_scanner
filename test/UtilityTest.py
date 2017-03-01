import unittest
from util.utility import *


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
        mail_to = CONFIG['app']['mail.to']
        self.assertEqual(mail_to, 'ntin.nan@gmail.com,\ntin_nan@hotmail.com')

if __name__ == '__main__':
    unittest.main()