from flask import Blueprint

shop_bp = Blueprint('shop', __name__)

from . import views