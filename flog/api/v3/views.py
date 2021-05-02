"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from apiflask import output
from flask import url_for
from flask.views import MethodView
from .schemas import *
from flog.models import User
from . import api_v3


@api_v3.route("/", endpoint="index")
class IndexAPI(MethodView):
    @output(IndexSchema)
    def get(self):
        return {
            "api_version": "3.0",
            "api_base_url": url_for("api_v3.index", _external=True)
        }


@api_v3.route("/user/<int:user_id>/", endpoint="get_user")
class GetUserAPI(MethodView):
    @output(UserOutSchema)
    def get(self, user_id: int):
        return User.query.get_or_404(user_id)
