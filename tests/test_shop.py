from random import randint
from flask import current_app, request
from flog.models import db, Belong
from flog.extensions import mail
from .conftest import Testing


class ShopTestCase(Testing):
    def test_shop(self):
        self.login()
        response = self.client.get("/shop/")
        assert response.status_code == 200

    def test_buy(self):
        self.login()
        response = self.client.get("/shop/buy/1")
        assert response.status_code == 200
        response_data = response.get_data(as_text=True)
        assert "Success" in response_data

    def test_use(self):
        self.login()
        response = self.client.get("/shop/use/1")
        assert response.status_code == 200
        response_data = response.get_data(as_text=True)
        assert "Success" in response_data