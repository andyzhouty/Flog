"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog import db
from flog.models import (
    User,
    Post,
    Notification,
    Group,
    Message,
    Follow,
    Column,
    AnonymousUser,
    Permission,
)
from .conftest import Testing


class ModelTestCase(Testing):
    def test_password_setter(self):
        u = User()
        u.set_password("hello")
        assert u.password_hash is not None

    def test_password_verification(self):
        u = User()
        u.set_password("hello")
        assert u.verify_password("hello")
        assert not u.verify_password("bye")

    def test_password_salts_are_random(self):
        u1 = User()
        u2 = User()
        u1.set_password("hello")
        u2.set_password("hello")
        assert u1.password_hash != u2.password_hash

    def test_confirmation_token(self):
        u = User(email="test@example.com")
        token = u.generate_confirmation_token()
        assert u.confirm(token)

    def test_collect(self):
        user = User()
        post = Post()
        user.collect(post)
        assert user.is_collecting(post)

    def test_follow(self):
        user1 = User()
        user2 = User()
        user1.follow(user2)
        assert user1.is_following(user2)

    def test_notification(self):
        user = User()
        notification = Notification(message="Hello World", receiver=user)
        db.session.add(notification)
        db.session.commit()
        assert notification in user.notifications

    def test_group(self):
        user = User()
        group = Group()
        user.join_group(group)
        assert user.in_group(group)

    def test_block_user(self):
        user = User()
        user.lock()
        assert user.locked
        user.unlock()
        assert not user.locked

    def test_column(self):
        user = User()
        post = Post()
        column = Column()
        column.posts.append(post)
        db.session.add(column)
        db.session.commit()
        assert post in column.posts
        user.columns.append(column)
        assert column in user.columns
        assert post in user.posts

    def test_avatar_url(self):
        user = User(email="test@example.com")
        user.custom_avatar_url = "https://example.com/test.png"
        assert user.avatar_url() == "https://example.com/test.png"

    def test_print_layout(self):
        user1 = User()
        user2 = User()
        assert user1.role.__repr__() == "<Role: User>"
        user1.follow(user2)
        assert user1.is_following(user2)

        f = Follow.query.with_parent(user1).first()
        assert f.__repr__() == f"<Follow follower: '{user1}' following: '{user2}'"

    def test_delete_column(self):
        user = User()
        column = Column()
        db.session.add(column)
        db.session.commit()
        user.columns.append(column)
        assert column in user.columns
        column.delete()
        assert column not in user.columns

    def test_anonymous_permissions(self):
        anonym_user = AnonymousUser()
        assert not anonym_user.can(Permission.COMMENT)
        assert not anonym_user.is_administrator()

    def test_group_messages(self):
        g = Group()
        m = Message()
        g.messages.append(m)
        assert m.group == g
