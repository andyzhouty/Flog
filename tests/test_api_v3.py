from flask import current_app
from .helpers import register, login, get_api_v3_headers, generate_post
from flog.models import User, Post, Comment, db


def test_api_index(client):
    response = client.get("/api/v3")
    data = response.get_json()
    assert data["api_version"] == "3.0"


def test_user(client):
    register(client)
    login(client, "test", "password")
    user_id = User.query.filter_by(username="test").first().id
    response = client.get(f"/api/v3/user/{user_id}")
    data = response.get_json()
    assert data["username"] == "test"


def test_get_token(client):
    response = client.post(
        "/api/v3/token",
        data=dict(
            username=current_app.config["FLOG_ADMIN"],
            password=current_app.config["FLOG_ADMIN_PASSWORD"],
        ),
    )
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data.get("access_token"), str)


def test_user(client):
    register(client)
    user = User.query.filter_by(username="test").first()
    response = client.get(f"/api/v3/user/{user.id}")
    data = response.get_json()
    assert data["id"] == user.id

    user_data = {
        "name": "Real Name",
        "about_me": "A test user.",
        "location": "Nowhere",
        "password": "new_password",
    }
    response = client.put(
        f"/api/v3/user/{user.id}", json=user_data, headers=get_api_v3_headers(client)
    )
    assert response.status_code == 200
    assert user.name == user_data["name"]
    assert user.verify_password("new_password")

    response = client.patch(
        f"/api/v3/user/{user.id}",
        json=user_data,
        headers=get_api_v3_headers(
            client,
            username=current_app.config["FLOG_ADMIN"],
            password=current_app.config["FLOG_ADMIN_PASSWORD"],
        ),
    )
    assert response.status_code == 200
    assert user.locked


def test_post(client):
    register(client)
    post = Post(
        private=False,
        title="abc",
        content="1234",
        author=User.query.filter_by(username="test").first(),
    )
    db.session.add(post)
    db.session.commit()
    response = client.get(f"/api/v3/post/{post.id}")
    data = response.get_json()
    assert data["title"] == post.title
    put_data = {"title": "ABCD", "content": "<p>test</p>", "private": True}
    response = client.put(
        f"/api/v3/post/{post.id}", headers=get_api_v3_headers(client), json=put_data
    )
    data = response.get_json()

    assert data["private"] is True

    response = client.get(f"/api/v3/post/{post.id}")
    assert response.status_code == 403

    response = client.get(
        f"/api/v3/post/{post.id}",
        headers=get_api_v3_headers(
            client,
            username=current_app.config["FLOG_ADMIN"],
            password=current_app.config["FLOG_ADMIN_PASSWORD"],
        ),
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v3/post/add",
        json=dict(title="abcd", content="test content", private=False),
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 200
    assert Post.query.filter_by(title="abcd").count() == 1


def test_comments(client):
    register(client)
    comment = Comment.query.get(1)
    comment.author = User.query.filter_by(username="test").first()
    db.session.commit()
    response = client.get(f"/api/v3/comment/1")
    data = response.get_json()
    assert data["body"] == comment.body

    response = client.put(
        "/api/v3/comment/1", json=dict(body="body"), headers=get_api_v3_headers(client)
    )
    assert response.status_code == 200
    assert comment.body == "body"

    replied = Comment.query.get(2)
    response = client.put(
        "/api/v3/comment/1",
        json=dict(reply_id=2, post_id=replied.post.id),
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 200
    assert comment.replied == replied

    p = Post(
        private=True,
        author=User.query.filter_by(username="test").first(),
        title="test",
        content="abcd",
    )
    response = client.put(
        "/api/v3/comment/1",
        json=dict(post_id=p.id),
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 400

    comment_dict = {
        "body": "test body",
        "post_id": replied.post.id,
        "reply_id": replied.id,
    }
    response = client.post(
        "/api/v3/comment/add",
        json=comment_dict,
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 200

    comment_dict["post_id"] = p.id
    comment_dict.pop("reply_id")
    response = client.post(
        "/api/v3/comment/add",
        json=comment_dict,
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 400
