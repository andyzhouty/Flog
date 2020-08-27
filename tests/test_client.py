import unittest
import os
from faker import Faker
from sealog import create_app, db
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
            'data': data,
            'text': text
        }

    def test_login_and_logout(self):
        response = self.login()
        response_data = response.get_data(as_text=True)
        self.assertTrue(response.status_code, 302)
        self.assertIn('Welcome, Administrator test', response_data)
        self.assertTrue(self.logout().status_code, 302)

    def test_create_article(self):
        response = self.create_article()['response']
        data = self.create_article()['data']
        self.assertTrue(response.status_code, 302)
        self.assertGreater(Post.query.count(), 0)
        response = self.client.get('/')
        response_data = response.get_data(as_text=True)
        self.assertIn(data['title'], response_data)
        # 测试striptags过滤器是否工作
        self.assertNotIn(data['content'], response_data)

    def test_post_slug(self):
        data = self.create_article()['data']
        slugified_title = slugify(data['title'])
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
        old_content = self.create_article()['text']
        data = {
            'content': fake.text()
        }
        response = self.client.post('/admin/posts/edit/1', data=data, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        # self.assertEqual(response.status_code, 302)
        self.assertNotIn(old_content, response_data)
        self.assertIn(data['content'], response_data)
