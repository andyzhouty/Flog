"""
    flog.api.v1.resources
    ~~~~~~~~~~~~~~~~~~~~~
    This module contains functions and APIs of this website.

    :copyright: Andy Zhou
    :license: MIT License
"""

from flask import g, jsonify, request, url_for
from flask.views import MethodView
from .errors import (  # noqa
    ValidationError,
    bad_request,
    unauthorized,
    forbidden
)
from .authentication import auth
from .schemas import user_schema, post_schema
from flog.models import db, User, Post


def get_post_data() -> tuple:
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if (content is None or str(content).strip() == '' or
            title is None or str(title).strip() == ''):
        raise ValidationError('The post content is invalid or empty.')
    return (title, content)


def can_edit_post(post: Post) -> bool:
    try:
        return (g.current_user == post.author or
                g.current_user.is_administrator())
    except:  # noqa
        return False


def can_edit_profile(user: User) -> bool:
    try:
        return (g.current_user == user or
                g.current_user.is_administrator())
    except:  # noqa
        return False


class IndexAPI(MethodView):
    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": url_for('api_v1.index', _external=True),
        })


class UserAPI(MethodView):
    """API for user operations"""
    decorators = [auth.login_required]

    def get(self, user_id: int):
        """Get User"""
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema(user))

    def put(self, user_id: int):
        """Change user profile"""
        user = User.query.get_or_404(user_id)
        if not can_edit_profile(user):
            return forbidden('You cannot edit this user\'s profile.')
        user.username = request.json.get('username', user.username)
        user.name = request.json.get('name', user.name)
        user.location = request.json.get('location', user.location)
        user.about_me = request.json.get('about_me', user.about_me)
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema(user))

    def delete(self, user_id: int):
        """Delete user"""
        user = User.query.get_or_404(user_id)
        if not can_edit_profile(user):
            return forbidden('You cannot delete this user.')
        user.delete()
        return f'User id {user_id} deleted.', 200


class PostAPI(MethodView):
    """API for post operations"""
    decorators = [auth.login_required]

    def get(self, post_id):
        """Get Post"""
        post = Post.query.get_or_404(post_id)
        return jsonify(post_schema(post))

    def put(self, post_id):
        """Edit Post"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden('You cannot edit this post.')
        post_data = get_post_data()
        post.title = post_data[0]
        post.content = post_data[1]
        db.session.add(post)
        db.session.commit()
        return '', 204

    def patch(self, post_id):
        """Toggle Post Visiblity"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden('You cannot change this post\'s visiblity.')
        post.private = not post.private
        db.session.add(post)
        db.session.commit()
        return '', 204

    def delete(self, post_id):
        """Delete Post"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden('You cannot delete this post.')
        post.delete()
        return '', 204
