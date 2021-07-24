import random

from flog.models import db, User, Role, Group, Notification, Message
from .helpers import register, login, logout


def test_create_group(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    response = client.get("/group/create/")
    assert response.status_code == 200
    data = {"group_name": "test_group"}
    response = client.post("/group/create/", data=data, follow_redirects=True)
    assert response.status_code == 200
    group = Group.query.filter_by(name=data["group_name"]).first()
    assert group is not None
    assert admin.in_group(group)


def test_join_group(client):
    register(client)
    login(client, "test", "password")
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    data = {"group_name": "test_group"}
    client.post("/group/create/", data=data, follow_redirects=True)
    group = Group.query.filter_by(name=data["group_name"]).first()
    logout(client)
    login(client)
    assert not admin.in_group(group)
    token = group.generate_join_token()
    response = client.get(f"/group/join/{token}/", follow_redirects=True)
    assert response.status_code == 200
    assert admin.in_group(group)


def test_find_group(client):
    register(client)
    login(client, "test", "password")
    data = {"group_name": "test_group"}
    client.post("/group/create/", data=data, follow_redirects=True)
    logout(client)
    login(client)
    notifaction_count = Notification.query.count()
    response = client.get("/group/find/")
    assert response.status_code == 200
    fake_data = {"group_name": "not existing"}
    response = client.post("/group/find/", data=fake_data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert "No such group" in response_data
    response = client.post("/group/find/", data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "We have sent a notification to the manager of the group." in response_data
    assert Notification.query.count() == notifaction_count + 1


def test_group_invite(client):
    register(client)
    login(client, "test", "password")
    data = {"group_name": "test_group"}
    client.post("/group/create/", data=data, follow_redirects=True)
    notification_count = Notification.query.count()
    group = Group.query.filter_by(name=data["group_name"]).first()
    data = {"group_id": group.id}
    response = client.get("/group/invite/1/")
    assert response.status_code == 200
    response = client.post("/group/invite/1/", data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert Notification.query.count() == notification_count + 1
    assert "Notification sent to user" in response_data


def test_group_hint_ajax(client):
    login(client)
    data1 = {"group_name": "test_group"}
    data2 = {"group_name": "test_group1234abcd"}
    data3 = {"group_name": "test_group1", "private": True}
    client.post("/group/create/", data=data1, follow_redirects=True)
    client.post("/group/create/", data=data2, follow_redirects=True)
    client.post("/group/create/", data=data3, follow_redirects=True)
    response = client.get("/ajax/group/hint/?q=test")
    response_data = response.get_json()
    assert response.status_code == 200
    assert data1["group_name"] in response_data["hint"]
    assert data2["group_name"] in response_data["hint"]
    assert data3["group_name"] in response_data["hint"]
    logout(client)
    register(client)
    login(client, "test", "password")
    response = client.get("/ajax/group/hint/?q=test")
    response_data = response.get_json()
    assert data3["group_name"] not in response_data["hint"]
    logout(client)
    login(client)
    assert len(response_data["hint"]) == 2
    response = client.get("/ajax/group/hint/?q=1234")
    response_data = response.get_json()
    assert data2["group_name"] in response_data["hint"]
    assert data1["group_name"] not in response_data["hint"]


def test_group_info(client):
    register(client)
    login(client, "test", "password")
    data = {"group_name": "test_group"}
    client.post("/group/create/", data=data, follow_redirects=True)
    g = Group.query.filter_by(name="test_group").first()
    response = client.get(f"/group/{g.id}/info/")
    assert response.status_code == 200


def test_group_discussions(client):
    register(client)
    login(client, "test", "password")
    data = {"group_name": "test_group"}
    client.post("/group/create/", data=data, follow_redirects=True)
    g = Group.query.filter_by(name="test_group").first()
    response = client.get(f"/group/{g.id}/discussion/")
    assert response.status_code == 200
    response = client.post(f"/group/{g.id}/discussion/", data=dict(body="hello"))
    assert response.status_code == 200
    m = Message.query.filter_by(body="hello").first()
    assert m in g.messages
    logout(client)
    login(client)
    response = client.post(f"/group/{g.id}/discussion/", data=dict(body="hello"))
    assert response.status_code == 403
    logout(client)
    u = User.query.get(1)
    g.members.append(u)
    login(client, "test", "password")
    c = Notification.query.count()
    response = client.post(f"/group/{g.id}/discussion/", data=dict(body="hello"))
    assert Notification.query.count() == c + 1


def test_group_all(client):
    register(client)
    login(client, "test", "password")
    data = dict(group_name="test_group", private=True)
    client.post("/group/create/", data=data, follow_redirects=True)
    g1 = Group.query.filter_by(name="test_group").first()
    response = client.get("/group/all/")
    assert g1.name not in response.get_data(as_text=True)
    logout(client)
    login(client)  # login as administrator
    response = client.get("/group/all/")
    assert g1.name in response.get_data(as_text=True)


def test_kick_out(client):
    register(client)
    g = Group()
    u = User.query.filter_by(username="test").first()
    g.members.append(u)
    g.manager = u
    u2 = User.query.get(random.randint(2, 5))
    g.members.append(u2)
    db.session.commit()

    login(client, u2.username, "123456")
    response = client.post(f"/group/{g.id}/kick/{u.id}/")
    assert response.status_code == 403
    logout(client)

    login(client, "test", "password")
    response = client.post(f"/group/{g.id}/kick/{u2.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert u2 not in g.members


def test_set_manager(client):
    register(client)
    g = Group()
    u = User.query.filter_by(username="test").first()
    g.members.append(u)
    g.manager = u
    u2 = User.query.get(random.randint(2, 5))
    g.members.append(u2)
    db.session.commit()

    login(client, u2.username, "123456")
    response = client.get(f"/group/{g.id}/set-manager/{u.id}/")
    assert response.status_code == 403
    logout(client)

    login(client, "test", "password")
    response = client.get(f"/group/{g.id}/set-manager/{u2.id}/")
    assert response.status_code == 200
    response = client.post(f"/group/{g.id}/set-manager/{u2.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert g.manager == u2
 
