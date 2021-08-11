"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog.models import db, User, Role, Group

from .conftest import Testing


class SearchTestCase(Testing):
    def test_search(self):
        self.login()

        self.generate_post("abcd")
        self.generate_post("efgh")
        self.generate_post("ijklmn")
        response = self.client.get("/search/?q=ab&category=post")
        assert response.status_code == 200
        response_data = response.get_data(as_text=True)
        assert "abcd" in response_data
        assert "efgh" not in response_data
        assert "ijklmn" not in response_data
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
