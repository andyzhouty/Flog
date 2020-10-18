"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import unittest
import logging
from flask import current_app
from app import create_app, db
from app.utils import slugify


class BasicsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
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

    def test_about_us(self):
        response = self.client.get('/about-us')
        self.assertEqual(response.status_code, 200)

