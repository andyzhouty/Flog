"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import current_app
from flog.models import User

from .conftest import Testing


class OtherTestCase(Testing):
    def test_change_theme_fail(self):
        theme = "unknown_theme!"
        response = self.client.get(f"/change-theme/{theme}/", follow_redirects=True)
        assert response.status_code == 404

    def test_change_theme_success(self):
        for theme in current_app.config["BOOTSTRAP_THEMES"]:
            self.client.get(f"/change-theme/{theme}/", follow_redirects=True)
            cookie = next(
                (cookie for cookie in self.client.cookie_jar if cookie.name == "theme"),
                None,
            )
            assert cookie is not None
            assert cookie.value == theme

    def test_redirections(self):
        response = self.client.get("/login/", follow_redirects=True)
        login_response = self.client.get("/auth/login/")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == login_response.get_data(as_text=True)

        response = self.client.get("/register/", follow_redirects=True)
        register_response = self.client.get("/auth/register/")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == register_response.get_data(
            as_text=True
        )

        self.login()
        response = self.client.get("/admin/", follow_redirects=True)
        main_response = self.client.get("/")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == main_response.get_data(as_text=True)

    def test_about(self):
        self.login()
        admin = User.query.get(1)
        self.admin.locale = "en_US"
        response = self.client.get("/about/")
        assert response.status_code == 200
        self.logout()

        response2 = self.client.get("/about/")
        assert response2.status_code == 200
