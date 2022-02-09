"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

others_bp = Blueprint("others", __name__)

from . import views
