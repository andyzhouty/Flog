"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

ajax_bp = Blueprint("ajax", __name__)

from . import views
