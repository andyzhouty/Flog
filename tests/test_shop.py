from .conftest import Testing


class ShopTestCase(Testing):
    def test_shop(self):
        self.login()
        response = self.client.get("/shop/")
        assert response.status_code == 200

    def test_buy(self):
        self.login()
        response = self.client.get("/shop/buy/1")
        assert response.status_code == 302

    def test_use(self):
        self.login()
        response = self.client.get("/shop/use/1")
        assert response.status_code == 302
