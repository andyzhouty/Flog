"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
import random
from flask.globals import current_app
from flog.models import User, Comment, Post, Image
from tests.helpers import register, get_api_v1_headers, api_upload_image, b64encode
from flog import fakes as fake


def test_api_index(client):
    response = client.get("/api/v1/")
    data = response.get_json()
    assert data["api_version"] == "1.0"


def test_no_auth(client):
    response = client.get("/api/v1/post/1/")
    assert response.status_code == 401


def test_get_token(client):
    register(client)
    response = client.get("/api/v1/auth/token/", headers=get_api_v1_headers())
    assert response.status_code == 200
    token = response.get_json().get("access_token")
    headers = {
        "Authorization": "Basic " + b64encode(f"{token}:".encode("utf-8")).decode("utf-8"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = client.get("/api/v1/post/1/", headers=headers)
    assert response.status_code == 200


def test_posts(client):
    register(client)

    # test POST
    post = {"content": "<p>body of the post</p>", "title": None, "private": False}

    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers(),
        data=json.dumps(post),
    )
    assert response.status_code == 400

    post["title"] = "hello"
    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers(),
        data=json.dumps(post),
    )
    assert response.status_code == 200

    data = response.get_json()
    post_id = data.get("id")
    assert post_id is not None
    assert data.get("content") == "<p>body of the post</p>"
    assert data.get("title") == "hello"
    assert data.get("private") is False

    post["title"] = "hello_admin"
    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers(
            current_app.config["FLOG_ADMIN"],
            current_app.config["FLOG_ADMIN_PASSWORD"],
        ),
        data=json.dumps(post),
    )
    admin_post_id = response.get_json().get("id")
    print(admin_post_id)

    # test GET
    response = client.get(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    data = response.get_json()
    assert isinstance(data["author"], dict)
    assert data["author"]["username"] == "test"

    # test PUT
    data = {"title": "a new title", "content": "the new content", "private": True}
    response = client.put(
        f"/api/v1/post/{post_id}/", json=data, headers=get_api_v1_headers()
    )
    assert response.status_code == 204

    response = client.put(
        f"/api/v1/post/{admin_post_id}/", json=data, headers=get_api_v1_headers()
    )
    assert response.status_code == 403

    response = client.get(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    assert response.status_code == 200
    assert response.get_json().get("content") == data["content"]

    response = client.patch(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    assert response.status_code == 204

    response = client.patch(
        f"/api/v1/post/{admin_post_id}/", json=data, headers=get_api_v1_headers()
    )
    assert response.status_code == 403

    response = client.get(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    assert response.get_json()["private"] is False

    response = client.delete(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    assert response.status_code == 204

    response = client.delete(
        f"/api/v1/post/{admin_post_id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 403

    response = client.get(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    assert response.status_code == 404


def test_users(client):
    register(client)
    user = User.query.filter_by(username="test").first()
    assert user is not None
    response = client.get(f"/api/v1/user/{user.id}/", headers=get_api_v1_headers())
    data = response.get_json()
    assert data["id"] == user.id
    assert data["username"] == user.username

    # test put method
    user_data = {
        "name": "Real Name",
        "about_me": "A test user.",
        "location": "Nowhere",
    }
    response = client.put(
        f"/api/v1/user/{user.id}/", json=user_data, headers=get_api_v1_headers()
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == user_data["name"]
    assert data["about_me"] == user_data["about_me"]
    assert data["location"] == user_data["location"]

    # test forbidden
    response = client.put(
        "/api/v1/user/1/", json=user_data, headers=get_api_v1_headers()
    )
    assert response.status_code == 403

    # test delete method
    response = client.delete(f"/api/v1/user/{user.id}/", headers=get_api_v1_headers())
    assert response.status_code == 200
    assert response.get_data(as_text=True) == f"User id {user.id} deleted."
    assert User.query.get(user.id) is None


def test_notifications(client):
    fake.notifications(receiver=User.query.get(1), count=10)
    response = client.get(
        "/api/v1/notifications/unread/",
        headers=get_api_v1_headers(
            current_app.config["FLOG_ADMIN"], current_app.config["FLOG_ADMIN_PASSWORD"]
        ),
    )
    data = response.get_json()
    assert data.get("unread_num") == 10
    assert data.get("unread_num") == len(data.get("unread_items"))
    assert isinstance(data.get("unread_items")[1], list)


def test_comments(client):
    register(client)
    # create a post first
    response = client.post(
        "/api/v1/post/new/",
        headers=get_api_v1_headers(),
        data=json.dumps(
            {"content": "<p>body of the post</p>", "title": "hello", "private": False}
        ),
    )
    assert response.status_code == 200
    data = response.get_json()
    post_id = data.get("id")

    # then create a comment
    data = {"body": "comment content", "post_id": post_id}
    response = client.post(
        "/api/v1/comment/new/", data=json.dumps(data), headers=get_api_v1_headers()
    )
    assert response.status_code == 200
    comment_id = response.get_json().get("id")

    response = client.get(f"/api/v1/post/{post_id}/", headers=get_api_v1_headers())
    data = response.get_json()
    comments = data.get("comments")
    assert isinstance(comments, list)
    assert comments[0]["author"] == "test"
    assert comments[0]["body"] == "comment content"

    response = client.get(
        f"/api/v1/comment/{comment_id}/", headers=get_api_v1_headers()
    )
    data = response.get_json()
    assert data["author"]["username"] == "test"
    assert data["post"]["id"] == post_id
    assert data["body"] == "comment content"

    response = client.delete(
        f"/api/v1/comment/{comment_id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 204
    assert Comment.query.get(comment_id) is None


def test_follow(client_with_request_ctx):
    client = client_with_request_ctx
    register(client)
    user = User.query.filter_by(username="test").first()
    user2 = User.query.filter(User.username != "test").first()
    response = client.get(
        f"/api/v1/user/follow/{user2.id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 204
    assert user.is_following(user2)
    response = client.get(
        f"/api/v1/user/unfollow/{user2.id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 204
    assert not user.is_following(user2)


def test_collect(client):
    register(client)
    user = User.query.filter_by(username="test").first()
    post = Post.query.get(random.randint(1, Post.query.count()))
    response = client.get(
        f"/api/v1/post/collect/{post.id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 200
    assert user.is_collecting(post)
    response = client.get(
        f"/api/v1/post/uncollect/{post.id}/", headers=get_api_v1_headers()
    )
    assert response.status_code == 200
    assert not user.is_collecting(post)


def test_image(client):
    admin_username = current_app.config["FLOG_ADMIN"]
    admin_password = current_app.config["FLOG_ADMIN_PASSWORD"]
    image_dict = api_upload_image(
        client,
        "/api/v1",
        headers=get_api_v1_headers(
            username=admin_username,
            password=admin_password,
            content_type="multipart/form-data",
        ),
    )
    response = image_dict["response"]
    data = image_dict["data"]
    assert response.status_code == 201
    assert data["image_url"] == f"/image/{admin_username}_test.png"
    response = client.get(f"/image/{admin_username}_test.png")
    assert response.status_code == 200
    image_id = data["image_id"]
    response = client.delete(
        f"/api/v1/image/{image_id}/",
        headers=get_api_v1_headers(username=admin_username, password=admin_password),
    )
    assert response.status_code == 204
    assert Image.query.get(image_id) is None
