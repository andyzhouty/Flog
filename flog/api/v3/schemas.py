"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import Schema
from apiflask.fields import (
    Integer,
    Boolean,
    String,
    URL,
    DateTime,
    Email,
    Nested,
    List,
    Raw,
)
from flog.extensions import ma


class IndexSchema(Schema):
    api_version = String(default="3.0")
    api_base_url = URL()


class UserOutSchema(Schema):
    id = Integer()
    username = String()
    name = String()
    location = String()
    about_me = String()
    confirmed = Boolean()
    blocked = Boolean()
    member_since = DateTime()
    last_seen = DateTime()
    self = ma.URLFor(".user", values=dict(user_id="<id>"))


class UserInSchema(Schema):
    username = String(required=True)
    email = Email(required=True)
    password = String(required=True)
    name = String()
    location = String()
    about_me = String()


class TokenInSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenOutSchema(Schema):
    access_token = String()
    expires_in = Integer()
    token_type = String()


class VerifyTokenInSchema(Schema):
    token = String(required=True)


class VerifyTokenOutSchema(Schema):
    username = String()
    valid = Boolean()


class CommentInSchema(Schema):
    body = String(required=True)
    post_id = Integer(required=True)
    reply_id = Integer()


class CommentOutSchema(Schema):
    id = Integer()
    body = String()
    author = Nested(UserOutSchema)
    post = Nested(
        lambda: PostOutSchema(
            only=(
                "id",
                "title",
                "self",
            )
        )
    )
    replying = Nested(lambda: CommentOutSchema(exclude=("replying",)))
    self = ma.URLFor(".comment", values=dict(comment_id="<id>"))


class ColumnInSchema(Schema):
    name = String()
    post_ids = List(Integer())


class ColumnOutSchema(Schema):
    id = Integer()
    name = String()
    author = Nested(UserOutSchema)
    posts = List(Nested(lambda: PostOutSchema(only=("id", "title", "self"))))
    self = ma.URLFor(".column", values=dict(column_id="<id>"))


class PostInSchema(Schema):
    title = String(required=True)
    content = String(required=True)
    private = Boolean(default=False)
    column_ids = List(Integer())


class PostOutSchema(Schema):
    id = Integer()
    title = String()
    content = String()
    private = Boolean()
    author = Nested(UserOutSchema)
    comments = List(Nested(CommentOutSchema, exclude=("post",)))
    columns = List(Nested(ColumnOutSchema, exclude=("posts", "author")))
    self = ma.URLFor(".post", values=dict(post_id="<id>"))


class ImageInSchema(Schema):
    upload = Raw(type="file", required=True)


class ImageOutSchema(Schema):
    id = Integer()
    filename = String()
    image_url = URL()
