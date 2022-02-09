import random

from flog.models import db, User, Group, Notification, Message


from .conftest import Testing


class GroupTestCase(Testing):
    def test_create_group(self):
        self.login()

        response = self.client.get("/group/create/")
        assert response.status_code == 200
        data = {"group_name": "test_group"}
        response = self.client.post("/group/create/", data=data, follow_redirects=True)
        assert response.status_code == 200
        group = Group.query.filter_by(name=data["group_name"]).first()
        assert group is not None
        assert self.admin.in_group(group)

    def test_join_group(self):
        self.register()
        self.login("test", "password")

        data = {"group_name": "test_group"}
        self.client.post("/group/create/", data=data, follow_redirects=True)
        group = Group.query.filter_by(name=data["group_name"]).first()
        self.logout()
        self.login()
        assert not self.admin.in_group(group)
        token = group.generate_join_token()
        response = self.client.get(f"/group/join/{token}/", follow_redirects=True)
        assert response.status_code == 200
        assert self.admin.in_group(group)

    def test_find_group(self):
        self.register()
        self.login("test", "password")
        data = {"group_name": "test_group"}
        self.client.post("/group/create/", data=data, follow_redirects=True)
        self.logout()
        self.login()
        notifaction_count = Notification.query.count()
        response = self.client.get("/group/find/")
        assert response.status_code == 200
        fake_data = {"group_name": "not existing"}
        response = self.client.post(
            "/group/find/", data=fake_data, follow_redirects=True
        )
        response_data = response.get_data(as_text=True)
        assert "No such group" in response_data
        response = self.client.post("/group/find/", data=data, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert (
            "We have sent a notification to the manager of the group." in response_data
        )
        assert Notification.query.count() == notifaction_count + 1

    def test_group_invite(self):
        self.register()
        self.login("test", "password")
        data = {"group_name": "test_group"}
        self.client.post("/group/create/", data=data, follow_redirects=True)
        notification_count = Notification.query.count()
        group = Group.query.filter_by(name=data["group_name"]).first()
        data = {"group_id": group.id}
        response = self.client.get("/group/invite/1/")
        assert response.status_code == 200
        response = self.client.post(
            "/group/invite/1/", data=data, follow_redirects=True
        )
        response_data = response.get_data(as_text=True)
        assert response.status_code == 200
        assert Notification.query.count() == notification_count + 1
        assert "Notification sent to user" in response_data

    def test_group_hint_ajax(self):
        self.login()
        data1 = {"group_name": "test_group"}
        data2 = {"group_name": "test_group1234abcd"}
        data3 = {"group_name": "test_group1", "private": True}
        self.client.post("/group/create/", data=data1, follow_redirects=True)
        self.client.post("/group/create/", data=data2, follow_redirects=True)
        self.client.post("/group/create/", data=data3, follow_redirects=True)
        response = self.client.get("/ajax/group/hint/?q=test")
        response_data = response.get_json()
        assert response.status_code == 200
        assert data1["group_name"] in response_data["hint"]
        assert data2["group_name"] in response_data["hint"]
        assert data3["group_name"] in response_data["hint"]
        self.logout()
        self.register()
        self.login("test", "password")
        response = self.client.get("/ajax/group/hint/?q=test")
        response_data = response.get_json()
        assert data3["group_name"] not in response_data["hint"]
        self.logout()
        self.login()
        assert len(response_data["hint"]) == 2
        response = self.client.get("/ajax/group/hint/?q=1234")
        response_data = response.get_json()
        assert data2["group_name"] in response_data["hint"]
        assert data1["group_name"] not in response_data["hint"]

    def test_group_info(self):
        self.register()
        self.login("test", "password")
        data = {"group_name": "test_group"}
        self.client.post("/group/create/", data=data, follow_redirects=True)
        g = Group.query.filter_by(name="test_group").first()
        response = self.client.get(f"/group/{g.id}/info/")
        assert response.status_code == 200

    def test_group_discussions(self):
        self.register()
        self.login("test", "password")
        data = {"group_name": "test_group"}
        self.client.post("/group/create/", data=data, follow_redirects=True)
        g = Group.query.filter_by(name="test_group").first()
        response = self.client.get(f"/group/{g.id}/discussion/")
        assert response.status_code == 200
        response = self.client.post(
            f"/group/{g.id}/discussion/", data=dict(body="hello")
        )
        assert response.status_code == 200
        m = Message.query.filter_by(body="hello").first()
        assert m in g.messages
        self.logout()
        self.login()
        response = self.client.post(
            f"/group/{g.id}/discussion/", data=dict(body="hello")
        )
        assert response.status_code == 403
        self.logout()
        u = User.query.get(1)
        g.members.append(u)
        self.login("test", "password")
        c = Notification.query.count()
        response = self.client.post(
            f"/group/{g.id}/discussion/", data=dict(body="hello")
        )
        assert Notification.query.count() == c + 1

    def test_group_all(self):
        self.register()
        self.login("test", "password")
        data = dict(group_name="test_group", private=True)
        self.client.post("/group/create/", data=data, follow_redirects=True)
        g1 = Group.query.filter_by(name="test_group").first()
        response = self.client.get("/group/all/")
        assert g1.name not in response.get_data(as_text=True)
        self.logout()

    def test_kick_out(self):
        self.register()
        g = Group()
        u = User.query.filter_by(username="test").first()
        g.members.append(u)
        g.manager = u
        u2 = User.query.get(random.randint(2, 5))
        g.members.append(u2)
        db.session.commit()

        self.login(u2.username, "123456")
        response = self.client.post(f"/group/{g.id}/kick/{u.id}/")
        assert response.status_code == 403
        self.logout()

        self.login("test", "password")
        response = self.client.post(
            f"/group/{g.id}/kick/{u2.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert u2 not in g.members

    def test_set_manager(self):
        self.register()
        g = Group()
        u = User.query.filter_by(username="test").first()
        g.members.append(u)
        g.manager = u
        u2 = User.query.get(random.randint(2, 5))
        g.members.append(u2)
        db.session.commit()

        self.login(u2.username, "123456")
        response = self.client.get(f"/group/{g.id}/set-manager/{u.id}/")
        assert response.status_code == 403
        self.logout()

        self.login("test", "password")
        response = self.client.get(f"/group/{g.id}/set-manager/{u2.id}/")
        assert response.status_code == 200
        response = self.client.post(
            f"/group/{g.id}/set-manager/{u2.id}/",
            data={"password": "invalid"},
            follow_redirects=True,
        )
        assert response.status_code == 403

        response = self.client.post(
            f"/group/{g.id}/set-manager/{u2.id}/",
            data={"password": "password"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert g.manager == u2
