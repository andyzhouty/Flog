from flask import jsonify
from flog.models import User
from .schemas import user_schema
from . import api_v1

@api_v1.route('/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify(user_schema(user))