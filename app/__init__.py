from logging import log
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.logging import default_handler
from .extensions import (
    bootstrap, ckeditor, share, db, csrf, migrate, mail, moment, login_manager
)
from .models import Post, Feedback, Role, Permission, User
from .settings import config
from .errors import register_error_handlers
from .commands import register_commands
from .others import others_bp
from .feedback import feedback_bp
from .admin import admin_bp
from .auth import auth_bp
from .main import main_bp


def create_app(config_name=None) -> Flask:
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('flog')
    register_config(app, config_name)
    register_logger(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app, db)
    register_error_handlers(app)
    register_context(app)
    return app


def register_config(app: Flask, config_name: str):
    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


def register_logger(app: Flask):

    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s "
                                  "%(message)s")
    if app.config['DEBUG']:
        file_handler = RotatingFileHandler(
            filename="logs/flog.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    else:
        default_handler.setLevel(logging.INFO)
        app.logger.addHandler(default_handler)


def register_extensions(app: Flask) -> None:
    bootstrap.init_app(app)
    share.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(others_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")


def register_context(app: Flask) -> None:
    @app.shell_context_processor
    def make_shell_context():
        Role.insert_roles()
        return dict(
            db=db,
            Post=Post, Feedback=Feedback,
            Permission=Permission, Role=Role, User=User
        )

    @app.context_processor
    def make_template_context():
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
        return dict(
            posts=posts,
            feedbacks=feedbacks,
            Permission=Permission,
            current_app=app
        )
