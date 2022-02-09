"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

image_bp = Blueprint("image", __name__)

from . import views
