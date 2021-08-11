"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
import random
from flask import current_app
from flog.models import User, Comment, Post, Image
from flog import fakes as fake
from .conftest import Testing


class APIV2TestCase(Testing):
    def test_api_index(self):
        response = self.client.get("/api/v2/")
        data = response.get_json()
        assert data["api_version"] == "2.0"

    def test_no_auth(self):
        response = self.client.get("/api/v2/post/1/")
        data = response.get_json()
        assert (
            data.get("message")
            == "The token type must be bearer and the token must not be none."
        )

        response = self.client.get(
            "/api/v2/post/1/",
            headers=self.get_api_v2_headers(custom_token="Bearer fake-token"),
        )
        data = response.get_json()
        assert data.get("message") == "invalid token"

    def test_get_token(self):
        response = self.client.post(
            "/api/v2/oauth/token/",
            data=dict(
                grant_type="password",
                username=current_app.config["FLOG_ADMIN"],
                password=current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
        )
        data = response.get_json()
        assert response.status_code == 200
        assert isinstance(data.get("access_token"), str)

    def test_posts(self):
        self.register()

        # test POST
        post = {"content": "<p>body of the post</p>", "title": None, "private": False}

        response = self.client.post(
            "/api/v2/post/new/",
            headers=self.get_api_v2_headers(),
            data=json.dumps(post),
        )
        assert response.status_code == 400

        post["title"] = "hello"

        response = self.client.post(
            "/api/v2/post/new/",
            headers=self.get_api_v2_headers(),
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
            "/api/v2/post/new/",
            headers=self.get_api_v2_headers(
                current_app.config["FLOG_ADMIN"],
                current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
            data=json.dumps(post),
        )
        admin_post_id = response.get_json().get("id")

        # test GET
        response = self.client.get(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        data = response.get_json()
        assert isinstance(data["author"], dict)
        assert data["author"]["username"] == "test"

        # test put
        data = {"title": "a new title", "content": "the new content", "private": True}
        response = self.client.put(
            f"/api/v2/post/{post_id}/", json=data, headers=self.get_api_v2_headers()
        )
        assert response.status_code == 204

        response = self.client.get(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        assert response.get_json().get("content") == data["content"]

        # test send PUT request to an admin's post
        data = {"title": "a new title", "content": "the new content", "private": True}
        response = self.client.put(
            f"/api/v2/post/{admin_post_id}/",
            json=data,
            headers=self.get_api_v2_headers(),
        )
        assert response.status_code == 403

        # test PATCH
        response = self.client.patch(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 204

        response = self.client.patch(
            f"/api/v2/post/{admin_post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 403

        response = self.client.get(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.get_json()["private"] is False

        response = self.client.delete(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 204

        response = self.client.delete(
            f"/api/v2/post/{admin_post_id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 403

    def test_users(self):
        self.register()
        user = User.query.filter_by(username="test").first()
        assert user is not None
        response = self.client.get(
            f"/api/v2/user/{user.id}/", headers=self.get_api_v2_headers()
        )
        data = response.get_json()
        assert data["id"] == user.id
        assert data["username"] == user.username

        # test put method
        user_data = {
            "name": "Real Name",
            "about_me": "A test user.",
            "location": "Shanghai",
        }
        response = self.client.put(
            f"/api/v2/user/{user.id}/",
            json=user_data,
            headers=self.get_api_v2_headers(),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == user_data["name"]
        assert data["about_me"] == user_data["about_me"]
        assert data["location"] == user_data["location"]

        # test forbidden
        response = self.client.put(
            "/api/v2/user/1/", json=user_data, headers=self.get_api_v2_headers()
        )
        assert response.status_code == 403

        # test deleting the admin's account
        # should be forbidden
        # test forbidden
        response = self.client.delete(
            "/api/v2/user/1/", json=user_data, headers=self.get_api_v2_headers()
        )
        assert response.status_code == 403

        # test delete method
        response = self.client.delete(
            f"/api/v2/user/{user.id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        assert response.get_data(as_text=True) == f"User id {user.id} deleted."
        assert User.query.get(user.id) is None

    def test_notifications(self):
        fake.notifications(receiver=User.query.get(1), count=10)
        response = self.client.get(
            "/api/v2/notifications/unread/",
            headers=self.get_api_v2_headers(
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
            "/api/v2/post/new/",
            headers=self.get_api_v2_headers(),
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
            "/api/v2/comment/new/",
            data=json.dumps(data),
            headers=self.get_api_v2_headers(),
        )
        assert response.status_code == 200
        comment_id = response.get_json().get("id")

        response = self.client.get(
            f"/api/v2/post/{post_id}/", headers=self.get_api_v2_headers()
        )
        data = response.get_json()
        comments = data.get("comments")
        assert isinstance(comments, list)
        assert comments[0]["author"] == "test"
        assert comments[0]["body"] == "comment content"

        response = self.client.get(
            f"/api/v2/comment/{comment_id}/", headers=self.get_api_v2_headers()
        )
        data = response.get_json()
        assert data["author"]["username"] == "test"
        assert data["post"]["id"] == post_id
        assert data["body"] == "comment content"
        response = self.client.delete(
            f"/api/v2/comment/{comment_id}/", headers=self.get_api_v2_headers()
        )
        data = response.get_json()
        assert response.status_code == 204
        assert Comment.query.get(comment_id) is None

    def test_follow(self):
        self.register()
        user = User.query.filter_by(username="test").first()
        user2 = User.query.filter(User.username != "test").first()
        response = self.client.get(
            f"/api/v2/user/follow/{user2.id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 204
        assert user.is_following(user2)
        response = self.client.get(
            f"/api/v2/user/unfollow/{user2.id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 204
        assert not user.is_following(user2)

    def test_collect(self):
        self.register()
        user = User.query.filter_by(username="test").first()
        post = Post.query.get(random.randint(1, Post.query.count()))
        response = self.client.get(
            f"/api/v2/post/collect/{post.id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        assert user.is_collecting(post)
        response = self.client.get(
            f"/api/v2/post/uncollect/{post.id}/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        assert not user.is_collecting(post)

    def test_image(self):
        admin_username = current_app.config["FLOG_ADMIN"]
        admin_password = current_app.config["FLOG_ADMIN_PASSWORD"]
        image_dict = self.api_upload_image(
            "/api/v2",
            headers=self.get_api_v2_headers(
                username=admin_username,
                password=admin_password,
                content_type="multipart/form-data",
            ),
        )
        response = image_dict["response"]
        data = image_dict["data"]
        assert response.status_code == 201
        assert data["filename"] == f"{admin_username}_test.png"
        response = self.client.get(f"/image/{admin_username}_test.png")
        assert response.status_code == 200
        image_id = data["image_id"]
        response = self.client.delete(
            f"/api/v2/image/{image_id}/",
            headers=self.get_api_v2_headers(
                username=admin_username, password=admin_password
            ),
        )
        assert response.status_code == 204
        assert Image.query.get(image_id) is None

    def test_folder_like_urls(self):
        self.register()
        # create a post first
        response = self.client.post(
            "/api/v2/post/new/",
            headers=self.get_api_v2_headers(),
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

        user_id = User.query.filter_by(username="test").first().id
        response = self.client.get(
            f"/api/v2/user/{user_id}/posts/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        posts = response.get_json()
        assert posts[0].get("id") == post_id

        data = {"body": "comment content", "post_id": post_id}
        self.client.post(
            "/api/v2/comment/new/",
            data=json.dumps(data),
            headers=self.get_api_v2_headers(),
        )
        response = self.client.get(
            f"/api/v2/post/{post_id}/comments/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        comments = response.get_json()
        assert comments[0].get("body") == "comment content"

        response = self.client.get(
            f"/api/v2/user/{user_id}/comments/", headers=self.get_api_v2_headers()
        )
        assert response.status_code == 200
        comments = response.get_json()
        assert comments[0].get("body") == "comment content"

        # register a user and follow it
        u2 = User.query.filter(User.username != "test").first()
        user = User.query.get(user_id)
        user.follow(u2)

        response = self.client.get(
            f"/api/v2/user/{user_id}/following/", headers=self.get_api_v2_headers()
        )
        following = response.get_json()
        assert following[0].get("username") == u2.username

        response = self.client.get(
            f"/api/v2/user/{u2.id}/followers/", headers=self.get_api_v2_headers()
        )
        u2_followers = response.get_json()
        assert "test" in [u["username"] for u in u2_followers]
