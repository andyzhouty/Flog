"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import Blueprint

notification_bp = Blueprint("notification", __name__)

from . import views
