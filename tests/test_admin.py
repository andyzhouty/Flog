"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from random import randint
from faker import Faker
from flog.models import Post
from flog.utils import lower_username
from .helpers import create_article, login

fake = Faker()


def test_admin_edit_article(client):
    login(client)
    post_data = create_article(client)
    title = post_data['post']['title']
    post_id = Post.query.filter_by(title=title).first().id
    response = client.get(f"/post/edit/{post_id}/")
    response_data = response.get_data(as_text=True)
    # test if the old content exists in the edit page.
    print(response_data)
    assert post_data['text'] in response_data
    data = {
        'title': 'new title',
        'content': 'new content'
    }
    response = client.post(f"/post/edit/{post_id}/", data=data, follow_redirects=True)
    post = Post.query.get(post_id)
    assert post is not None
    assert post.title == data['title']


def test_admin_edit_user_profile(client):
    login(client)
    response = client.get("/admin/user/all/")
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
    response = client.post(f"/admin/user/{user_id}/profile/edit/",
                           data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert data['email'] in response_data
    assert data['username'] in response_data
    assert data['about_me'] in response_data
    assert data['location'] in response_data
