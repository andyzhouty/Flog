import unittest
import logging
from app import create_app, db, fakes
from app.models import Post, User, Role


class ModelsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        fakes.users(10)
        fakes.posts(10)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_posts_and_feedbacks_exists(self):
        self.assertGreater(len(Post.query.all()), 0)

    def test_password_setter(self):
        u = User()
        u.set_password('hello')
        self.assertIsNotNone(u.password_hash)

    def test_password_verification(self):
        u = User()
        u.set_password('hello')
        self.assertTrue(u.verify_password('hello'))
        self.assertFalse(u.verify_password('bye'))

    def test_password_salts_are_random(self):
        u1 = User()
        u2 = User()
        u1.set_password('hello')
        u2.set_password('hello')
        self.assertNotEqual(u1.password_hash, u2.password_hash)

    def test_confirmation_token(self):
        u = User(email='test@example.com')
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
