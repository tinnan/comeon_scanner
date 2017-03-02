import unittest
from cloud.mail import *
from scan.scanner import Notification, CHAP_STAT_UPD, CHAP_STAT_NEW


class TestTemplateEnvironment(unittest.TestCase):

    def test_load_template_complete(self):
        template = ENV.get_template('default.html')
        self.assertIsNotNone(template)

    def test_default_template(self):
        template = ENV.get_template('default.html')
        notifications = [
            Notification('Title 1', 'Chapter 1', 'www.dummy.com/story?sid=1&chid=1', CHAP_STAT_UPD),
            Notification('Title 1', 'Chapter 2', 'www.dummy.com/story?sid=1&chid=2', CHAP_STAT_NEW)
        ]
        rendered = template.render(notifications=notifications)
        expected = """\
<html>
    <head></head>
    <body>
        <p>Followed fiction update list.</p>
        <table>
            <thead>
                <tr>
                    <td>#</td>
                    <td>Story</td>
                    <td>Chapter</td>
                    <td>Status</td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Title 1</td>
                    <td><a href="www.dummy.com/story?sid=1&amp;chid=1">Chapter 1</a></td>
                    <td>Chapter updated</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Title 1</td>
                    <td><a href="www.dummy.com/story?sid=1&amp;chid=2">Chapter 2</a></td>
                    <td>New chapter</td>
                </tr>
            </tbody>
        </table>
    </body>
</html>"""

        self.assertEqual(expected, rendered)


class TestSendMail(unittest.TestCase):

    def test_send(self):
        notifications = [
            Notification('Title 1', 'Chapter 1', 'www.dummy.com/story?sid=1&chid=1', CHAP_STAT_UPD),
            Notification('Title 1', 'Chapter 2', 'www.dummy.com/story?sid=1&chid=2', CHAP_STAT_NEW)
        ]
        send_notification(notifications)


if __name__ == '__main__':
    unittest.main()
