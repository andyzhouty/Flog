import unittest
import logging
from flask import current_app
from sealog import create_app, db, fakes
from sealog.models import Article, Feedback


class ModelsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        fakes.generate_fake_articles()
        fakes.generate_fake_feedbacks()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_articles_and_feedbacks_exists(self):
        self.assertGreater(len(Article.query.all()), 0)
        self.assertGreater(len(Feedback.query.all()), 0)
