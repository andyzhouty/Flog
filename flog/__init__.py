"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from apiflask import APIFlask
from flask import Flask
from flask.logging import default_handler
from flask_login import current_user
from .extensions import (
    babel,
    bootstrap,
    ckeditor,
    compress,
    csrf,
    db,
    login_manager,
    ma,
    mail,
    migrate,
    moment,
    share,
)
from flask_babel import lazy_gettext as _l
from .models import Post, Feedback, Role, Permission, User, Notification, Message, Group
from .settings import config
from .errors import register_error_handlers
from .commands import register_commands
from .admin import admin_bp
from .ajax import ajax_bp
from .api.v1 import api_v1
from .api.v2 import api_v2
from .api.v3 import api_v3
from .auth import auth_bp
from .group import group_bp
from .feedback import feedback_bp
from .image import image_bp
from .language import language_bp
from .main import main_bp
from .notification import notification_bp
from .others import others_bp
from .testing import testing_bp
from .user import user_bp


def create_app(config_name=None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    app = APIFlask("flog")
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
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s " "%(message)s"
    )
    if app.debug or app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            filename="logs/flog.log", maxBytes=10 * 1024 * 1024, backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    else:
        default_handler.setLevel(logging.INFO)
        app.logger.addHandler(default_handler)


def register_extensions(app: Flask) -> None:
    babel.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)
    csrf.exempt(api_v2)
    csrf.exempt(api_v3)
    db.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = _l("Please log in to access this page")
    login_manager.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    share.init_app(app)


def register_blueprints(app: APIFlask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(others_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ajax_bp, url_prefix="/ajax")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_v1, url_prefix="/api/v1")
    app.register_blueprint(api_v2, url_prefix="/api/v2")
    app.register_blueprint(api_v3, url_prefix="/api/v3")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(group_bp, url_prefix="/group")
    app.register_blueprint(image_bp, url_prefix="/image")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")
    app.register_blueprint(language_bp, url_prefix="/language")
    app.register_blueprint(notification_bp, url_prefix="/notification")

    if app.testing:
        app.register_blueprint(testing_bp)


def register_context(app: Flask) -> None:
    @app.shell_context_processor
    def make_shell_context():
        Role.insert_roles()
        return dict(
            db=db,
            Post=Post,
            Feedback=Feedback,
            Permission=Permission,
            Role=Role,
            User=User,
            Message=Message,
            Group=Group,
        )

    @app.context_processor
    def make_template_context():
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
        allowed_tags = " ".join(app.config["FLOG_ALLOWED_TAGS"])
        if current_user.is_authenticated:
            notification_count = Notification.query.with_parent(current_user).count()
        else:
            notification_count = None
        return dict(
            posts=posts,
            feedbacks=feedbacks,
            Permission=Permission,
            current_app=app,
            notification_count=notification_count,
            allowed_tags=allowed_tags,
        )
