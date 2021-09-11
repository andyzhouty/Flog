from flask import current_app
from flog.models import User, Post, Comment, db, Column, Notification, Group
from flog.fakes import fake
from .conftest import Testing


class APIV3TestCase(Testing):
    def setUp(self):
        super().setUp()
        self.register()

    def test_api_index(self):
        response = self.client.get("/api/v3")
        data = response.get_json()
        assert data["api_version"] == "3.0"

    def test_token(self):
        response = self.client.post(
            "/api/v3/token",
            data=dict(
                username=current_app.config["FLOG_ADMIN"],
                password=current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
        )
        data = response.get_json()
        assert response.status_code == 200
        assert isinstance(data.get("access_token"), str)

        response = self.client.post(
            "/api/v3/token/verify", data=dict(token=data.get("access_token"))
        )
        assert response.status_code == 200
        response = self.client.post(
            "/api/v3/token/verify", data=dict(token="FAKE-TOKEN")
        )
        assert response.status_code == 401
        response = self.client.get(
            "/api/v3/self/posts",
            headers=self.get_api_v3_headers(custom_token="FAKE-TOKEN"),
        )
        assert response.status_code == 401

    def test_user(self):
        test_user_data = {
            "username": "test2",
            "password": "password",
            "email": "test@example.com",
        }
        response = self.client.post("/api/v3/register", data=test_user_data)
        assert response.status_code == 200

        user = User.query.filter_by(username="test2").first()
        response = self.client.get(f"/api/v3/user/{user.id}")
        data = response.get_json()
        assert data["id"] == user.id

        user_data = {
            "name": "Real Name",
            "about_me": "A test user.",
            "location": "Nowhere",
            "password": "new_password",
        }
        response = self.client.put(
            f"/api/v3/user/{user.id}",
            json=user_data,
            headers=self.get_api_v3_headers(username="test2"),
        )
        assert response.status_code == 200
        assert user.name == user_data["name"]
        assert user.verify_password("new_password")

        response = self.client.patch(
            f"/api/v3/user/{user.id}",
            json=user_data,
            headers=self.get_api_v3_headers(
                username=current_app.config["FLOG_ADMIN"],
                password=current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
        )
        assert response.status_code == 200
        assert user.locked

    def test_post(self):

        self.register("test2", "test2", "123456", "test2@example.com")
        user = User.query.filter_by(username="test").first()
        post = Post(
            private=False,
            title="abc",
            content="1234",
            author=user,
        )
        db.session.add(post)
        db.session.commit()
        response = self.client.get(f"/api/v3/post/{post.id}")
        data = response.get_json()
        assert data["title"] == post.title

        # test PUT /api/v3/post/{post.id}
        put_data = {"title": "ABCD", "content": "<p>test</p>", "private": True}
        response = self.client.put(
            f"/api/v3/post/{post.id}", headers=self.get_api_v3_headers(), json=put_data
        )
        data = response.get_json()

        assert data["private"] is True

        # test get private posts without authentication
        response = self.client.get(f"/api/v3/user/{user.id}/posts")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []  # should be empty since the user has no public posts
        # test get private posts with ANOTHER user's authentication
        response = self.client.get(
            f"/api/v3/user/{user.id}/posts",
            headers=self.get_api_v3_headers("test2", "123456", "InvalidToken"),
        )
        data = response.get_json()
        assert data == []
        # test get private posts WITH author's authentication
        response = self.client.get(
            f"/api/v3/user/{user.id}/posts", headers=self.get_api_v3_headers()
        )
        data = response.get_json()
        assert any(post["title"] == "ABCD" for post in data)

        # test get private posts WITHOUT authentication
        response = self.client.get(f"/api/v3/post/{post.id}")
        assert response.status_code == 403

        response = self.client.get(
            f"/api/v3/post/{post.id}", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 200

        # test get private post with admin permission
        response = self.client.get(
            f"/api/v3/post/{post.id}",
            headers=self.get_api_v3_headers(
                username=current_app.config["FLOG_ADMIN"],
                password=current_app.config["FLOG_ADMIN_PASSWORD"],
            ),
        )
        assert response.status_code == 200

        # test get ALL posts with/without author's authentication
        response = self.client.get(
            "/api/v3/post/all", headers=self.get_api_v3_headers()
        )
        data = response.get_json()
        assert any(post["title"] == "ABCD" for post in data)

        response = self.client.get("/api/v3/post/all")
        data = response.get_json()
        assert not any(post["title"] == "ABCD" for post in data)

        # test add posts
        response = self.client.post(
            "/api/v3/post/add",
            json=dict(title="abcd", content="test content", private=False),
            headers=self.get_api_v3_headers(),
        )
        query = Post.query.filter_by(title="abcd")
        assert response.status_code == 200
        assert query.count() == 1
        post = query.first()

        # test delete posts
        response = self.client.delete(
            f"/api/v3/post/{post.id}", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204
        assert query.count() == 0

    def test_comments(self):

        comment = Comment.query.get(1)
        comment.author = User.query.filter_by(username="test").first()
        db.session.commit()
        response = self.client.get("/api/v3/comment/1")
        data = response.get_json()
        assert data["body"] == comment.body

        response = self.client.put(
            "/api/v3/comment/1",
            json=dict(body="body"),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 200
        assert comment.body == "body"

        replied = Comment.query.get(2)
        response = self.client.put(
            "/api/v3/comment/1",
            json=dict(reply_id=2, post_id=replied.post.id),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 200
        assert comment.replied == replied

        p = Post(
            private=True,
            author=User.query.filter_by(username="test").first(),
            title="test",
            content="abcd",
        )
        response = self.client.put(
            "/api/v3/comment/1",
            json=dict(post_id=p.id),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 400

        response = self.client.delete(
            "/api/v3/comment/1", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204
        assert Comment.query.get(1) is None

        comment_dict = {
            "body": "test body",
            "post_id": replied.post.id,
            "reply_id": replied.id,
        }
        response = self.client.post(
            "/api/v3/comment/add",
            json=comment_dict,
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 200

        comment_dict["post_id"] = p.id
        comment_dict.pop("reply_id")
        response = self.client.post(
            "/api/v3/comment/add",
            json=comment_dict,
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 400

    def test_column(self):

        data = {"name": "test-column"}
        response = self.client.post(
            "/api/v3/column/create", headers=self.get_api_v3_headers(), json=data
        )
        assert response.status_code == 200
        assert response.get_json()["author"]["username"] == "test"
        column = Column.query.filter_by(name="test-column").first()

        post = dict(title="1234", content="content", column_ids=[column.id])
        response = self.client.post(
            "/api/v3/post/add", headers=self.get_api_v3_headers(), json=post
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["columns"][0]["id"] == column.id

        post2 = dict(title="abcd", content="foobar")
        self.client.post(
            "/api/v3/post/add", headers=self.get_api_v3_headers(), json=post2
        )
        post2 = Post.query.filter_by(title="abcd").first()
        column2 = dict(name="column2", post_ids=[post2.id])
        response = self.client.post(
            "/api/v3/column/create", headers=self.get_api_v3_headers(), json=column2
        )
        assert response.status_code == 200
        assert "posts" in response.get_json()
        column2 = Column.query.filter_by(name="column2").first()
        assert post2 in column2.posts

        response = self.client.get(f"/api/v3/column/{column2.id}")
        assert response.status_code == 200
        assert response.get_json()["name"] == "column2"

        post3 = dict(title="efgh", content="hello world")
        self.client.post(
            "/api/v3/post/add", headers=self.get_api_v3_headers(), json=post3
        )
        post3 = Post.query.filter_by(title="efgh").first()

        response = self.client.put(
            f"/api/v3/column/{column2.id}",
            json=dict(name="foobar", post_ids=[post2.id, post3.id]),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 200
        assert response.get_json()["name"] == "foobar"

        response = self.client.delete(
            f"/api/v3/column/{column2.id}", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204
        assert (
            Column.query.filter_by(name="foobar").count() == 0
        )  # ensure the column is deleted.

    def test_self(self):

        response = self.client.get("/api/v3/self", headers=self.get_api_v3_headers())
        assert response.get_json()["username"] == "test"

        post = dict(title="1234", content="content")
        self.client.post(
            "/api/v3/post/add", headers=self.get_api_v3_headers(), json=post
        )

        response = self.client.get(
            "/api/v3/self/posts", headers=self.get_api_v3_headers()
        )
        assert response.get_json()[0]["title"] == "1234"

    def test_notifications(self):

        user = User.query.filter_by(username="test").first()
        notification_array = []
        for _ in range(5):
            n = Notification(receiver=user, message=fake.sentence())
            db.session.add(n)
            notification_array.append(n)
        db.session.commit()

        response = self.client.get(
            "/api/v3/notification/all", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 200
        assert len(response.get_json()) == 5

        response = self.client.get(
            "/api/v3/notification/1", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 200
        assert response.get_json()["id"] == notification_array[0].id

        self.register("Test2", "test2", "pwd", "t@example.com")
        response = self.client.get(
            "/api/v3/notification/1", headers=self.get_api_v3_headers("test2", "pwd")
        )
        assert response.status_code == 403
        response = self.client.delete(
            "/api/v3/notification/1", headers=self.get_api_v3_headers("test2", "pwd")
        )
        assert response.status_code == 403

        response = self.client.delete(
            "/api/v3/notification/1", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204

    def test_group(self):

        u2 = User(username="u2", email="u2@example.com")
        u2.set_password("123456")
        db.session.add(u2)
        db.session.commit()

        # test create group with private
        g_dict = dict(name="test-group", private=True)
        response = self.client.post(
            "/api/v3/group/create", json=g_dict, headers=self.get_api_v3_headers()
        )
        assert response.status_code == 200
        g = Group.query.filter_by(name="test-group").first()

        response = self.client.get(
            f"/api/v3/group/{g.id}", headers=self.get_api_v3_headers("u2", "123456")
        )
        assert response.status_code == 403

        # test create group with members
        g_dict = dict(name="test-group2", members=[u2.id])
        response = self.client.post(
            "/api/v3/group/create", json=g_dict, headers=self.get_api_v3_headers()
        )
        assert response.status_code == 200
        g = Group.query.filter_by(name="test-group2").first()

        response = self.client.get(
            f"/api/v3/group/{g.id}", headers=self.get_api_v3_headers("u2", "123456")
        )
        assert response.status_code == 200

        # test PUT group
        modified = dict(members=[u2.id])
        response = self.client.put(
            f"/api/v3/group/{g.id}", headers=self.get_api_v3_headers(), json=modified
        )
        assert response.status_code == 200
        data = response.get_json()

        assert any(u2.id == u["id"] for u in data["members"])

        # test DELETE group
        response = self.client.delete(
            f"/api/v3/group/{g.id}", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204

    def test_coins(self):
        p = Post(title="title", content="content")
        p2 = Post(title="title2", content="content2")
        db.session.add(p)
        db.session.add(p2)
        db.session.commit()
        response = self.client.post(
            f"/api/v3/post/coin/{p.id}",
            json=dict(amount=2),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 200
        response = self.client.post(
            f"/api/v3/post/coin/{p.id}",
            json=dict(amount=1),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 400
        u = User.query.filter_by(username="test").first()
        assert u.coins == 1
        assert u.experience == 20

        response = self.client.post(
            f"/api/v3/post/coin/{p.id}",
            json=dict(amount=2),
            headers=self.get_api_v3_headers(),
        )
        assert response.status_code == 400
