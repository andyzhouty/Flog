"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user, login_required
from .models import Group


def permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.locked:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
