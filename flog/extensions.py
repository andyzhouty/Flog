"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import request
from flask.globals import current_app
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_compress import Compress
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_moment import Moment
from flask_share import Share
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

babel = Babel()
bootstrap = Bootstrap()
ckeditor = CKEditor()
compress = Compress()
csrf = CSRFProtect()
db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['8640 per day', '720 per hour', '3 per second']
)
login_manager = LoginManager()
ma = Marshmallow()
mail = Mail()
migrate = Migrate()
moment = Moment()
share = Share()


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    admin = User.query.get(user_id)
    return admin


@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale
    locale = request.cookies.get("locale")
    if locale is not None:
        return locale
    return request.accept_languages.best_match(current_app.config["LOCALES"].keys())
