from apiflask import abort
from flask import g
from functools import wraps
from flog.models import User
from .authentication import auth


def can_edit_profile(f):
    @wraps(f)
    @auth.login_required
    def decorator(*args, **kwargs):
        permitted = False
        print(g.current_user)
        if g.current_user is not None:
            if args[1] is not None:
                permitted = (g.current_user == User.query.get(args[1]))
            if g.current_user.is_administrator():
                permitted = True
        if not permitted:
            abort(403)
        return f(*args, **kwargs)

    return decorator
