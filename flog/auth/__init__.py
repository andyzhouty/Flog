"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from . import views
