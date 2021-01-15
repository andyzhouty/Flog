"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

main_bp = Blueprint("main", __name__)

from . import views
