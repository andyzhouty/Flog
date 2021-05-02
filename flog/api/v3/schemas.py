"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import Schema
from apiflask.fields import Integer, Boolean, String, URL, DateTime


class IndexSchema(Schema):
    api_version = String(default="3.0")
    api_base_url = URL()


class UserOutSchema(Schema):
    id = Integer()
    username = String()
    location = String()
    about_me = String()
    confirmed = Boolean()
    member_since = DateTime()
    last_seen = DateTime()
