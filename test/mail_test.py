import unittest
from cloud.mail import *


class TestTemplateEnvironment(unittest.TestCase):

    def test_load_template_complete(self):
        template = ENV.get_template('default.html')
        self.assertIsNotNone(template)

if __name__ == '__main__':
    unittest.main()
