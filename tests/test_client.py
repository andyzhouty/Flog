"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import json
from random import randint
from faker import Faker
from flask import current_app, url_for
from flog import fakes
from flog.models import db, Post, Role, User
from flog.utils import lower_username
from .helpers import *

fake = Faker()


def test_login_logout(client):
    response = login(client)
    response_data = response.get_data(as_text=True)
    print(response_data)
    assert f'Welcome, Administrator\n {current_app.config["FLOG_ADMIN"]}' in response_data
    response = logout(client)
    assert 'You have been logged out' in response.get_data(as_text=True)


def test_fail_login(client):
    fail_login_res = login(client, password='wrongpassword')
    res_data = fail_login_res.get_data(as_text=True)
    assert 'Invalid username or password!' in res_data


def test_register_login_and_confirm(client):
    register(client)
    login_response = login(client, username='test', password='password')
    assert 'test' in login_response.get_data(as_text=True)
    user = User.query.filter_by(email='test@example.com').first()
    client.get(url_for('auth.confirm', token=user.generate_confirmation_token()),
               follow_redirects=True)
    assert user.confirmed


def test_create_article(client):
    data = create_article(client)
    response = data['response']
    post = data['post']
    assert Post.query.count() > 0
    response = client.get('/')
    response_data = response.get_data(as_text=True)
    assert post['title'] in response_data
    # test if filter 'striptag' work
    assert not(post['content'] in response_data)


def test_edit_profile(client):
    user = User(name='abcd', username='abcd', email='test@example.com', confirmed=True)
    user.role = Role.query.filter_by(name='User').first()
    user.set_password('123456')
    db.session.add(user)
    db.session.commit()
    login(client, username='abcd', password='123456')
    data = {
        'name': fake.name(),
        'location': fake.address(),
        'about_me': fake.sentence(),
    }
    response = client.post(url_for('user.edit_profile'), data=data, follow_redirects=True)
    print(response.get_data(as_text=True))
    user = User.query.filter_by(username='abcd').first()
    assert user.name == data['name']
    assert user.location == data['location']
    assert user.about_me == data['about_me']


def test_admin_edit_article(client):
    login(client)
    post_data = create_article(client)
    title = post_data['post']['title']
    post_id = Post.query.filter_by(title=title).first().id
    response = client.get(url_for('main.edit_post', id=post_id))
    response_data = response.get_data(as_text=True)
    # test if the old content exists in the edit page.
    assert post_data['text'] in response_data
    data = {
        'title': 'new title',
        'content': 'new content'
    }
    response = client.post(url_for('main.edit_post', id=post_id), data=data, follow_redirects=True)
    post = Post.query.get(post_id)
    assert post is not None
    assert post.title == data['title']


def test_admin_edit_user_profile(client):
    login(client)
    response = client.get(url_for('admin.manage_users'))
    assert response.status_code == 200
    user_id = randint(2, 11)
    data = {
        'email': fake.email(),
        'username': lower_username(fake.name()),
        'confirmed': bool(randint(0, 1)),
        'role': 1,
        'name': fake.name(),
        'location': fake.address(),
        'about_me': fake.text()
    }
    response = client.post(url_for('admin.edit_user_profile', id=user_id),
                           data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert data['email'] in response_data
    assert data['username'] in response_data
    assert data['about_me'] in response_data
    assert data['location'] in response_data


def test_send_feedback(client):
    login(client)
    data = {'body': fake.text(), }
    response = client.post(url_for('feedback.feedback'), data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert data['body'] in response_data


def test_change_theme(client):
    client.get(url_for('others.change_theme', theme_name='lite'), follow_redirects=True)
    cookie = next(
        (cookie for cookie in client.cookie_jar if cookie.name == "theme"),
        None
    )
    assert cookie is not None
    assert cookie.value == 'lite'


def test_delete_account(client):
    login(client)
    user_count = User.query.count()
    client.post(url_for('auth.delete_account'),
                data={'password': os.getenv('FLOG_ADMIN_PASSWORD')},
                follow_redirects=True)
    assert User.query.count() == user_count - 1


def test_language_selection(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    admin.locale = 'en_US'
    print(client.get(url_for('language.set_locale', locale='zh_Hans_CN'), follow_redirects=True).get_data(as_text=True))
    assert admin.locale == 'zh_Hans_CN'


def test_no_login_language_selection(client):
    client.get(url_for('language.set_locale', locale='zh_Hans_CN'), follow_redirects=True)
    data = client.get('/').get_data(as_text=True)
    assert '加入我们' in data


def test_collect_uncollect(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()

    post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    while post_not_private is None:  # ensure the post exists
        fakes.posts(2)
        post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    post_id = post_not_private.id
    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True).get_data(as_text=True)
    assert admin.is_collecting(post_not_private)

    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True).get_data(as_text=True)
    assert 'Already collected.' in data

    data = client.get(url_for('main.uncollect_post', id=post_id), follow_redirects=True).get_data(as_text=True)
    assert 'Post uncollected.' in data
    assert not admin.is_collecting(post_not_private)

    private_post = Post.query.filter(Post.author != admin, Post.private).first()
    while private_post is None:  # same as the while loop above
        fakes.posts(2)
        private_post = Post.query.filter(Post.author != admin, Post.private).first()
    post_id = private_post.id
    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True).get_data(as_text=True)
    assert 'The author has set this post to invisible. So you cannot collect this post.' in data
    assert not admin.is_collecting(private_post)

    title = create_article(client)['post']['title']
    post_id = Post.query.filter_by(title=title).first().id
    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True).get_data(as_text=True)
    assert 'You cannot collect your own post.' in data
    assert not admin.is_collecting(Post.query.get(post_id))


def test_follow(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    user = User.query.filter_by(
        role=Role.query.filter_by(
            name='User'
        ).first()
    ).first()
    data = client.post(url_for('user.follow', username=user.username), follow_redirects=True).get_data(as_text=True)
    assert 'User followed.' in data
    assert admin.is_following(user)
    data = client.post(url_for('user.follow', username=user.username), follow_redirects=True).get_data(as_text=True)
    assert 'Already followed' in data
    data = client.post(url_for('user.unfollow', username=user.username), follow_redirects=True).get_data(as_text=True)
    assert 'User unfollowed.' in data
    assert not admin.is_following(user)


def test_notification(client):
    login(client)
    for i in range(5):
        send_notification(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    assert len(admin.notifications) == 5
    assert Notification.query.filter_by(is_read=False).count() == 5
    str_data = client.get(url_for('ajax.notification_count')).get_data(as_text=True).strip()
    data = json.loads(str_data)
    assert dict(count=5) == data
    client.post(url_for('notification.read', id=1))
    assert Notification.query.filter_by(is_read=False).count() == 4
    client.post(url_for('notification.read_all'))
    assert Notification.query.filter_by(is_read=False).count() == 0
    str_data = client.get(url_for('ajax.notification_count')).get_data(as_text=True).strip()
    data = json.loads(str_data)
    assert dict(count=0) == data
