"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from random import randint
from faker import Faker
from flask import current_app, request
from flog.models import db, Role, User, Group
from flog.extensions import mail
from .helpers import *

fake = Faker()


def test_register(client):
    response = client.get("/auth/register/")
    assert response.status_code == 200
    response = register(client)
    response_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "You can now login!" in response_data

    # test if a logined user can be redirected to main page
    login(client, "test", "password")
    reg_response = client.get("/auth/register/", follow_redirects=True)
    main_response = client.get("/")
    assert reg_response.get_data() == main_response.get_data()


def test_login_logout(client):
    response = login(client)
    response_data = response.get_data(as_text=True)
    assert (
        f'Welcome, Administrator\n {current_app.config["FLOG_ADMIN"]}' in response_data
    )
    # test if the login redirection works
    login_response = client.get("/auth/login/", follow_redirects=True)
    main_response = client.get("/")
    login_res_data = login_response.get_data()
    main_res_data = main_response.get_data()
    assert login_res_data == main_res_data
    response = logout(client)
    assert "You have been logged out" in response.get_data(as_text=True)


def test_fail_login(client):
    fail_login_res = login(client, password="wrong_password")
    res_data = fail_login_res.get_data(as_text=True)
    assert "Invalid username or password!" in res_data


def test_register_login_and_confirm(client):
    register(client)
    login_response = login(client, username="test", password="password")
    assert "test" in login_response.get_data(as_text=True)
    user = User.query.filter_by(email="test@example.com").first()
    response = client.get(f"/auth/confirm/resend/", follow_redirects=True)
    assert response.status_code == 200
    client.get(
        f"/auth/confirm/{user.generate_confirmation_token()}/", follow_redirects=True
    )
    assert user.confirmed


def test_edit_profile(client):

    user = User(name="abcd", username="abcd", email="test@example.com", confirmed=True)
    user.role = Role.query.filter_by(name="User").first()
    user.set_password("123456")
    db.session.add(user)
    db.session.commit()
    login(client, username="abcd", password="123456")
    response = client.get("/profile/edit/")
    response_data = response.get_data(as_text=True)
    assert "abcd" in response_data

    data = {
        "name": fake.name(),
        "location": fake.address(),
        "about_me": fake.sentence(),
    }
    response = client.post("/profile/edit/", data=data, follow_redirects=True)
    user = User.query.filter_by(username="abcd").first()
    assert user.name == data["name"]
    assert user.location == data["location"]
    assert user.about_me == data["about_me"]
    logout(client)

    login(client)
    response = client.get("/profile/edit/")
    assert response.status_code == 302
    response = client.get("/profile/edit/", follow_redirects=True)
    response2 = client.get("/admin/user/1/profile/edit/")
    assert response.get_data(as_text=True) == response2.get_data(as_text=True)
    logout(client)

    user = User(name="xyz", username="xyz", email="test@example.com", confirmed=False)
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    login(client, "xyz", "secret")
    response = client.get("/profile/edit/", follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert "Your email has not been confirmed yet!" in response_data


def test_delete_account(client):
    login(client)
    user_count = User.query.count()
    response = client.post(
        "/auth/account/delete/",
        data={"password": current_app.config["FLOG_ADMIN_PASSWORD"]},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert User.query.count() == user_count - 1


def test_follow(client):

    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    user = User.query.filter_by(role=Role.query.filter_by(name="User").first()).first()
    data = client.post(f"/follow/{user.username}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "User followed." in data
    assert admin.is_following(user)
    data = client.post(f"/follow/{user.username}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "Already followed" in data
    data = client.post(f"/unfollow/{user.username}", follow_redirects=True).get_data(
        as_text=True
    )
    assert "User unfollowed." in data
    assert not admin.is_following(user)


def test_all_users(client):
    login(client)
    response = client.get("/user/all/")
    data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert f'<p style="display: none">{User.query.count()}</p>' in data


def test_change_password_with_auth(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    form_data = {"password": "abcd1234", "password_again": "abcd1234"}
    response = client.post("/password/change/", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert admin.verify_password("abcd1234")


def test_reset_password_without_auth(client_with_request_ctx):
    client = client_with_request_ctx
    random_user_id = randint(1, User.query.count())
    user = User.query.get(random_user_id)
    with mail.record_messages() as outbox:
        response = client.post(
            "/password/forget/", data=dict(email=user.email), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        assert len(outbox) == 1
        assert "A confirmation email has been sent." in data
    token = user.generate_confirmation_token()
    response = client.post(
        f"/password/reset/{token}/",
        data=dict(password="abcd1234", password_again="abcd1234"),
        follow_redirects=True,
    )
    data = response.get_data(as_text=True)
    assert "Password Changed" in data
    assert request.path == "/"
    assert user.verify_password("abcd1234")


def test_block_user(client):
    user = User(name="xyz", username="xyz", email="test@example.com")
    user.set_password("secret")
    db.session.add(user)
    db.session.commit()

    login(client, "xyz", "secret")
    response = client.post(f"/admin/block/{user.id}/")
    assert response.status_code == 403
    logout(client)

    moderator = User(
        name="moderator",
        username="moderator",
        email="moderator@example.com",
        confirmed=True,
        role=Role.query.filter_by(name='Moderator').first()
    )
    moderator.set_password("secr3t")
    db.session.add(moderator)
    db.session.commit()
    login(client, "moderator", "secr3t")
    response = client.post(f"/admin/block/{user.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert user.locked

    response = client.post(f"/admin/unblock/{user.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert not user.locked
