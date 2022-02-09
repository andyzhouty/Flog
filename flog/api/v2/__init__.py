"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint
from flask_cors import CORS

api_v2 = Blueprint("api_v2", __name__)
CORS(api_v2)

from . import views  # noqa
