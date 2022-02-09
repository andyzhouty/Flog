"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
import random
from flask import current_app
from flog import fakes as fake
from flog.models import User, Comment, Post
from .conftest import b64encode, Testing


class APIV1TestCase(Testing):
    def test_api_index(self):
        response = self.client.get("/api/v1/")
        data = response.get_json()
        assert data["api_version"] == "1.0"

    def test_no_auth(self):
        response = self.client.get("/api/v1/post/1/")
        assert response.status_code == 401

    def test_get_token(self):
        self.register()
        response = self.client.get(
            "/api/v1/auth/token/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 200
        token = response.get_json().get("access_token")
        headers = {
            "Authorization": "Basic "
            + b64encode(f"{token}:".encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = self.client.get("/api/v1/post/1/", headers=headers)
        assert response.status_code == 200

    def test_posts(self):
        self.register()

        # test POST
        post = {"content": "<p>body of the post</p>", "title": None, "private": False}

        response = self.client.post(
            "/api/v1/post/new/",
            headers=self.get_api_v1_headers(),
            data=json.dumps(post),
        )
        assert response.status_code == 400

        post["title"] = "hello"
        response = self.client.post(
            "/api/v1/post/new/",
            headers=self.get_api_v1_headers(),
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
        response = self.client.post(
            "/api/v1/post/new/",
            headers=self.get_api_v1_headers(
                current_app.config["FLOG_ADMIN"],
                current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
            data=json.dumps(post),
        )
        admin_post_id = response.get_json().get("id")

        # test GET
        response = self.client.get(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        data = response.get_json()
        assert isinstance(data["author"], dict)
        assert data["author"]["username"] == "test"

        # test PUT
        data = {"title": "a new title", "content": "the new content", "private": True}
        response = self.client.put(
            f"/api/v1/post/{post_id}/", json=data, headers=self.get_api_v1_headers()
        )
        assert response.status_code == 204

        response = self.client.put(
            f"/api/v1/post/{admin_post_id}/",
            json=data,
            headers=self.get_api_v1_headers(),
        )
        assert response.status_code == 403

        response = self.client.get(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 200
        assert response.get_json().get("content") == data["content"]

        response = self.client.patch(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 204

        response = self.client.patch(
            f"/api/v1/post/{admin_post_id}/",
            json=data,
            headers=self.get_api_v1_headers(),
        )
        assert response.status_code == 403

        response = self.client.get(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.get_json()["private"] is False

        response = self.client.delete(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 204

        response = self.client.delete(
            f"/api/v1/post/{admin_post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 403

        response = self.client.get(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 404

    def test_users(self):
        self.register()
        user = User.query.filter_by(username="test").first()
        assert user is not None
        response = self.client.get(
            f"/api/v1/user/{user.id}/", headers=self.get_api_v1_headers()
        )
        data = response.get_json()
        assert data["id"] == user.id
        assert data["username"] == user.username

        # test put method
        user_data = {
            "name": "Real Name",
            "about_me": "A test user.",
            "location": "Nowhere",
        }
        response = self.client.put(
            f"/api/v1/user/{user.id}/",
            json=user_data,
            headers=self.get_api_v1_headers(),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == user_data["name"]
        assert data["about_me"] == user_data["about_me"]
        assert data["location"] == user_data["location"]

        # test forbidden
        response = self.client.put(
            "/api/v1/user/1/", json=user_data, headers=self.get_api_v1_headers()
        )
        assert response.status_code == 403

        # test delete method
        response = self.client.delete(
            f"/api/v1/user/{user.id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 200
        assert response.get_data(as_text=True) == f"User id {user.id} deleted."
        assert User.query.get(user.id) is None

    def test_notifications(self):
        fake.notifications(receiver=User.query.get(1), count=10)
        response = self.client.get(
            "/api/v1/notifications/unread/",
            headers=self.get_api_v1_headers(
                current_app.config["FLOG_ADMIN"],
                current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
        )
        data = response.get_json()
        assert data.get("unread_num") == 10
        assert data.get("unread_num") == len(data.get("unread_items"))
        assert isinstance(data.get("unread_items")[1], list)

    def test_comments(self):
        self.register()
        # create a post first
        response = self.client.post(
            "/api/v1/post/new/",
            headers=self.get_api_v1_headers(),
            data=json.dumps(
                {
                    "content": "<p>body of the post</p>",
                    "title": "hello",
                    "private": False,
                }
            ),
        )
        assert response.status_code == 200
        data = response.get_json()
        post_id = data.get("id")

        # then create a comment
        data = {"body": "comment content", "post_id": post_id}
        response = self.client.post(
            "/api/v1/comment/new/",
            data=json.dumps(data),
            headers=self.get_api_v1_headers(),
        )
        assert response.status_code == 200
        comment_id = response.get_json().get("id")

        response = self.client.get(
            f"/api/v1/post/{post_id}/", headers=self.get_api_v1_headers()
        )
        data = response.get_json()
        comments = data.get("comments")
        assert isinstance(comments, list)
        assert comments[0]["author"] == "test"
        assert comments[0]["body"] == "comment content"

        response = self.client.get(
            f"/api/v1/comment/{comment_id}/", headers=self.get_api_v1_headers()
        )
        data = response.get_json()
        assert data["author"]["username"] == "test"
        assert data["post"]["id"] == post_id
        assert data["body"] == "comment content"

        response = self.client.delete(
            f"/api/v1/comment/{comment_id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 204
        assert Comment.query.get(comment_id) is None

    def test_collect(self):
        self.register()
        user = User.query.filter_by(username="test").first()
        post = Post.query.get(random.randint(1, Post.query.count()))
        response = self.client.get(
            f"/api/v1/post/collect/{post.id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 200
        assert user.is_collecting(post)
        response = self.client.get(
            f"/api/v1/post/uncollect/{post.id}/", headers=self.get_api_v1_headers()
        )
        assert response.status_code == 200
        assert not user.is_collecting(post)
