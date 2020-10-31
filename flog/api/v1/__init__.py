"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__)
CORS(api_v1)

from . import views # noqa
