"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask.views import MethodView
from .authentication import auth

class UserAPI(MethodView):
    decorators = [auth.login_required]
