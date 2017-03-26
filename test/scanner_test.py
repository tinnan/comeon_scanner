import unittest

from src.scan.scanner import History, CHAP_STAT_UPD, CHAP_STAT_NEW, CHAP_STAT_NOT, load_follow_list, Scanner


def create_struct():
    return {
        "S0001": {
            "C0001": {
                "chapter": "s 1 - c 1",
                "date": "01-01-01"
            }
        },
        "S0002": {
            "C0004": {
                "chapter": "s 2 - c 1",
                "date": "04-01-01"
            },
            "C0005": {
                "chapter": "s 2 - c 2",
                "date": "05-01-01"
            },
            "C0006": {
                "chapter": "s 2 - c 3",
                "date": "06-01-01"
            },
            "C0007": {
                "chapter": "s 2 - c 4",
                "date": "07-01-01"
            }
        }
    }


def create_history():
    return History(create_struct())


class TestHistoryClass(unittest.TestCase):

    def setUp(self):
        self.his = create_history()

    def test_has_sid_invalid_sid(self):
        invalid_sid = 'S0003'
        self.assertFalse(self.his.has_sid(invalid_sid))

    def test_has_sid_valid_sid(self):
        valid_sid = 'S0002'
        self.assertTrue(self.his.has_sid(valid_sid))

    def test_has_chapter_invalid_sid(self):
        invalid_sid = 'S0003'
        chapter = 'C0001'
        self.assertFalse(self.his.has_chapter(invalid_sid, chapter))

    def test_has_chapter_invalid_chapter_id(self):
        valid_sid = 'S0002'
        invalid_chapter = 'C0008'
        self.assertFalse(self.his.has_chapter(valid_sid, invalid_chapter))

    def test_has_chapter_valid_chapter_id(self):
        valid_sid = 'S0002'
        valid_chapter = 'C0006'
        self.assertTrue(self.his.has_chapter(valid_sid, valid_chapter))

    def test_add_chapter_new_story(self):
        sid = 'S0003'
        chid = 'C0008'
        chapter = 's 3 - c 1'
        date = '08-01-01'
        self.his.add_chapter(sid, chid, chapter, date)
        self.assertEqual(len(self.his.get_history()[sid]), 1)
        self.assertEqual(self.his.get_history()[sid][chid]['chapter'], chapter)
        self.assertEqual(self.his.get_history()[sid][chid]['date'], date)

    def test_add_chapter_existing_story(self):
        sid = 'S0001'
        chid = 'C0002'
        chapter = 's 1 - c 2'
        date = '02-01-01'
        self.his.add_chapter(sid, chid, chapter, date)
        # chapter count is 2
        self.assertEqual(len(self.his.get_history()[sid]), 2)
        # assert chapter is not changed
        self.assertEqual(self.his.get_history()[sid]['C0001']['chapter'], 's 1 - c 1')
        self.assertEqual(self.his.get_history()[sid]['C0001']['date'], '01-01-01')
        # assert new chapter
        self.assertEqual(self.his.get_history()[sid][chid]['chapter'], chapter)
        self.assertEqual(self.his.get_history()[sid][chid]['date'], date)

    def test_upd_chapter(self):
        sid = 'S0002'
        chid = 'C0007'

        chapter = 's 2 - c 4'
        date = '07-01-01'

        new_chapter = 's 2 - c 5'
        new_date = '08-01-01'

        # first, assert current chapter data
        self.assertEqual(self.his.get_history()[sid][chid]['chapter'], chapter)
        self.assertEqual(self.his.get_history()[sid][chid]['date'], date)

        self.his.upd_chapter(sid, chid, new_chapter, new_date)
        # assert new chapter data
        self.assertEqual(self.his.get_history()[sid][chid]['chapter'], new_chapter)
        self.assertEqual(self.his.get_history()[sid][chid]['date'], new_date)

    def test_del_chapter(self):
        sid = 'S0001'
        chid = 'C0001'

        self.his.del_chapter(sid, chid)
        self.assertEqual(len(self.his.get_history()[sid]), 0)

    def test_chapter_count(self):
        sid = 'S0002'
        self.assertEqual(self.his.chapter_count(sid), 4)

    def test_chapter_status_not_change(self):
        sid = 'S0001'
        chid = 'C0001'
        chapter = 's 1 - c 1'
        date = '01-01-01'

        self.assertEqual(self.his.chapter_status(sid, chid, chapter, date), CHAP_STAT_NOT)

    def test_chapter_status_new(self):
        sid = 'S0001'
        chid = 'C0002'
        chapter = 's 1 - c 2'
        date = '02-01-01'

        self.assertEqual(self.his.chapter_status(sid, chid, chapter, date), CHAP_STAT_NEW)

    def test_chapter_status_update(self):
        sid = 'S0002'
        chid = 'C0007'
        chapter = 's 2 - c 5'
        date = '08-01-01'

        self.assertEqual(self.his.chapter_status(sid, chid, chapter, date), CHAP_STAT_UPD)

    def test_find_deleted_chapter(self):
        sid = 'S0002'
        chapters = ['C0004', 'C0005', 'C0008']
        del_chapters = self.his.find_deleted_chapter(sid, chapters)
        self.assertEqual(del_chapters[0], 'C0006')
        self.assertEqual(del_chapters[1], 'C0007')

    def test_get_history(self):
        self.assertEqual(self.his.get_history(), create_struct())


class TestLoadFollowList(unittest.TestCase):

    def test_load_follow_list(self):
        follow_list = load_follow_list()
        expected = ['11111', '22222', '33333', '55555']
        self.assertEqual(follow_list, expected)


class TestRunScanner(unittest.TestCase):

    def test_run(self):
        s = Scanner()
        h = History({})
        n = s.scan([30303], h)
        print(n)
        print(h)
