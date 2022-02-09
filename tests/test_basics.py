"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import current_app
from .conftest import Testing


class BasicTestCase(Testing):
    def test_app_exists(self):
        assert current_app is not None

    def test_app_is_testing(self):
        assert current_app.config["TESTING"]

    def test_about_us(self):
        response = self.client.get("/about/")
        assert response.status_code == 200
