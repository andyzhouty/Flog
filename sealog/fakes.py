"""
生成虚拟数据
"""
from random import randint
from faker import Faker
from flask import current_app
import click
from .models import db, Post, Feedback, User, Role
from .utils import slugify

fake = Faker()


def users(count: int=2) -> None:
    """生成虚拟用户"""
    for i in range(count):
        name = fake.name()
        user = User(
            username=slugify(name),
            name=name,
            email=fake.email(),
            confirmed=True
        )
        user.set_password('123456')
        user.role = Role.query.filter_by(name='User').first()
        db.session.add(user)
    db.session.commit()


def moderators(count: int=1) -> None:
    """生成虚拟协管员"""
    for i in range(count):
        name = fake.name()
        moderator = User(
            username=slugify(name),
            name=name,
            email=fake.email(),
            confirmed=True
        )
        moderator.set_password('123456')
        moderator.role = Role.query.filter_by(name='Moderator').first()
        db.session.add(moderator)
    db.session.commit()


def posts(count: int=2) -> None:
    """生成虚拟文章"""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            date=fake.date_time_this_year().strftime("%Y-%m-%d"),
            content=fake.text(randint(100, 300)),
            timestamp=fake.date_time_this_year()
        )
        post.author = User.query.get(randint(1, len(User.query.all())))
        db.session.add(post)
    db.session.commit()


def feedbacks(count: int=2) -> None:
    """生成虚拟反馈"""
    for i in range(count):
        feedback = Feedback(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(feedback)
    db.session.commit()
