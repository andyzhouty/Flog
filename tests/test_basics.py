import unittest
import logging
from flask import current_app
from sealog import create_app, db
from sealog.utils import slugify


class BasicsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertIsNotNone(current_app)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_slugify(self):
        string = "Andy Zhou"
        self.assertEqual(slugify(string), 'andy-zhou')
