"""
Generates fake data for development use.
"""
from faker import Faker
import click
from .models import db, Article, Feedback

fake = Faker('zh-CN')


def generate_fake_articles(count: int) -> None:
    """Generates fake articles."""
    for i in range(count):
        article = Article(
            title=fake.sentence(),
            author=fake.name(),
            date=fake.date_time_this_year().strftime("%Y-%m-%d"),
            content=fake.text(200),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(article)
    db.session.commit()
    click.echo(f"Generated {count} fake articles.")


def generate_fake_feedback(count: int) -> None:
    """Generates fake feedback."""
    for i in range(count):
        feedback = Feedback(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(feedback)
    db.session.commit()
    click.echo(f"Generated {count} fake feedbacks.")
