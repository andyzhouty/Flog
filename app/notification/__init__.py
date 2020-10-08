from flask import Blueprint

notification_bp = Blueprint('notification', __name__)

from . import views
