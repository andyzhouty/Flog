from random import randint
import unittest
import time
from faker import Faker
from flask import escape
from app import create_app, db, fakes
from app.models import Post, Role, User
from app.utils import slugify

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
                          email='test@example.com', confirmed=True)
        self.admin.set_password('password')
        self.admin.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        db.session.remove()
        self.app_context.pop()

    def login(self, email='test@example.com', password='password'):
        login_data = {
            'username_or_email': email,
            'password': password,
            'remember_me': True
        }
        return self.client.post('/auth/login/', data=login_data, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout/', follow_redirects=True)

    def register(self):
        register_data = {
            'email': 'test2@example.com',
            'name': 'Test3',
            'username': 'test3',
            'password': 'abcd1234',
            'password_again': 'abcd1234'
        }
        return {
            'data': register_data,
            'response': self.client.post('/auth/register/', data=register_data, follow_redirects=True)
        }

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
        response = self.logout()
        self.assertIn('You have been logged out', response.get_data(as_text=True))

    def test_fail_login(self):
        fail_login_res = self.login(password='wrongpassword')
        res_data = fail_login_res.get_data(as_text=True)
        self.assertIn('Invalid username or password!', res_data)

    def test_register_login_and_confirm(self):
        self.client.get('/auth/register/')
        reg = self.register()
        login_response = self.login(
            email=reg['data']['email'], password=reg['data']['password'])
        self.assertIn(reg['data']['name'], login_response.get_data(as_text=True))
        user = User.query.filter_by(email=reg['data']['email']).first()
        self.client.get(f'/auth/confirm/{user.generate_confirmation_token()}/', follow_redirects=True)
        self.assertTrue(user.confirmed)

    def test_create_article(self):
        data = self.create_article()
        response = data['response']
        post = data['post']
        self.assertTrue(response.status_code, 302)
        self.assertGreater(Post.query.count(), 0)
        response = self.client.get('/')
        response_data = response.get_data(as_text=True)
        self.assertIn(post['title'], response_data)
        # test if filter 'striptag' work
        self.assertNotIn(post['content'], response_data)

    def test_post_slug(self):
        post = self.create_article()['post']
        slugified_title = slugify(post['title'])
        self.assertEqual(
            self.client.get(f'/post/{slugified_title}/').status_code, 200
        )

    def test_edit_profile(self):
        user = User(name='abcd', username='abcd', email='test@example.com', confirmed=True)
        user.role = Role.query.filter_by(name='User').first()
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        self.login('abcd', '123456')
        data = {
            'name': fake.name(),
            'location': fake.address(),
            'about_me': fake.sentence(),
        }
        response = self.client.post('/edit-profile', data=data, follow_redirects=True)
        self.assertTrue(response.status_code, 302)
        user = User.query.filter_by(username='abcd').first()
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.location, data['location'])
        self.assertEqual(user.about_me, data['about_me'])

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
        self.client.get('/change-theme/lite', follow_redirects=True)
        cookie = next(
            (cookie for cookie in self.client.cookie_jar if cookie.name == "theme"),
            None
        )
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, 'lite')

    def test_delete_account(self):
        self.login()
        self.client.post('/auth/delete-account/', data={'password': 'password'}, follow_redirects=True)
        self.assertEqual(User.query.count(), 0)
