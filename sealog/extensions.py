import os
from flask_bootstrap import Bootstrap
from flask_share import Share
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager

bootstrap = Bootstrap()
share = Share()
db = SQLAlchemy()
csrf = CSRFProtect()
ckeditor = CKEditor()
migrate = Migrate()
mail = Mail()
moment = Moment()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    admin = User.query.get(user_id)
    print('Here # load_user')
    return admin
