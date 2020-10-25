"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import Blueprint

feedback_bp = Blueprint('feedback', __name__)

from . import views
