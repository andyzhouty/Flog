"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user, login_required


def permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.locked:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
