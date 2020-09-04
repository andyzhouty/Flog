from flask import Blueprint

others_bp = Blueprint('others', __name__)

from . import views