from flask import Blueprint

language_bp = Blueprint('language', __name__)

from . import views
