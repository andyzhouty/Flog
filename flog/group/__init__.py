"""
MIT License
Copyright (c) 2021 Andy Zhou
"""
from flask import Blueprint

group_bp = Blueprint("group", __name__)

from . import views
