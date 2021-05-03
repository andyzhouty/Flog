"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import g
from apiflask import HTTPTokenAuth
from flog.models import User

auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token: str):
    user = User.verify_auth_token_api(token)
    if user:
        g.current_user = user
        return user
    return None
