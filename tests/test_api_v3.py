from flask import current_app
from .helpers import (
    register,
    get_api_v3_headers,
    generate_post,
    api_upload_image,
)
from flog.models import User, Post, Comment, db, Column, Notification, Group
from flog.fakes import fake


def test_api_index(client):
    response = client.get("/api/v3")
    data = response.get_json()
    assert data["api_version"] == "3.0"


def test_token(client):
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

    response = client.post(
        "/api/v3/token/verify", data=dict(token=data.get("access_token"))
    )
    assert response.status_code == 200
    response = client.post("/api/v3/token/verify", data=dict(token="FAKE-TOKEN"))
    assert response.status_code == 401


def test_user(client):
    test_user_data = {
        "username": "test",
        "password": "password",
        "email": "test@example.com",
    }
    response = client.post("/api/v3/register", data=test_user_data)
    print(response.get_json())
    assert response.status_code == 200

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
    register(client, "test2", "test2", "123456", "test2@example.com")
    user = User.query.filter_by(username="test").first()
    post = Post(
        private=False,
        title="abc",
        content="1234",
        author=user,
    )
    db.session.add(post)
    db.session.commit()
    response = client.get(f"/api/v3/post/{post.id}")
    data = response.get_json()
    assert data["title"] == post.title

    # test PUT /api/v3/post/{post.id}
    put_data = {"title": "ABCD", "content": "<p>test</p>", "private": True}
    response = client.put(
        f"/api/v3/post/{post.id}", headers=get_api_v3_headers(client), json=put_data
    )
    data = response.get_json()

    assert data["private"] is True

    # test get private posts without authentication
    response = client.get(f"/api/v3/user/{user.id}/posts")
    assert response.status_code == 200
    data = response.get_json()
    assert data == []  # should be empty since the user has no public posts
    # test get private posts with ANOTHER user's authentication
    response = client.get(
        f"/api/v3/user/{user.id}/posts",
        headers=get_api_v3_headers(client, "test2", "123456", "InvalidToken"),
    )
    data = response.get_json()
    assert data == []
    # test get private posts WITH author's authentication
    response = client.get(
        f"/api/v3/user/{user.id}/posts", headers=get_api_v3_headers(client)
    )
    data = response.get_json()
    assert any(post["title"] == "ABCD" for post in data)

    # test get private posts WITHOUT authentication
    response = client.get(f"/api/v3/post/{post.id}")
    assert response.status_code == 403

    response = client.get(f"/api/v3/post/{post.id}", headers=get_api_v3_headers(client))
    assert response.status_code == 200

    # test get private post with admin permission
    response = client.get(
        f"/api/v3/post/{post.id}",
        headers=get_api_v3_headers(
            client,
            username=current_app.config["FLOG_ADMIN"],
            password=current_app.config["FLOG_ADMIN_PASSWORD"],
        ),
    )
    assert response.status_code == 200

    # test get ALL posts with/without author's authentication
    response = client.get("/api/v3/post/all", headers=get_api_v3_headers(client))
    data = response.get_json()
    assert any(post["title"] == "ABCD" for post in data)

    response = client.get("/api/v3/post/all")
    data = response.get_json()
    assert not any(post["title"] == "ABCD" for post in data)

    # test add posts
    response = client.post(
        "/api/v3/post/add",
        json=dict(title="abcd", content="test content", private=False),
        headers=get_api_v3_headers(client),
    )
    query = Post.query.filter_by(title="abcd")
    assert response.status_code == 200
    assert query.count() == 1
    post = query.first()

    # test delete posts
    response = client.delete(
        f"/api/v3/post/{post.id}", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 204
    assert query.count() == 0


def test_comments(client):
    register(client)
    comment = Comment.query.get(1)
    comment.author = User.query.filter_by(username="test").first()
    db.session.commit()
    response = client.get("/api/v3/comment/1")
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

    response = client.delete("/api/v3/comment/1", headers=get_api_v3_headers(client))
    assert response.status_code == 204
    assert Comment.query.get(1) is None

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


def test_column(client):
    register(client)
    data = {"name": "test-column"}
    response = client.post(
        "/api/v3/column/create", headers=get_api_v3_headers(client), json=data
    )
    assert response.status_code == 200
    assert response.get_json()["author"]["username"] == "test"
    column = Column.query.filter_by(name="test-column").first()

    post = dict(title="1234", content="content", column_ids=[column.id])
    response = client.post(
        "/api/v3/post/add", headers=get_api_v3_headers(client), json=post
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["columns"][0]["id"] == column.id

    post2 = dict(title="abcd", content="foobar")
    client.post("/api/v3/post/add", headers=get_api_v3_headers(client), json=post2)
    post2 = Post.query.filter_by(title="abcd").first()
    column2 = dict(name="column2", post_ids=[post2.id])
    response = client.post(
        "/api/v3/column/create", headers=get_api_v3_headers(client), json=column2
    )
    assert response.status_code == 200
    assert "posts" in response.get_json()
    column2 = Column.query.filter_by(name="column2").first()
    assert post2 in column2.posts

    response = client.get(f"/api/v3/column/{column2.id}")
    assert response.status_code == 200
    assert response.get_json()["name"] == "column2"

    post3 = dict(title="efgh", content="hello world")
    client.post("/api/v3/post/add", headers=get_api_v3_headers(client), json=post3)
    post3 = Post.query.filter_by(title="efgh").first()

    response = client.put(
        f"/api/v3/column/{column2.id}",
        json=dict(name="foobar", post_ids=[post2.id, post3.id]),
        headers=get_api_v3_headers(client),
    )
    assert response.status_code == 200
    assert response.get_json()["name"] == "foobar"

    response = client.delete(
        f"/api/v3/column/{column2.id}", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 204
    assert (
        Column.query.filter_by(name="foobar").count() == 0
    )  # ensure the column is deleted.


def test_self(client):
    register(client)
    response = client.get("/api/v3/self", headers=get_api_v3_headers(client))
    assert response.get_json()["username"] == "test"

    post = dict(title="1234", content="content")
    client.post("/api/v3/post/add", headers=get_api_v3_headers(client), json=post)

    response = client.get("/api/v3/self/posts", headers=get_api_v3_headers(client))
    assert response.get_json()[0]["title"] == "1234"


def test_image(client):
    register(client)
    data = api_upload_image(
        client,
        "/api/v3",
        get_api_v3_headers(client, content_type="multipart/form-data"),
    )["data"]
    assert data["filename"] == "test_test.png"
    image_id = data["id"]
    response = client.delete(
        f"/api/v3/image/{image_id}", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 204


def test_notifications(client):
    register(client)
    user = User.query.filter_by(username="test").first()
    notification_array = []
    for _ in range(5):
        n = Notification(receiver=user, message=fake.sentence())
        db.session.add(n)
        db.session.commit()
        notification_array.append(n)
    response = client.get(
        "/api/v3/notification/all", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 200
    assert len(response.get_json()) == 5

    response = client.get("/api/v3/notification/1", headers=get_api_v3_headers(client))
    assert response.status_code == 200
    assert response.get_json()["id"] == notification_array[0].id

    register(client, "Test2", "test2", "pwd", "t@example.com")
    response = client.get(
        "/api/v3/notification/1", headers=get_api_v3_headers(client, "test2", "pwd")
    )
    assert response.status_code == 403
    response = client.delete(
        "/api/v3/notification/1", headers=get_api_v3_headers(client, "test2", "pwd")
    )
    assert response.status_code == 403

    response = client.delete(
        "/api/v3/notification/1", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 204


def test_group(client):
    register(client)
    u2 = User(username="u2", email="u2@example.com")
    u2.set_password("123456")
    db.session.add(u2)
    db.session.commit()

    # test create group with private
    g_dict = dict(name="test-group", private=True)
    response = client.post(
        "/api/v3/group/create", json=g_dict, headers=get_api_v3_headers(client)
    )
    assert response.status_code == 200
    g = Group.query.filter_by(name="test-group").first()

    response = client.get(
        f"/api/v3/group/{g.id}", headers=get_api_v3_headers(client, "u2", "123456")
    )
    assert response.status_code == 403

    # test create group with members
    g_dict = dict(name="test-group2", members=[u2.id])
    response = client.post(
        "/api/v3/group/create", json=g_dict, headers=get_api_v3_headers(client)
    )
    assert response.status_code == 200
    g = Group.query.filter_by(name="test-group2").first()

    response = client.get(
        f"/api/v3/group/{g.id}", headers=get_api_v3_headers(client, "u2", "123456")
    )
    assert response.status_code == 200

    # test PUT group
    modified = dict(members=[u2.id])
    response = client.put(
        f"/api/v3/group/{g.id}", headers=get_api_v3_headers(client), json=modified
    )
    assert response.status_code == 200
    data = response.get_json()
    
    assert any(u2.id == u["id"] for u in data["members"])

    # test DELETE group
    response = client.delete(
        f"/api/v3/group/{g.id}", headers=get_api_v3_headers(client)
    )
    assert response.status_code == 204
