"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import Blueprint

image_bp = Blueprint("image", __name__)

from . import views
