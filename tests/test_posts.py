"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog import fakes
from faker import Faker
from flog.models import Comment, User, Role, Post, Column
from .helpers import (
    login,
    generate_post,
    generate_column,
    get_response_and_data_of_post,
    logout,
    register,
)

fake = Faker()


def test_create_post(client):
    login(client)
    data = generate_post(client)
    post = data["post"]
    response = client.get("/")
    response_data = response.get_data(as_text=True)
    assert post["title"] in response_data
    # test if filter 'striptag' work
    assert not (post["content"] in response_data)

    col_name = generate_column(client)["column_name"]
    column = Column.query.filter_by(name=col_name).first()
    print(column.author)
    # test add post to column when submit
    title = fake.sentence()
    data = dict(
        title=title,
        content=fake.text(),
        columns=[column.id]
    )
    response = client.post("/write/", data=data, follow_redirects=True)
    assert response.status_code == 200
    print(response.get_data(as_text=True))
    post = Post.query.filter_by(title=title).first()
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    assert post in column.posts
    assert column in admin.columns


def test_collect_uncollect(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()

    post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    while post_not_private is None:  # ensure the post exists
        fakes.posts(2)
        post_not_private = Post.query.filter(
            Post.author != admin, ~Post.private
        ).first()
    post_id = post_not_private.id
    data = client.get(f"/post/collect/{post_id}", follow_redirects=True).get_data(
        as_text=True
    )
    assert admin.is_collecting(post_not_private)

    # test if the collected post appears in the collection page
    response = client.get("/post/collected/")
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert post_not_private.title in data

    data = client.get(f"/post/collect/{post_id}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "Already collected." in data

    data = client.get(f"/post/uncollect/{post_id}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "Post uncollected." in data
    assert not admin.is_collecting(post_not_private)

    private_post = Post.query.filter(Post.author != admin, Post.private).first()
    while private_post is None:  # same as the while loop above
        fakes.posts(2)
        private_post = Post.query.filter(Post.author != admin, Post.private).first()
    post_id = private_post.id
    data = client.get(f"/post/collect/{post_id}", follow_redirects=True).get_data(
        as_text=True
    )
    assert (
        "The author has set this post to invisible. So you cannot collect this post."
        in data
    )
    assert not admin.is_collecting(private_post)

    title = generate_post(client)["post"]["title"]
    post_id = Post.query.filter_by(title=title).first().id
    data = client.get(f"/post/collect/{post_id}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "You cannot collect your own post." in data
    assert not admin.is_collecting(Post.query.get(post_id))


def test_view_post(client):
    post = Post.query.filter(~Post.private).first()
    while post is None:
        fakes.posts(1)
        post = Post.query.filter(~Post.private).first()
    data = get_response_and_data_of_post(client, post.id)[1]
    print(data)
    assert post.content in data

    post_private = Post.query.filter(Post.private).first()
    while post_private is None:
        fakes.posts(1)
        post_private = Post.query.filter(Post.private).first()
    data = get_response_and_data_of_post(client, post_private.id)[1]
    assert "The author has set this post to invisible." in data

    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()

    post_not_private = Post.query.filter(Post.author != admin, ~Post.private).first()
    while post_not_private is None:  # ensure the post exists
        fakes.posts(1)
        post_not_private = Post.query.filter(
            Post.author != admin, ~Post.private
        ).first()
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

    register(client, "john", "john", "123456", "john@example.com")
    login(client, "john", "123456")
    data = get_response_and_data_of_post(client, post_private.id)[1]
    assert "The author has set this post to invisible." in data


def test_delete_post(client):
    login(client)
    title = generate_post(client)["post"]["title"]
    post = Post.query.filter_by(title=title).first()
    response = client.post(f"/post/delete/{post.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert Post.query.filter_by(title=title).first() is None


def test_get_urls(client):
    """Test if the user can GET the urls withour displaying a 500 page."""
    login(client)
    title = generate_post(client)["post"]["title"]
    post = Post.query.filter_by(title=title).first()
    response = client.get(f"/post/{post.id}/")
    assert response.status_code == 200
    response = client.get("/write/")
    assert response.status_code == 200
    response = client.get(f"/post/edit/{post.id}/")
    assert response.status_code == 200


def test_comments(client):
    login(client)
    title = generate_post(client)["post"]["title"]
    post = Post.query.filter_by(title=title).first()
    data = {"body": "comment content"}
    response = client.post(f"/post/{post.id}/", data=data, follow_redirects=True)
    assert response.status_code == 200
    response = client.get(f"/post/{post.id}/")
    assert data["body"] in response.get_data(as_text=True)
    comment = Comment.query.filter_by(body=data["body"]).first()

    # test replying comments
    reply = {"body": "reply"}
    response = client.post(
        f"/post/{post.id}/?reply={comment.id}", data=reply, follow_redirects=True
    )
    assert response.status_code == 200
    assert len(comment.replies) == 1


def test_comment_posts_of_deleted_users(client):
    register(client)
    login(client, "test", "password")
    title = generate_post(client, username="test", password="password")["post"][
        "title"
    ]
    logout(client)
    post = Post.query.filter_by(title=title).first()
    user = User.query.filter_by(username="test").first()
    user.delete()
    login(client)

    data = {"body": "comment content"}
    response = client.post(f"/post/{post.id}/", data=data, follow_redirects=True)
    assert response.status_code == 200


def test_create_column(client):
    register(client)
    login(client, "test", "password")
    generate_post(client, login=False)
    response = client.get("/column/create/")
    assert response.status_code == 200

    user = User.query.filter_by(username="test").first()
    column = dict(
        name="test",
        posts=[post.id for post in Post.query.filter_by(author=user).all()],
    )
    response = client.post("/column/create/", data=column, follow_redirects=True)
    assert response.status_code == 200
    res_data = response.get_data(as_text=True)
    assert "Your column was successfully created." in res_data


def test_view_column(client):
    register(client)
    login(client, "test", "password")
    col_name = generate_column(client)["column_name"]
    column = Column.query.filter_by(name=col_name).first()
    response = client.get(f"/column/{column.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert col_name in response.get_data(as_text=True)
