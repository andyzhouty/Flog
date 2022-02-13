"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from datetime import date, datetime
from flog import db
from flog.models import User, Post, Notification, Group, Message, Column, AnonymousUser
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
        db.session.add(user)
        db.session.commit()
        user.collect(post)
        assert user.is_collecting(post)

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
        assert not anonym_user.is_administrator()

    def test_group_messages(self):
        g = Group()
        m = Message()
        g.messages.append(m)
        assert m.group == g

    def test_coins(self):
        u = User()
        u.last_seen = datetime(2021, 8, 13, 23, 59, 59)
        force_time = datetime(2021, 8, 14, 23, 59, 59)
        u.ping(force_time)
        assert u.coins == 4

        u.last_seen = datetime(2021, 8, 14)
        u.ping(force_time)
        assert u.coins == 4

    def test_level(self):
        experience_level_table = {
            0: (1, "eee"),
            100: (2, "ff9"),
            200: (3, "afa"),
            350: (4, "5d5"),
            550: (5, "0dd"),
            800: (6, "00f"),
            1100: (7, "da3"),
            1500: (8, "f00"),
        }
        u = User()
        for k, v in experience_level_table.items():
            u.experience = k
            assert u.level() == v[0]
            assert (
                u.level_badge_link()
                == "https://img.shields.io/badge/Lv" + str(v[0]) + "%20-" + v[1]
            )

    def test_lv9(self):
        u = User()
        u.experience = 2700
        assert u.level() == 10
        u.experience = 3100
        assert u.level() == 11
        assert u.level_badge_link().endswith("%20%2B2-808")
