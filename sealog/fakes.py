"""
Generates fake data for development use.
"""
from random import randint as rint
from faker import Faker
from flask import current_app
import click
from .models import db, Post, Feedback, User, Role
from .utils import slugify

fake = Faker()


def users(count: int=10) -> None:
    """Generates fake users."""
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
    if not current_app.config['TESTING']:
        click.echo(f"Generated {count} fake users.")


def posts(count: int=10) -> None:
    """Generates fake posts."""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            date=fake.date_time_this_year().strftime("%Y-%m-%d"),
            content=fake.text(1000),
            timestamp=fake.date_time_this_year()
        )
        post.author = User.query.get(rint(1, len(User.query.all())))
        db.session.add(post)
    db.session.commit()
    if not current_app.config['TESTING']:
        click.echo(f"Generated {count} fake posts.")


def feedbacks(count: int=10) -> None:
    """Generates fake feedback."""
    for i in range(count):
        feedback = Feedback(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(feedback)
    db.session.commit()
    if not current_app.config['TESTING']:
        click.echo(f"Generated {count} fake feedbacks.")
