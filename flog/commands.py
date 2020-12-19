"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import click
from flask import Flask


def register_commands(app: Flask, db):
    @app.cli.command()
    def test() -> None:
        """Run the unittests."""
        os.system('pytest -v')

    @app.cli.command()
    def create_admin():
        """Create administrator account"""
        from .models import Role, User
        admin_role = Role.query.filter_by(name='Administrator').first()
        username = app.config['FLOG_ADMIN']
        email = app.config['FLOG_ADMIN_EMAIL']
        password = app.config['FLOG_ADMIN_PASSWORD']
        if User.query.filter_by(email=email).count() == 0:
            admin = User(username=username, email=email, name=username, confirmed=True)
            admin.set_password(password)
            admin.role = admin_role
            db.session.add(admin)
            db.session.commit()
        else:
            click.echo("Either exceeded the max number of admins: 1 or the role is invalid")

    @app.cli.command()
    @click.option('--users', default=20, help="Generates fake users")
    @click.option('--posts', default=20, help='Generates fake posts')
    @click.option('--feedbacks', default=20, help='Generates fake feedbacks')
    @click.option('--follows', default=20, help='Generates fake follows')
    @click.option('--comments', default=20, help='Generates fake comments')
    @click.option('--notifications', default=5, help='Generates fake notifications')
    def forge(users, posts, feedbacks, follows, comments, notifications):
        """Generates fake data"""
        from . import fakes as fake
        from .models import Role
        Role.insert_roles()
        fake.users(users)
        fake.posts(posts)
        fake.comments(comments)
        fake.feedbacks(feedbacks)
        fake.follows(follows)
        fake.notifications(notifications)

    @app.cli.command()
    @click.option('--drop/--no-drop', help='Drop database or not')
    def init_db(drop: bool=False) -> None:
        """Initialize database on a new machine."""
        if drop:
            db.drop_all(app=app)
        db.create_all(app=app)


    @app.cli.command()
    def deploy():
        """Run deployment tasks"""
        from flask_migrate import upgrade, stamp
        try:
            # upgrade the database.
            upgrade()
        except:
            # I forgot to run `flask db migrate` at the beginning of the project,
            # so I have to init the database like this.
            db.create_all()
            stamp()
        from .models import User, Role
        # insert roles
        Role.insert_roles()
        # add self-follows
        for user in User.query.all():
            user.follow(user)


    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('Error: Extracting the config file failed.')
        if os.system(
            'pybabel init -i messages.pot -d flog`/translations -l ' + locale):
            raise RuntimeError(f'Error: Initing the new language {locale} failed.')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('Error: Extracting the config file failed.')
        if os.system('pybabel update -i messages.pot -d flog/translations'):
            raise RuntimeError('Error: Updating the .po file failed.')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages to .mo file."""
        if os.system('pybabel compile -d flog/translations'):
            raise RuntimeError('Error: Compiling failed.')
