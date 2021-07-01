from apiflask import abort
from flask import g
from functools import wraps
from flog.models import User, Post, Comment, Column
from .authentication import auth


def can_edit(permission_type: str):
    def decorator(f):
        @wraps(f)
        @auth.login_required
        def decorated_function(*args, **kwargs):
            permitted = False
            if g.current_user is not None:
                if args[1] is not None:
                    permitted = check_permission(permission_type, args[1])
                if g.current_user.is_administrator():
                    permitted = True
            if not permitted:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_permission(permission_type: str, model_id: int) -> bool:
    permitted = False
    if permission_type == "profile":
        permitted = g.current_user == User.query.get_or_404(model_id)
    elif permission_type == "post":
        permitted = Post.query.get_or_404(model_id) in g.current_user.posts
    elif permission_type == "comment":
        permitted = Comment.query.get_or_404(model_id) in g.current_user.comments
    elif permission_type == "column":
        permitted = Column.query.get_or_404(model_id) in g.current_user.columns
    return permitted


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        @auth.login_required
        def decorated_function(*args, **kwargs):
            if (g.get("current_user") is None) or (not g.current_user.can(permission)):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
