"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from random import randint
from faker import Faker
from .models import Notification, db, Post, Feedback, User, Role, Comment
from .utils import slugify

fake = Faker()


def users(count: int=2) -> None:
    """Generates fake users"""
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
    """Generates fake moderators"""
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
    """Generates fake posts"""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            date=fake.date_time_this_year().strftime("%Y-%m-%d"),
            content=fake.text(randint(100, 300)),
            timestamp=fake.date_time_this_year()
        )
        post.author = User.query.get(randint(1, User.query.count()))
        db.session.add(post)
    db.session.commit()


def comments(count: int=2) -> None:
    """Generates fake comments for posts."""
    for i in range(count):
        comment = Comment(
            author=User.query.get(randint(0, User.query.count())),
            post=Post.query.get(randint(0, User.query.count())),
            body=fake.text()
        )
        db.session.add(comment)
    db.session.commit()


def notifications(count: int=2) -> None:
    admin_role = Role.query.filter_by(name='Administrator').first()
    admin = User.query.filter_by(role=admin_role).first()
    for i in range(count):
        notification = Notification(
            is_read=False,
            message=fake.sentence(),
            receiver=admin
        )
        db.session.add(notification)
    db.session.commit()

def feedbacks(count: int=2) -> None:
    """Generates fake feedbacks"""
    for i in range(count):
        feedback = Feedback(
            author=User.query.get(randint(0, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(feedback)
    db.session.commit()


def follows(count: int=20) -> None:
    """Generates fake follow relationships"""
    admin_role = Role.query.filter_by(name='Administrator').first()
    admin = User.query.filter_by(role=admin_role).first()
    for i in range(count):
        user1 = User.query.get(randint(1, User.query.count()))
        user2 = User.query.get(randint(1, User.query.count()))
        if user1.role != admin_role and admin:
            user1.follow(admin)
        elif not admin and user1 != user2:
            user1.follow(user2)
