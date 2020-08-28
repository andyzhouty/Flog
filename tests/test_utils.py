import unittest
from sealog.utils import slugify


class UtilTestCase(unittest.TestCase):
    def test_slugify(self):
        string = "Andy Zhou"
        self.assertEqual(slugify(string), 'andy-zhou')
