"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import json
from flask import url_for
from random import randint
from flog.models import Comment, Notification, Post, User, Role
from flog.notifications import (
    push_collect_notification,
    push_comment_notification,
    push_follow_notification,
)
from flog.utils import lower_username, is_safe_url

from .conftest import Testing


class UtilsTestCase(Testing):
    def test_lower_username(self):
        username = "Test User"
        assert lower_username(username) == "testuser"

    def test_is_safe_url(self):
        target = url_for("main.main", _external=True)
        assert is_safe_url(target)


class NotificationTestCase(Testing):
    def test_push_notifications(self):
        # test if the push_*_notification functions work.
        random_user_id = randint(1, User.query.count() - 1)
        random_post_id = randint(1, Post.query.count())
        collector = User.query.get(random_user_id)
        receiver = User.query.get(random_user_id + 1)
        post = Post.query.get(random_post_id)
        push_collect_notification(collector, receiver, post)

        assert Notification.query.count() == 1
        follower = collector
        push_follow_notification(follower, receiver)

        assert Notification.query.count() == 2
        random_comment_id = randint(1, Comment.query.count())
        comment = Comment.query.get(random_comment_id)
        while not comment.post:
            random_comment_id = randint(1, Comment.query.count())
            comment = Comment.query.get(random_comment_id)
        push_comment_notification(comment, receiver)
        assert Notification.query.count() == 3

    def test_notifications(self):
        self.login()
        for i in range(5):
            self.send_notification()

        assert len(self.admin.notifications) == 5
        assert Notification.query.count() == 5

        response = self.client.get("/notification/")
        assert response.status_code == 200
        str_data = (
            self.client.get("/ajax/notification/count/").get_data(as_text=True).strip()
        )
        data = json.loads(str_data)
        assert dict(count=5) == data
        self.client.post("/notification/read/1/")
        assert Notification.query.count() == 4
        self.client.post("/notification/read/all/")
        assert Notification.query.count() == 0
        str_data = (
            self.client.get("/ajax/notification/count/").get_data(as_text=True).strip()
        )
        data = json.loads(str_data)
        assert dict(count=0) == data

    def test_redirections(self):
        """test if is_safe_url() works"""
        response = self.client.get(
            "/redirect?next=http://example.com", follow_redirects=True
        )
        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert "Flog" in data

    def test_ignored_notifications(self):
        """
        Test when a user write a comment to his own article, he will not be notified.
        """
        self.login()
        initial_notification_count = Notification.query.count()
        title = self.generate_post()["post"]["title"]
        post = Post.query.filter_by(title=title).first()
        self.client.post(
            f"/post/{post.id}/", data={"body": "lorem ipsum"}, follow_redirects=True
        )
        assert Notification.query.count() == initial_notification_count
