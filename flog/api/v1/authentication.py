from flask_httpauth import HTTPBasicAuth
from flask import g
from flog.models import User
from .errors import unauthorized
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password_or_token(username_or_token, password):
    if username_or_token == '':
        return False
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        user = User.verify_auth_token()
        g.current_user = user
        return bool(user)
    g.current_user = user
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')
