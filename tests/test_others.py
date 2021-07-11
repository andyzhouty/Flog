"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import current_app
from flog.models import User
from .helpers import login, logout


def test_change_theme_fail(client):
    theme = "unknown_theme!"
    response = client.get(f"/change-theme/{theme}/", follow_redirects=True)
    assert response.status_code == 404


def test_change_theme_success(client):
    for theme in current_app.config["BOOTSTRAP_THEMES"]:
        client.get(f"/change-theme/{theme}/", follow_redirects=True)
        cookie = next(
            (cookie for cookie in client.cookie_jar if cookie.name == "theme"), None
        )
        assert cookie is not None
        assert cookie.value == theme


def test_redirections(client_with_request_ctx):
    client = client_with_request_ctx
    response = client.get("/login/", follow_redirects=True)
    login_response = client.get("/auth/login/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == login_response.get_data(as_text=True)

    response = client.get("/register/", follow_redirects=True)
    register_response = client.get("/auth/register/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == register_response.get_data(as_text=True)

    login(client)
    response = client.get("/admin/", follow_redirects=True)
    main_response = client.get("/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == main_response.get_data(as_text=True)


def test_about(client):
    login(client)
    admin = User.query.get(1)
    admin.locale = "en_US"
    response = client.get("/about/")
    assert response.status_code == 200
    logout(client)

    response2 = client.get("/about/")
    assert response2.status_code == 200
