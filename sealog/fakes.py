"""
Generates fake data for development use.
"""
from random import randint as rint
from faker import Faker
from flask import current_app
import click
from .models import db, Article, Feedback, User, Role

fake = Faker('zh-CN')


def generate_fake_users(count: int=10) -> None:
    """Generates fake users."""
    for i in range(count):
        user = User(
            name=fake.name(),
            email=fake.email(),
        )
        user.set_password(fake.password())
        user.role = Role.query.filter_by(name='User').first()
        db.session.add(user)
    db.session.commit()
    if not current_app.config['TESTING']:
        click.echo(f"Generated {count} fake users.")


def generate_fake_articles(count: int=10) -> None:
    """Generates fake articles."""
    for i in range(count):
        article = Article(
            title=fake.sentence(),
            date=fake.date_time_this_year().strftime("%Y-%m-%d"),
            content=fake.text(200),
            timestamp=fake.date_time_this_year()
        )
        article.author = User.query.get(rint(1, len(User.query.all())))
        db.session.add(article)
    db.session.commit()
    if not current_app.config['TESTING']:
        click.echo(f"Generated {count} fake articles.")


def generate_fake_feedbacks(count: int=10) -> None:
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

