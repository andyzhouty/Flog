"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import Schema
from apiflask.fields import Integer, Boolean, String, URL, DateTime, Email
from marshmallow_sqlalchemy import SQLAlchemySchema


class IndexSchema(Schema):
    api_version = String(default="3.0")
    api_base_url = URL()


class UserOutSchema(SQLAlchemySchema):
    id = Integer()
    username = String()
    name = String()
    location = String()
    about_me = String()
    confirmed = Boolean()
    blocked = Boolean()
    member_since = DateTime()
    last_seen = DateTime()


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
