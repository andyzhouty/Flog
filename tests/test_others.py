"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import current_app


def test_change_theme(client):
    for theme in current_app.config['BOOTSTRAP_THEMES']:
        client.get(f"/change-theme/{theme}/", follow_redirects=True)
        cookie = next(
            (cookie for cookie in client.cookie_jar if cookie.name == "theme"),
            None
        )
        assert cookie is not None
        assert cookie.value == theme
