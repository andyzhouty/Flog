"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from .helpers import generate_post, login, logout, register
from flog.models import db, User, Role, Post


def test_language_selection(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    admin.locale = "en_US"
    client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True)
    assert admin.locale == "zh_Hans_CN"


def test_language_selection_404(client):
    login(client)
    response = client.get("/language/set-locale/fake-language/", follow_redirects=True)
    assert response.status_code == 404


def test_no_login_language_selection(client):
    client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True)
    data = client.get("/").get_data(as_text=True)
    assert "加入我们" in data


def test_notification_language(client):
    """Test the notification received is in the receiver's language instead of the sender's."""
    # generate a post 
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    admin.locale = "zh_Hans_CN"
    db.session.commit()
    title = generate_post(client)["title"]
    post = Post.query.filter_by(title=title).first()
    logout(client)

    register(client)
    login(client, "test", "password")
    user = User.query.filter_by(username="test").first()
    user.locale = "en_US"
    db.session.commit()
    # test using the post collecting route
    client.get(f"/post/collect/{post.id}/")
    logout(client)

    assert "文章" in admin.notifications[-1].message
