"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import Schema
from apiflask.fields import Integer, Boolean, String, URL, DateTime, Email, Nested, List
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


class CommentOutSchema(Schema):
    id = Integer()
    body = String()
    author = Nested(UserOutSchema)
    post = Nested(lambda: PostOutSchema(only=("id", "title", "author",)))
    self = ma.URLFor(".comment", values=dict(comment_id="<id>"))


class PostOutSchema(Schema):
    id = Integer()
    title = String()
    content = String()
    author = Nested(UserOutSchema)
    comments = List(Nested(CommentOutSchema, exclude=("post",)))
    self = ma.URLFor(".post", values=dict(post_id="<id>"))
