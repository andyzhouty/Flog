"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import Blueprint

testing_bp = Blueprint("testing", __name__)

from . import views
