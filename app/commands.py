from app.user.views import follow
import os
import sys
import unittest
import logging
import click
from flask import Flask
from flask_migrate import upgrade, stamp
from .models import User, Role


def register_commands(app: Flask, db): # noqa
    @app.cli.command()
    def test() -> None:
        """Run the unittests."""
        logging.disable(logging.CRITICAL)  # disable log
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)


    @app.cli.command()
    @click.option('--name', default=os.getenv('ADMIN_NAME'), required=True)
    @click.option('--email', default=os.getenv('ADMIN_EMAIL'), required=True)
    @click.option('--password', default=os.getenv('ADMIN_PASSWORD'), required=True)
    @click.option('--role', required=True, prompt=True)
    def create_user(name, email, password, role):
        role = role.capitalize()
        if User.query.filter_by(email=email).count() == 0 and role == 'Admin':
            username = os.getenv('ADMIN_NAME', name)
            email = os.getenv('ADMIN_EMAIL', email)
            password = os.getenv('ADMIN_PASSWORD', password)
            admin = User(username=username, email=email, name=username, confirmed=True)
            admin.set_password(password)
            admin.role = Role.query.filter_by(name='Administrator').first()
            db.session.add(admin)
            db.session.commit()
        elif role == 'User' or role == 'Moderator':
            user = User(username=name, name=name, email=email, confirmed=True)
            user.set_password(password)
            user.role = Role.query.filter_by(name=role).first()
            db.session.add(user)
            db.session.commit()
        else:
            click.echo("Either exceeded the max number of admins: 1 or the role is invalid")

    @app.cli.command()
    @click.option('--users', default=20, help="Generates fake users")
    @click.option('--posts', default=20, help='Generates fake posts')
    @click.option('--feedbacks', default=20, help='Generates fake feedbacks')
    @click.option('--follows', default=20, help='Generates fake follows')
    def forge(users, posts, feedbacks, follows):
        """Generates fake data"""
        from . import fakes as fake
        Role.insert_roles()
        fake.users(users)
        fake.posts(posts)
        fake.feedbacks(feedbacks)
        fake.follows(follows)

    def init_db(drop: bool=False) -> None:
        """Init database on a new machine."""
        if drop:
            db.drop_all(app=app)
        db.create_all(app=app)


    @app.cli.command()
    def deploy():
        """Run deployment tasks"""
        from .models import Role
        try:
            # upgrade the database.
            upgrade()
        except:
            # I forgot to run `flask db migrate` at the beginning of the project,
            # so I have to init the database like this.
            init_db()
            stamp()
        # insert roles
        Role.insert_roles()
        # add self-follows
        for user in User.query.all():
            user.follow(user)
