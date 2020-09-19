import click
from flask import Flask


def register_commands(app: Flask, db):
    @app.cli.command()
    def test() -> None:
        import logging
        import unittest
        """Run the unittests."""
        logging.disable(logging.CRITICAL)  # disable log
        tests = unittest.TestLoader().discover('tests') # use unittest to discover tests
        unittest.TextTestRunner(verbosity=2).run(tests) # run tests

    @app.cli.command()
    def create_admin():
        """Create administrator account"""
        from .models import Role, User
        admin_role = Role.query.filter_by(name='Administrator').first()
        username = app.config['ADMIN_NAME']
        email = app.config['ADMIN_EMAIL']
        password = app.config['ADMIN_PASSWORD']
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
    def forge(users, posts, feedbacks, follows):
        """Generates fake data"""
        from . import fakes as fake
        from .models import Role
        Role.insert_roles()
        fake.users(users)
        fake.posts(posts)
        fake.feedbacks(feedbacks)
        fake.follows(follows)

    def init_db(drop: bool=False) -> None:
        """Initialize database on a new machine."""
        if drop:
            db.drop_all(app=app)
        db.create_all(app=app)


    @app.cli.command()
    def deploy():
        """Run deployment tasks"""
        from .models import User, Role
        from flask_migrate import upgrade, stamp
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
