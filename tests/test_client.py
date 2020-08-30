from random import randint
import unittest
import os
from faker import Faker
from flask import escape
from sealog import create_app, db, fakes
from sealog.models import Post, Role, User
from sealog.utils import slugify

fake = Faker()


class ClientTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.admin = User(name='test', username='test',
                          email=os.getenv('ADMIN_EMAIL'), confirmed=True)
        self.admin.set_password('password')
        self.admin.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        db.session.remove()
        self.app_context.pop()

    def login(self):
        login_data = {
            'username_or_email': self.admin.email,
            'password': 'password',
            'remember_me': True
        }
        return self.client.post('/auth/login', data=login_data, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def create_article(self):
        self.login()
        text = fake.text()
        data = {
            'date': fake.date_time_this_year().strftime('%Y-%m-%d'),
            'title': fake.sentence(),
            'content': f"<p>{text}</p>",
        }
        return {
            'response': self.client.post('/write/', data=data, follow_redirects=True),
            'post': data,
            'text': text
        }

    def test_login_and_logout(self):
        response = self.login()
        response_data = response.get_data(as_text=True)
        self.assertTrue(response.status_code, 302)
        self.assertIn('Welcome, Administrator test', response_data)
        self.assertTrue(self.logout().status_code, 302)

    def test_create_article(self):
        data = self.create_article()
        response = data['response']
        post = data['post']
        text = data['text']
        self.assertTrue(response.status_code, 302)
        self.assertGreater(Post.query.count(), 0)
        response = self.client.get('/')
        response_data = response.get_data(as_text=True)
        self.assertIn(post['title'], response_data)
        # 测试striptags过滤器是否工作
        self.assertNotIn(post['content'], response_data)

    def test_post_slug(self):
        post = self.create_article()['post']
        slugified_title = slugify(post['title'])
        self.assertEqual(
            self.client.get(f'/post/{slugified_title}/').status_code, 200
        )

    def test_edit_profile(self):
        self.login()
        data = {
            'name': fake.name(),
            'location': fake.address(),
            'about_me': fake.sentence(),
        }
        response = self.client.post('/edit-profile', data=data, follow_redirects=True)
        self.assertTrue(response.status_code, 302)
        self.assertEqual(self.admin.name, data['name'])
        self.assertEqual(self.admin.location, data['location'])
        self.assertEqual(self.admin.about_me, data['about_me'])

    def test_admin_edit_article(self):
        self.login()
        old_content = escape(self.create_article()['text'])
        data = {
            'title': 'new title',
            'content': 'new content'
        }
        response = self.client.post('/posts/edit/1', data=data, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertNotIn(old_content, response_data)
        self.assertIn(data['content'], response_data)

    def test_admin_edit_user_profile(self):
        self.login()
        fakes.users(10)
        response = self.client.get('/admin/users/')
        self.assertEqual(response.status_code, 200)
        user_id = randint(2, 11)
        data = {
            'email': fakes.fake.email(),
            'username': slugify(fakes.fake.name()),
            'confirmed': bool(randint(0, 1)),
            'role': 1,
            'name': fakes.fake.name(),
            'location': fakes.fake.address(),
            'about_me': fakes.fake.text()
        }
        response = self.client.post(f'/admin/users/{user_id}/edit-profile',
                                    data=data, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertIn(data['email'], response_data)
        self.assertIn(data['username'], response_data)
        self.assertIn(data['about_me'], response_data)
        self.assertIn(data['location'], response_data)

    def test_send_feedback(self):
        self.login()
        data = {'body': fake.text(),}
        response = self.client.post('/feedback/', data=data, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertIn(data['body'], response_data)

    def test_change_theme(self):
        self.client.get('/change-theme/ubuntu', follow_redirects=True)
        cookie = next(
            (cookie for cookie in self.client.cookie_jar if cookie.name == "theme"),
            None
        )
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, 'ubuntu')
