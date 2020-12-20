"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog import fakes
from flog.models import User, Role, Post
from .helpers import login, create_article, get_response_and_data_of_post, logout, register


def test_create_article(client):
    data = create_article(client)
    print(data)
    response = data['response']
    post = data['post']
    response = client.get('/')
    response_data = response.get_data(as_text=True)
    assert post['title'] in response_data
    # test if filter 'striptag' work
    assert not(post['content'] in response_data)


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
    data = client.get(f"/post/collect/{post_id}", follow_redirects=True)\
                 .get_data(as_text=True)
    assert admin.is_collecting(post_not_private)

    data = client.get(f"/post/collect/{post_id}", follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'Already collected.' in data

    data = client.get(f"/post/uncollect/{post_id}", follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'Post uncollected.' in data
    assert not admin.is_collecting(post_not_private)

    private_post = Post.query.filter(Post.author != admin, Post.private).first()
    while private_post is None:  # same as the while loop above
        fakes.posts(2)
        private_post = Post.query.filter(Post.author != admin, Post.private).first()
    post_id = private_post.id
    data = client.get(f"/post/collect/{post_id}", follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'The author has set this post to invisible. So you cannot collect this post.' in data
    assert not admin.is_collecting(private_post)

    title = create_article(client)['post']['title']
    post_id = Post.query.filter_by(title=title).first().id
    data = client.get(
        f"/post/collect/{post_id}",
        follow_redirects=True
    ).get_data(as_text=True)
    assert 'You cannot collect your own post.' in data
    assert not admin.is_collecting(Post.query.get(post_id))


def test_view_post(client):
    post = Post.query.filter(~Post.private).first()
    data = get_response_and_data_of_post(client, post.id)[1]
    assert post.content in data

    post_private = Post.query.filter(Post.private).first()
    data = get_response_and_data_of_post(client, post_private.id)[1]
    assert 'The author has set this post to invisible.' in data

    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()

    post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    while post_not_private is None:  # ensure the post exists
        fakes.posts(1)
        post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    data = get_response_and_data_of_post(client, post_not_private.id)[1]
    assert post_not_private.content in data

    # test if admin users can see other users' private postss
    post_private = Post.query.filter(Post.author != admin, Post.private).first()
    while post_private is None:
        fakes.posts(1)
        post_private = Post.query.filter(Post.author != admin, Post.private).first()
    data = get_response_and_data_of_post(client, post_private.id)[1]
    assert post_private.content in data

    logout(client)

    register(client, 'john', 'john', '123456', 'john@example.com')
    login(client, 'john', '123456')
    data = get_response_and_data_of_post(client, post_private.id)[1]
    assert 'The author has set this post to invisible.' in data


def test_delete_post(client):
    login(client)
    title = create_article(client)['post']['title']
    post = Post.query.filter_by(title=title).first()
    response = client.post(f'/post/delete/{post.id}/', follow_redirects=True)
    assert response.status_code == 200
    assert Post.query.filter_by(title=title).first() is None
