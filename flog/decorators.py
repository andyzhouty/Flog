"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user, login_required
from .models import Permission, Group


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def group_login_required(f):
    @login_required
    @wraps(f)
    def decorator(*args, **kwargs):
        if not isinstance(current_user, Group):
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return decorator
