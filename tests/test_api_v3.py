from .helpers import register, login
from flog.models import User


def test_api_index(client):
    response = client.get("/api/v3/")
    data = response.get_json()
    assert data["api_version"] == "3.0"


def test_user(client):
    register(client)
    login(client, "test", "password")
    user_id = User.query.filter_by(username="test").first().id
    response = client.get(f"/api/v3/user/{user_id}/")
    data = response.get_json()
    assert data["username"] == "test"
