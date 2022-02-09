"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import Blueprint

user_bp = Blueprint("user", __name__)

from . import views
