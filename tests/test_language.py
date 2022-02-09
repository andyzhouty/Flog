"""
MIT License
Copyright (c) 2020 Andy Zhou
"""

from flog.models import db, User, Post
from .conftest import Testing


class LanguageTestCase(Testing):
    def test_language_selection(self):
        self.login()

        self.admin.locale = "en_US"
        self.client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True)
        assert self.admin.locale == "zh_Hans_CN"

    def test_language_selection_404(self):
        self.login()
        response = self.client.get(
            "/language/set-locale/fake-language/", follow_redirects=True
        )
        assert response.status_code == 404

    def test_no_login_language_selection(self):
        self.client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True)
        data = self.client.get("/").get_data(as_text=True)
        assert "加入我们" in data

    def test_notification_language(self):
        """Test the notification received is in the receiver's language instead of the sender's."""
        self.login()
        # generate a post

        self.admin.locale = "zh_Hans_CN"
        db.session.commit()
        title = self.generate_post()["title"]
        post = Post.query.filter_by(title=title).first()
        self.logout()

        self.register()
        self.login("test", "password")
        user = User.query.filter_by(username="test").first()
        user.locale = "en_US"
        db.session.commit()
        # test using the post collecting route
        self.client.get(f"/post/collect/{post.id}/")
        self.logout()

        assert "文章" in self.admin.notifications[-1].message
