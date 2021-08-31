"""
MIT License
Copyright (c) 2020 Andy Zhou
"""

from tests.conftest import Production, Testing


JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


class ErrorTestCase(Testing):
    def test_400(self):
        response = self.client.get("/400")
        assert response.status_code == 400

        response = self.client.get("/400", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "bad request"

    def test_403(self):
        response = self.client.get("/403")
        assert response.status_code == 403

        response = self.client.get("/403", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "forbidden"

    def test_404(self):
        response = self.client.get("/404")
        assert response.status_code == 404

        response = self.client.get("/404", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "not found"

    def test_405(self):
        response = self.client.get("/405")
        assert response.status_code == 405

        response = self.client.get("/405", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "method not allowed"

    def test_413(self):
        response = self.client.get("/413")
        assert response.status_code == 413

        response = self.client.get("/413", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "image file too large"

    def test_429(self):
        response = self.client.get("/429")
        assert response.status_code == 429

        response = self.client.get("/429", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "too many requests"

    def test_500(self):
        response = self.client.get("/500")
        assert response.status_code == 500

        response = self.client.get("/500", headers=JSON_HEADERS)
        data = response.get_json()
        assert data["error"] == "internal server error"


class ErrorProdTestCase(Production):
    def test_production_errors(self):
        """set the testing error pages to 404 when production"""
        for error in ["/400", "/401", "/403", "/404", "/405", "/413", "/429" , "/500"]:
            response = self.client.get(error)
            assert response.status_code == 404
