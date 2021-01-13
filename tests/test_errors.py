"""
MIT License
Copyright (c) 2020 Andy Zhou
"""

JSON_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def test_400(client):
    response = client.get("/400")
    assert response.status_code == 400

    response = client.get("/400", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "bad request"


def test_403(client):
    response = client.get("/403")
    assert response.status_code == 403

    response = client.get("/403", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "forbidden"


def test_404(client):
    response = client.get("/404")
    assert response.status_code == 404

    response = client.get("/404", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "not found"


def test_405(client):
    response = client.get("/405")
    assert response.status_code == 405

    response = client.get("/405", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "method not allowed"


def test_413(client):
    response = client.get("/413")
    assert response.status_code == 413

    response = client.get("/413", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "image file too large"


def test_500(client):
    response = client.get("/500")
    assert response.status_code == 500

    response = client.get("/500", headers=JSON_HEADERS)
    data = response.get_json()
    assert data["error"] == "internal server error"
