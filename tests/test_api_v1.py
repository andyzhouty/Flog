"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
from flask import url_for
from flask.globals import current_app
from flog.models import User
from tests.helpers import register, get_api_v1_headers
from flog import fakes as fake


def test_api_index(client):
    response = client.get("/api/v1/")
    data = response.get_json()
    assert data['api_version'] == '1.0'


def test_no_auth(client):
    response = client.get("/api/v1/post/1/")
    assert response.status_code == 401


def test_posts(client):
    register(email='user@example.com', password='1234',
             username='user', client=client)

    # test POST
    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers('user', '1234'),
        data=json.dumps(
            {'content': '<p>body of the post</p>',
             'title': 'hello',
             'private': False}
        )
    )
    assert response.status_code == 200
    data = response.get_json()
    post_id = data.get('id')
    assert post_id is not None
    assert data.get('content') == '<p>body of the post</p>'
    assert data.get('title') == 'hello'
    assert data.get('private') is False

    # test GET
    response = client.get(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    data = response.get_json()
    assert isinstance(data['author'], dict)
    assert data['author']['username'] == 'user'

    # test PUT
    data = {
        'title': 'a new title',
        'content': 'the new content',
        'private': True
    }
    response = client.put(
        f"/api/v1/post/{post_id}/",
        json=data,
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 200
    assert response.get_json().get('content') == data['content']

    response = client.patch(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.get_json()['private'] is False

    response = client.delete(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 404


def test_users(client):
    register(email='user@example.com', password='1234',
             username='user', client=client)
    user = User.query.filter_by(username='user').first()
    assert user is not None
    response = client.get(
        f"/api/v1/user/{user.id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    data = response.get_json()
    assert data['id'] == user.id
    assert data['username'] == user.username

    # test put method
    user_data = {
        'name': 'Real Name',
        'about_me': 'A test user.',
        'location': 'Shanghai'
    }
    response = client.put(
        f"/api/v1/user/{user.id}/",
        json=user_data,
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == user_data['name']
    assert data['about_me'] == user_data['about_me']
    assert data['location'] == user_data['location']

    # test delete method
    response = client.delete(
        f"/api/v1/user/{user.id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 200
    assert response.get_data(as_text=True) == f'User id {user.id} deleted.'
    assert User.query.get(user.id) is None


def test_notifications(client):
    fake.notifications(receiver=User.query.get(1), count=10)
    response = client.get(
        "/api/v1/notifications/unread/",
        headers=get_api_v1_headers(
            current_app.config['FLOG_ADMIN'],
            current_app.config['FLOG_ADMIN_PASSWORD']
        )
    )
    data = response.get_json()
    assert data.get('unread_num') == 10
    assert data.get('unread_num') == len(data.get('unread_items'))
    assert isinstance(data.get('unread_items')[1], list)


def test_comments(client):
    register(email='user@example.com', password='1234',
             username='user', client=client)
    # create a post first
    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers('user', '1234'),
        data=json.dumps(
            {'content': '<p>body of the post</p>',
             'title': 'hello',
             'private': False}
        )
    )
    assert response.status_code == 200
    data = response.get_json()
    post_id = data.get('id')
    
    # then create a comment
    data = {
        'body': 'comment content',
        'post_id': post_id
    }
    response = client.post(
        "/api/v1/comment/new/",
        data=json.dumps(data),
        headers=get_api_v1_headers('user', '1234')
    )
    assert response.status_code == 200
    comment_id = response.get_json().get('id')

    response = client.get(
        f"/api/v1/post/{post_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    data = response.get_json()
    print(data)
    comments =  data.get('comments')
    assert isinstance(comments, list)
    assert comments[0]['author'] == 'user'
    assert comments[0]['body'] == 'comment content'

    response = client.get(
        f"/api/v1/comment/{comment_id}/",
        headers=get_api_v1_headers('user', '1234')
    )
    data = response.get_json()
    assert data['author']['username'] == 'user'
    assert data['post']['id'] == post_id
    assert data['body'] == 'comment content'
