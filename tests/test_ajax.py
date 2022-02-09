from random import randint
from .conftest import Testing


class AjaxTestCase(Testing):
    def test_profile_popup(self):
        user_id = randint(2, 5)
        response = self.client.get(f"/ajax/profile/{user_id}/")
        assert response.status_code == 200

    def test_notification_count_without_auth(self):
        response = self.client.get("/ajax/notification/count/")
        assert response.status_code == 401

    def test_get_group_hint_without_auth(self):
        response = self.client.get("/ajax/group/hint/")
        assert response.status_code == 401
