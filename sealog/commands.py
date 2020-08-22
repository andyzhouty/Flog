import os
import sys
import unittest
import logging
import click
from flask import Flask
from .models import Permission, User, Role

COVERAGE = None
if os.getenv('FLASK_COVERAGE', False):
    import coverage
    COVERAGE = coverage.coverage(branch=True, source='sealog')
    COVERAGE.start()


def register_commands(app: Flask, db): # noqa
    @app.cli.command()
    @click.option('--coverage/--no-coverage', default=False, help='Run tests with coverage')
    def test(coverage: bool) -> None:
        """Run the unit tests."""
        if os.getenv("FLASK_COVERAGE", False):
            os.environ['FLASK_COVERAGE'] = '1'
            os.execvp(sys.executable, [sys.executable] + sys.argv)
        logging.disable(logging.CRITICAL)  # disable log
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
        if COVERAGE:
            COVERAGE.stop()
            COVERAGE.save()
            print('Coverage Summary: ')
            COVERAGE.report()
            basedir = os.path.abspath(os.path.abspath(__file__))
            covdir = os.path.join(basedir, 'htmlcov')
            COVERAGE.html_report(directory=covdir)
            print(f'HTML Version: file://{covdir}/index.html')
            COVERAGE.erase()

    @app.cli.command()
    @click.option('--drop/--no-drop', default=False, help='Delete data.', prompt=True)
    def init_db(drop: bool) -> None:
        """Init database on a new development machine."""
        if drop:
            click.echo("Your data is deleted.")
            db.drop_all(app=app)
        db.create_all(app=app)
        Role.insert_roles()

    @app.cli.command()
    @click.option('--name')
    @click.option('--email')
    @click.option('--password')
    def create_admin(name, email, password):
        name = os.getenv('ADMIN_NAME', name)
        email = os.getenv('ADMIN_EMAIL', email)
        password = os.getenv('ADMIN_PASSWORD', password)
        if User.query.filter_by(email=email).count() == 0:
            admin = User(name=name, email=email)
            admin.set_password(password)
            admin.role.add_permission(Permission.ADMIN)
            db.session.add(admin)
            db.session.commit()
        else:
            click.echo("Exceeded the max number of admins: 1")

    @app.cli.command()
    @click.option('--users', default=10, help="Generates fake users")
    @click.option('--articles', default=10, help='Generates fake articles')
    @click.option('--feedbacks', default=10, help='Generates fake feedbacks')
    def forge(articles, feedbacks):
        """Generates fake data"""
        from . import fakes as f
        db.drop_all()
        db.create_all()
        f.generate_fake_users()
        f.generate_fake_articles(articles)
        f.generate_fake_feedbacks(feedbacks)
