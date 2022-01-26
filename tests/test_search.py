"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog.models import db, User, Group

from .conftest import Testing


class SearchTestCase(Testing):
    def setUp(self):
        super().setUp()
        self.register()
        self.login()

    def test_post_public(self):
        self.generate_post("abcd")
        self.generate_post("efgh")
        self.generate_post("ijklmn")
        response = self.client.get("/search/?q=ab&category=post")
        assert response.status_code == 200
        response_data = response.get_data(as_text=True)
        assert "abcd" in response_data
        assert "efgh" not in response_data
        assert "ijklmn" not in response_data

    def test_post_private(self):
        self.generate_post("abcd", private=True)
        response = self.client.get("/search/?q=ab&category=post")
        assert "abcd" in response.get_data(as_text=True)
        self.logout()

        self.login("test", "password")
        response = self.client.get("/search/?q=ab&category=post")
        assert "abcd" not in response.get_data(as_text=True)

    def test_group_public(self):
        group1 = Group(manager=self.admin, name="xyz")
        db.session.add(group1)
        db.session.commit()
        response_data = self.client.get("/search/?q=xyz&category=post").get_data(
            as_text=True
        )
        assert "Group name: xyz" not in response_data
        response_data = self.client.get("/search/?q=xyz&category=group").get_data(
            as_text=True
        )
        assert "Group name: xyz" in response_data
        response_data = self.client.get(
            f"/search/?q={self.admin.username[:2]}&category=user"
        ).get_data(as_text=True)
        assert self.admin.username in response_data

        self.generate_column("foobar")
        response_data = self.client.get("/search/?q=foobar&category=column").get_data(
            as_text=True
        )
        assert "Column name: " in response_data
        assert "foobar" in response_data

    def test_group_private(self):
        group = Group(manager=self.admin, name="xyz", private=True)
        db.session.add(group)
        db.session.commit()

        response = self.client.get("/search/?q=xy&category=group")
        assert "xyz" in response.get_data(as_text=True)
        self.logout()

        self.login("test", "password")
        response = self.client.get("/search/?q=xy&category=group")
        assert "xyz" not in response.get_data(as_text=True)
