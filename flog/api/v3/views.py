"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import input, output, abort
from flask import url_for, jsonify, g
from flask.views import MethodView
from .schemas import *
from flog.models import db, User, Post, Comment, Permission, Column
from flog.utils import clean_html
from . import api_v3
from .decorators import can_edit, permission_required
from ..api_utils import get_current_user


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


@api_v3.route("/user/<int:user_id>/posts", endpoint="user_posts")
class UserPostAPI(MethodView):
    @output(PostOutSchema(many=True))
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        permitted = (get_current_user() is not None and (
                get_current_user() == user or get_current_user().is_administrator()))
        return user.posts if permitted else [post for post in user.posts if not post.private]


@api_v3.route("/register", endpoint="register")
class RegistrationAPI(MethodView):
    @input(UserInSchema, location="form")
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
            {"access_token": token, "expires_in": "exactly a year", "token_type": "Bearer"}
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


@api_v3.route("/token/verify", endpoint="verify_token")
class VerifyTokenAPI(MethodView):
    @input(VerifyTokenInSchema, location="form")
    @output(VerifyTokenOutSchema)
    def post(self, data):
        """Verify an input token"""
        user = User.verify_auth_token_api(data["token"])
        if user is None:
            abort(401)
        schema = VerifyTokenOutSchema()
        schema.valid = True
        schema.username = user.username
        return schema


@api_v3.route("/post/<int:post_id>", endpoint="post")
class PostAPI(MethodView):
    @output(PostOutSchema)
    def get(self, post_id: int):
        post = Post.query.get_or_404(post_id)

        if post.private:
            user = get_current_user()
            if user:
                if user.is_administrator() or post in user.posts:
                    return post
            abort(403, "the post is private")
        return post

    @permission_required(Permission.WRITE)
    @can_edit("post")
    @input(PostInSchema(partial=True))
    @output(PostOutSchema)
    def put(self, post_id, data):
        post = Post.query.get(post_id)
        for attr, value in data.items():
            if attr == "content":
                post.content = clean_html(value)
            else:
                post.__setattr__(attr, value)
        db.session.commit()
        return post

    @permission_required(Permission.WRITE)
    @can_edit("post")
    @output({}, 204)
    def delete(self, post_id: int):
        post = Post.query.get(post_id)
        post.delete()


@api_v3.route("/post/add", endpoint="post_create")
class PostAddAPI(MethodView):
    @permission_required(Permission.WRITE)
    @input(PostInSchema)
    @output(PostOutSchema)
    def post(self, data):
        post = Post(author=g.current_user)
        for attr, value in data.items():
            if attr == "content":
                post.content = clean_html(value)
            elif attr == "column_ids":
                for column_id in data[attr]:
                    column = Column.query.get_or_404(column_id)
                    post.columns.append(column)
            else:
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
        comment = Comment.query.get(comment_id)
        for attr, value in data.items():
            if attr == "reply_id":
                comment.replied = Comment.query.get_or_404(value)
            elif attr == "post_id":
                post = Post.query.get_or_404(value)
                if post.private:
                    abort(400, "the post is private")
                comment.post = post
            elif attr == "body":
                comment.body = clean_html(value)
            else:
                comment.__setattr__(attr, value)
        db.session.commit()
        return comment

    @permission_required(Permission.COMMENT)
    @can_edit("comment")
    @output({}, 204)
    def delete(self, comment_id: int):
        comment = Comment.query.get(comment_id)
        comment.delete()


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
            elif attr == "post_id":
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
            elif attr == "body":
                comment.body = clean_html(value)
            else:
                comment.__setattr__(attr, value)
        db.session.add(comment)
        db.session.commit()
        return comment


@api_v3.route("/column/<int:column_id>", endpoint="column")
class ColumnAPI(MethodView):
    @output(ColumnOutSchema)
    def get(self, column_id):
        column = Column.query.get_or_404(column_id)
        return column

    @permission_required(Permission.WRITE)
    @can_edit("column")
    @input(ColumnInSchema(partial=True))
    @output(ColumnOutSchema)
    def put(self, column_id, data):
        column = Column.query.get(column_id)
        for attr, value in data.items():
            if attr == "post_ids":
                for post_id in data[attr]:
                    post = Post.query.get(post_id)
                    if post is None:
                        abort(404, f"post {post_id} not found")
                    column.posts.append(post)
            else:
                column.__setattr__(attr, value)
        db.session.commit()
        return column

    @permission_required(Permission.WRITE)
    @can_edit("column")
    @output({}, 204)
    def delete(self, column_id):
        column = Column.query.get(column_id)
        db.session.delete(column)
        db.session.commit()


@api_v3.route("/column/create", endpoint="add_column")
class ColumnAddAPI(MethodView):
    @permission_required(Permission.WRITE)
    @input(ColumnInSchema)
    @output(CommentOutSchema)
    def post(self, data):
        column = Column(author=g.current_user)
        for attr, value in data.items():
            if attr == "post_ids":
                for post_id in data[attr]:
                    post = Post.query.get(post_id)
                    if post is None:
                        abort(404, f"post {post_id} not found")
                    column.posts.append(post)
            else:
                column.__setattr__(attr, value)
        db.session.add(column)
        db.session.commit()
        return column
