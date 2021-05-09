"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import input, output, abort
from flask import url_for, jsonify
from flask.views import MethodView
from .schemas import *
from flog.models import User, Post, Comment
from . import api_v3
from .decorators import can_edit_post, can_edit_profile


@api_v3.route("", endpoint="index")
class IndexAPI(MethodView):
    @output(IndexSchema)
    def get(self):
        """API Index"""
        return {
            "api_version": "3.0",
            "api_base_url": url_for("api_v3.index", _external=True)
        }


@api_v3.route("/user/<int:user_id>", endpoint="user")
class UserAPI(MethodView):
    @output(UserOutSchema)
    def get(self, user_id: int):
        """Return the schema of a certain user"""
        return User.query.get_or_404(user_id)

    @can_edit_profile
    @input(UserInSchema(partial=True))
    @output(UserOutSchema)
    def put(self, user_id: int, data):
        """Edit a user's profile if permitted"""
        user = User.query.get_or_404(user_id)
        for attr, value in data.items():
            if attr == "password":
                user.set_password(value)
            user.__setattr__(attr, value)
        return user

    @can_edit_profile
    @output(UserOutSchema)
    def patch(self, user_id: int):
        """Lock or unlock a user"""
        user = User.query.get_or_404(user_id)
        user.locked = not user.locked
        return user


@api_v3.route("/register", endpoint="register")
class RegistrationAPI(MethodView):
    @input(UserInSchema)
    @output(UserOutSchema)
    def post(self, data):
        """Register a new user"""
        user = User()
        for attr, value in data.items():
            if attr == "password":
                user.set_password(value)
            user.__setattr__(attr, value)
        return user


@api_v3.route("/token", endpoint="token")
class TokenAPI(MethodView):
    @input(TokenInSchema, location="form")
    @output(TokenOutSchema)
    def post(self, data):
        """Return the access token"""
        user = User.query.filter_by(username=data["username"]).first()
        if user is None or not user.verify_password(data["password"]):
            abort(400, message="Either the username or the password is invalid.")
        token = user.gen_api_auth_token()
        response = jsonify(
            {"access_token": token, "expires_in": 3600, "token_type": "Bearer"}
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


@api_v3.route("/post/<int:post_id>", endpoint="post")
class PostAPI(MethodView):
    @output(PostOutSchema)
    def get(self, post_id: int):
        return Post.query.get_or_404(post_id)

    @can_edit_post
    @input(PostInSchema)
    @output(PostOutSchema)
    def put(self, post_id: int, data: dict):
        post = Post.query.get_or_404(post_id)
        for attr, value in data.items():
            post.__setattr__(attr, value)
        return post


@api_v3.route("/comment/<int:comment_id>", endpoint="comment")
class CommentAPI(MethodView):
    @output(CommentOutSchema)
    def get(self, comment_id: int):
        return Comment.query.get_or_404(comment_id)
