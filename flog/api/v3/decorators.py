from apiflask import abort
from flask import g
from functools import wraps
from flog.models import User, Post
from .authentication import auth


def can_edit_profile(f):
    @wraps(f)
    @auth.login_required
    def decorator(*args, **kwargs):
        permitted = False
        if g.current_user is not None:
            if args[1] is not None:
                permitted = (g.current_user == User.query.get_or_404(args[1]))
            if g.current_user.is_administrator():
                permitted = True
        if not permitted:
            abort(403)
        return f(*args, **kwargs)

    return decorator


def can_edit_post(f):
    @wraps(f)
    @auth.login_required
    def decorator(*args, **kwargs):
        permitted = False
        if g.current_user is not None:
            if args[1] is not None:
                permitted = (Post.query.get_or_404(args[1]) in g.current_user.posts)
            if g.current_user.is_administrator():
                permitted = True
        if not permitted:
            abort(403)
        return f(*args, **kwargs)

    return decorator
