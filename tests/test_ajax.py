from random import randint


def test_profile_popup(client):
    user_id = randint(2, 5)
    response = client.get(f"/ajax/profile/{user_id}/")
    assert response.status_code == 200


def test_notification_count_without_auth(client):
    response = client.get("/ajax/notification/count/")
    assert response.status_code == 401


def test_get_group_hint_without_auth(client):
    response = client.get("/ajax/group/hint/")
    assert response.status_code == 401
