from flask import url_for
from flog import fakes
from flog.models import User, Role, Post
from .helpers import login, create_article


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
    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True)\
                 .get_data(as_text=True)
    assert admin.is_collecting(post_not_private)

    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'Already collected.' in data

    data = client.get(url_for('main.uncollect_post', id=post_id), follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'Post uncollected.' in data
    assert not admin.is_collecting(post_not_private)

    private_post = Post.query.filter(Post.author != admin, Post.private).first()
    while private_post is None:  # same as the while loop above
        fakes.posts(2)
        private_post = Post.query.filter(Post.author != admin, Post.private).first()
    post_id = private_post.id
    data = client.get(url_for('main.collect_post', id=post_id), follow_redirects=True)\
                 .get_data(as_text=True)
    assert 'The author has set this post to invisible. So you cannot collect this post.' in data
    assert not admin.is_collecting(private_post)

    title = create_article(client)['post']['title']
    post_id = Post.query.filter_by(title=title).first().id
    data = client.get(
        url_for('main.collect_post', id=post_id),
        follow_redirects=True
    ).get_data(as_text=True)
    assert 'You cannot collect your own post.' in data
    assert not admin.is_collecting(Post.query.get(post_id))


def test_view_post(client):
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
    response = client.get(url_for('main.full_post', id=post_not_private.id))
    data = response.get_data(as_text=True)
    assert post_not_private.content in data