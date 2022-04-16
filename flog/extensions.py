"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from djask.admin import Admin
from djask.extensions import login_manager, csrf, db
from flask import request
from flask.globals import current_app
from flask_babel import Babel
from flask_ckeditor import CKEditor
from flask_login import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_moment import Moment

admin_ext = Admin()
babel = Babel()
ckeditor = CKEditor()
limiter = Limiter(
    default_limits=["17280 per day", "1440 per hour"], key_func=get_remote_address
)
ma = Marshmallow()
mail = Mail()
migrate = Migrate()
moment = Moment()


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
