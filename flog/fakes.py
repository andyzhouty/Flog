"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from random import randint
import click
from faker import Faker
from .utils import lower_username
from .models import db, Post, Feedback, User, Role, Comment, Notification, Group

fake = Faker()


def users(count: int = 2) -> None:
    """Generates fake users"""
    for i in range(count):
        name = fake.name()
        username = lower_username(name)
        # Ensure the username is unique.
        if User.query.filter_by(username=username).first() is not None:
            continue
        user = User(
            username=username,
            name=name,
            email=fake.email(),
            confirmed=True,
        )
        user.set_password('123456')
        user.role = Role.query.filter_by(name='User').first()
        db.session.add(user)
    db.session.commit()


def posts(count: int = 2) -> None:
    """Generates fake posts"""
    for i in range(count):
        post = Post(
            title=fake.word() + ' ' + fake.word(),
            content=fake.text(randint(100, 300)),
            timestamp=fake.date_time_this_year(),
            private=bool(randint(0, 1))
        )
        post.author = User.query.get(randint(1, User.query.count()))
        db.session.add(post)
    db.session.commit()


def comments(count: int = 2) -> None:
    """Generates fake comments for posts."""
    for i in range(count):
        comment = Comment(
            author=User.query.get(randint(1, User.query.count())),
            post=Post.query.get(randint(1, User.query.count())),
            body=fake.text()
        )
        db.session.add(comment)
    db.session.commit()


def feedbacks(count: int = 2) -> None:
    """Generates fake feedbacks"""
    for i in range(count):
        feedback = Feedback(
            author=User.query.get(randint(0, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(feedback)
    db.session.commit()


def follows(count: int = 20) -> None:
    """Generates fake follow relationships"""
    admin_role = Role.query.filter_by(name='Administrator').first()
    admin = User.query.filter_by(role=admin_role).first()
    for i in range(count):
        user1 = User.query.get(randint(1, User.query.count()))
        user2 = User.query.get(randint(1, User.query.count()))
        if not (user1 or user2):
            continue
        if user1.role != admin_role and admin:
            user1.follow(admin)
        elif not admin and user1 != user2:
            user1.follow(user2)


def notifications(count: int, receiver: User = None) -> None:
    """Generates fake notifications"""
    for i in range(count):
        if receiver is None:
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User.query.filter_by(role=admin_role).first()
            receiver = admin
        notification = Notification(
            message=fake.sentence(),
            receiver=receiver,
        )
        db.session.add(notification)
    db.session.commit()


def groups(count: int) -> None:
    """Generates fake user groups"""
    for i in range(count):
        manager = User.query.get(randint(1, User.query.count()))
        group = Group(
            name=fake.sentence(),
            manager=manager
        )
        manager.join_group(group)
        db.session.add(group)
    db.session.commit()
