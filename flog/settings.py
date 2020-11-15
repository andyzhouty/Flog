"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
from flask_babel import lazy_gettext as _l


def generate_sqlite_filename(filename: str):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return 'sqlite:///' + os.path.join(basedir, f'{filename}.sqlite3')


class Base:
    DEBUG = False
    TESTING = False
    SSL_REDIRECT = False

    SECRET_KEY = os.getenv('SECRET_KEY', 'hard-to-guess')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("FLOG_EMAIL", "flog_admin@example.com")
    MAIL_PASSWORD = os.getenv("FLOG_EMAIL_PASSWORD", "flog_email_password")
    MAIL_DEFAULT_SENDER = os.getenv("DEFAULT_EMAIL_SENDER", "flog <flog_admin@example.com")

    FLOG_ADMIN = os.getenv('FLOG_ADMIN', 'flog_admin')
    FLOG_ADMIN_EMAIL = os.getenv('FLOG_ADMIN_EMAIL', MAIL_USERNAME)
    FLOG_ADMIN_PASSWORD = os.getenv('FLOG_ADMIN_PASSWORD', 'flog_admin_password')

    # ('theme name': 'display name')
    BOOTSTRAP_THEMES = {'default': _l('Default'), 'lite': _l('Lite'), 'dark': _l('Dark')}

    POSTS_PER_PAGE = 8
    USERS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10
    NOTIFICATIONS_PER_PAGE = 10

    LOCALES = {
        'en_US': 'English(US)',
        'zh_Hans_CN': '简体中文'
    }

    CKEDITOR_HEIGHT = 800

    @classmethod
    def init_app(cls, app):
        pass


class Production(Base):
    FLASK_CONFIG = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", generate_sqlite_filename('data'))
    # Specially configured for pythonanywhere
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}

    @classmethod
    def init_app(cls, app):
        Base.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'ADMIN_EMAIL', None) is not None:
            credentials = (cls.FLOG_ADMIN_EMAIL, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_DEFAULT_SENDER,
            toaddrs=[cls.FLOG_ADMIN_EMAIL],
            subject='Application Error',
            credentials=credentials, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class Development(Base):
    FLASK_CONFIG = 'development'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_DEV', generate_sqlite_filename('data-dev'))
    DEBUG = True
    MAIL_SUPPRESS_SEND = False


class Test(Base):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'production': Production,
    'development': Development,
    'testing': Test,
}
