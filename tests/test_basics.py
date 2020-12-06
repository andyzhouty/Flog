"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import current_app


def test_app_exists(client_without_request_ctx):
    assert current_app is not None


def test_app_is_testing(client_without_request_ctx):
    assert current_app.config['TESTING']


def test_about_us(client_without_request_ctx):
    client = client_without_request_ctx
    response = client.get('/about-us')
    assert response.status_code == 200
