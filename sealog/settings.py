# flake8: noqa
import os
from werkzeug.security import generate_password_hash


def generate_sqlite_file(str: str):
    basedir = os.path.abspath(os.path.dirname(__file__))
    return 'sqlite:///' + os.path.join(basedir, f'{str}.sqlite3')


class Base:
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("SEALOG_EMAIL")
    MAIL_PASSWORD = os.getenv("SEALOG_EMAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("DEFAULT_EMAIL_SENDER")

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ADMIN_EMAIL_LIST = [ADMIN_EMAIL]

    # ('theme name': 'display name')
    BOOTSTRAP_THEMES = {'default': 'Default', 'ubuntu': 'Ubuntu',
                       'lite': 'Lite', 'dark': 'Dark'}

    CKEDITOR_SERVE_LOCAL = True

    POSTS_PER_PAGE = 8

class Production(Base):
    FLASK_CONFIG = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", generate_sqlite_file('data'))


class Development(Base):
    FLASK_CONFIG = 'development'
    SQLALCHEMY_DATABASE_URI = generate_sqlite_file('data-dev')
    DEBUG = True
    MAIL_SUPPRESS_SEND = True
    ADMIN_EMAIL_LIST = [os.getenv("ADMIN_TWO_EMAIL")]


class Test(Base):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MAIL_DEFAULT_SENDER = os.getenv("DEFAULT_EMAIL_SENDER")
    ADMIN_EMAIL_LIST = [os.getenv("ADMIN_TWO_EMAIL")]


config = {
    'production': Production,
    'development': Development,
    'testing': Test
}
