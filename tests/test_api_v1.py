"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
from flask import url_for
from tests.helpers import register, get_api_v1_headers


def test_api_index(client):
    response = client.get(url_for('api_v1.index'))
    data = response.get_json()
    assert data['api_version'] == '1.0'


def test_no_auth(client):
    response = client.get(url_for('api_v1.post', post_id=1))
    assert response.status_code == 401


def test_posts(client):
    register(email='user@example.com', password='1234',
             username='user', client=client)
    response = client.post(
        url_for('api_v1.new_post'),
        headers=get_api_v1_headers('user', '1234'),
        data=json.dumps(
            {'content': '<p>body of the post</p>',
             'title': 'hello',
             'private': False}
        )
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('id') is not None
    assert data.get('content') == '<p>body of the post</p>'
    assert data.get('title') == 'hello'
    assert data.get('private') is False

    response = client.get(
        url_for('api_v1.post', post_id=data.get('id')),
        headers=get_api_v1_headers('user', '1234')
    )
    data = response.get_json()
    assert isinstance(data['author'], dict)
    assert data['author']['username'] == 'user'
