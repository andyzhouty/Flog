"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import input, output, abort, doc
from flask import url_for, jsonify, g, request
from flask.views import MethodView
from .schemas import *
from flog.models import db, User, Post, Comment, Permission
from . import api_v3
from .decorators import can_edit, permission_required


@api_v3.route("", endpoint="index")
class IndexAPI(MethodView):
    @output(IndexSchema)
    def get(self):
        """API Index"""
        return {
            "api_version": "3.0",
            "api_base_url": url_for("api_v3.index", _external=True),
        }


@api_v3.route("/user/<int:user_id>", endpoint="user")
class UserAPI(MethodView):
    @output(UserOutSchema)
    def get(self, user_id: int):
        """Return the schema of a certain user"""
        return User.query.get_or_404(user_id)

    @can_edit("profile")
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

    @can_edit("profile")
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
        post = Post.query.get_or_404(post_id)

        if post.private:
            auth = request.headers.get("Authorization")
            if auth:
                if not auth.startswith("Bearer"):
                    abort(403, "the post is private")
                token = auth[7:]
                user = User.verify_auth_token_api(token)
                if user:
                    if user.is_administrator() or post in user.posts:
                        return post
            abort(403, "the post is private")
        return post

    @can_edit("post")
    @input(PostInSchema(partial=True))
    @output(PostOutSchema)
    def put(self, post_id, data):
        post = Post.query.get_or_404(post_id)
        for attr, value in data.items():
            post.__setattr__(attr, value)
        db.session.commit()
        return post


@api_v3.route("/post/add", endpoint="post_create")
class PostAddAPI(MethodView):
    @permission_required(Permission.WRITE)
    @input(PostInSchema)
    @output(PostOutSchema)
    def post(self, data):
        post = Post(author=g.current_user)
        for attr, value in data.items():
            post.__setattr__(attr, value)
        db.session.add(post)
        db.session.commit()
        return post


@api_v3.route("/comment/<int:comment_id>", endpoint="comment")
class CommentAPI(MethodView):
    @output(CommentOutSchema)
    def get(self, comment_id: int):
        return Comment.query.get_or_404(comment_id)

    @permission_required(Permission.COMMENT)
    @can_edit("comment")
    @input(CommentInSchema(partial=True))
    @output(CommentOutSchema)
    def put(self, comment_id: int, data):
        comment = Comment.query.get_or_404(comment_id)
        for attr, value in data.items():
            if attr == "reply_id":
                comment.replied = Comment.query.get_or_404(value)
            if attr == "post_id":
                post = Post.query.get_or_404(value)
                if post.private:
                    abort(400, "the post is private")
                comment.post = post
            comment.__setattr__(attr, value)
        db.session.commit()
        return comment


@api_v3.route("/comment/add", endpoint="add_comment")
class CommentAddAPI(MethodView):
    @permission_required(Permission.COMMENT)
    @input(CommentInSchema)
    @output(CommentOutSchema)
    def post(self, data):
        comment = Comment(author=g.current_user)
        for attr, value in data.items():
            if attr == "reply_id":
                comment.replied = Comment.query.get_or_404(value)
            if attr == "post_id":
                post = Post.query.get_or_404(value)
                if post.private:
                    abort(400, "the post is private")
                comment.post = post
                comment.replied = Comment.query.get_or_404(data["reply_id"])
                if comment.replied not in comment.post.comments:
                    abort(
                        400,
                        "the comment you want to reply does not belongs to the post",
                    )
            comment.__setattr__(attr, value)
        db.session.add(comment)
        return comment