"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from random import randint
from faker import Faker
from flask import current_app, request
from flog.models import db, User, Group
from flog.extensions import mail
from .conftest import Testing


fake = Faker()


class UserTestCase(Testing):
    def test_register(self):
        response = self.client.get("/auth/register/")
        assert response.status_code == 200
        response = self.register()
        response_data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "You can now login!" in response_data

        # test if a logined user can be redirected to main page
        self.login("test", "password")
        reg_response = self.client.get("/auth/register/", follow_redirects=True)
        main_response = self.client.get("/")
        assert reg_response.get_data() == main_response.get_data()

    def test_login_logout(self):
        response = self.login()
        response_data = response.get_data(as_text=True)
        assert "Welcome" in response_data
        # test if the login redirection works
        login_response = self.client.get("/auth/login/", follow_redirects=True)
        main_response = self.client.get("/")
        login_res_data = login_response.get_data()
        main_res_data = main_response.get_data()
        assert login_res_data == main_res_data
        response = self.logout()
        assert "You have been logged out" in response.get_data(as_text=True)

    def test_fail_login(self):
        fail_login_res = self.login(password="wrong_password")
        res_data = fail_login_res.get_data(as_text=True)
        assert "Invalid username or password!" in res_data

    def test_register_login_and_confirm(self):
        self.register()
        login_response = self.login(username="test", password="password")
        assert "test" in login_response.get_data(as_text=True)
        user = User.query.filter_by(email="test@example.com").first()
        response = self.client.get(f"/auth/confirm/resend/", follow_redirects=True)
        assert response.status_code == 200
        self.client.get(
            f"/auth/confirm/{user.generate_confirmation_token()}/",
            follow_redirects=True,
        )
        assert user.confirmed

    def test_edit_profile(self):

        user = User(
            name="abcd", username="abcd", email="test@example.com", confirmed=True
        )
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        self.login(username="abcd", password="123456")
        response = self.client.get("/profile/edit/")
        response_data = response.get_data(as_text=True)
        assert "abcd" in response_data

        data = {
            "username": "abcd",
            "name": fake.name(),
            "location": fake.address(),
            "about_me": fake.sentence(),
            "custom_avatar_url": "https://example.com/test.png",
        }
        response = self.client.post("/profile/edit/", data=data, follow_redirects=True)
        assert response.status_code == 200
        user = User.query.filter_by(username="abcd").first()
        assert user.name == data["name"]
        assert user.location == data["location"]
        assert user.about_me == data["about_me"]
        assert user.custom_avatar_url == data["custom_avatar_url"]
        self.logout()

        self.login()
        response = self.client.get("/profile/edit/")
        assert response.status_code == 302
        response = self.client.get("/profile/edit/", follow_redirects=True)
        response2 = self.client.get("/admin/user/1/profile/edit/")
        assert response.get_data(as_text=True) == response2.get_data(as_text=True)
        self.logout()

        user = User(
            name="xyz", username="xyz", email="test@example.com", confirmed=False
        )
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

    def test_delete_account(self):
        self.login()
        user_count = User.query.count()
        response = self.client.post(
            "/auth/account/delete/",
            data={"password": current_app.config["FLOG_ADMIN_PASSWORD"]},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert User.query.count() == user_count - 1

    def test_follow(self):

        self.login()
        self.admin = User.query.filter_by(is_admin=True).first()
        user = User.query.filter_by(is_admin=False).first()
        data = self.client.post(
            f"/follow/{user.username}", follow_redirects=True
        ).get_data(as_text=True)
        assert "User followed." in data
        assert self.admin.is_following(user)
        data = self.client.post(
            f"/follow/{user.username}", follow_redirects=True
        ).get_data(as_text=True)
        assert "Already followed" in data
        data = self.client.post(
            f"/unfollow/{user.username}", follow_redirects=True
        ).get_data(as_text=True)
        assert "User unfollowed." in data
        assert not self.admin.is_following(user)

    def test_all_users(self):
        self.login()
        response = self.client.get("/user/all/")
        data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert f'<p style="display: none">{User.query.count()}</p>' in data

    def test_change_password_with_auth(self):
        self.login()
        form_data = {"password": "abcd1234", "password_again": "abcd1234"}
        response = self.client.post(
            "/password/change/", data=form_data, follow_redirects=True
        )
        assert response.status_code == 200
        assert self.admin.verify_password("abcd1234")

    def test_reset_password_without_auth(self):
        random_user_id = randint(1, User.query.count())
        user = User.query.get(random_user_id)
        with mail.record_messages() as outbox:
            response = self.client.post(
                "/password/forget/", data=dict(email=user.email), follow_redirects=True
            )
            data = response.get_data(as_text=True)
            assert len(outbox) == 1
            assert "A confirmation email has been sent." in data
        token = user.generate_confirmation_token()
        response = self.client.post(
            f"/password/reset/{token}/",
            data=dict(password="abcd1234", password_again="abcd1234"),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        assert "Password Changed" in data
        assert request.path == "/"
        assert user.verify_password("abcd1234")

    def test_block_user(self):
        user = User(name="xyz", username="xyz", email="test@example.com")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        self.login("xyz", "secret")
        response = self.client.post(f"/admin/block/{user.id}/")
        assert response.status_code == 403
        self.logout()
