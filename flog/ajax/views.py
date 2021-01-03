
"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import render_template, jsonify, request
from flask_login import current_user
from . import ajax_bp
from ..models import Notification, User, Group


@ajax_bp.route('/profile/<int:user_id>/')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('ajax/profile_popup.html', user=user)


@ajax_bp.route('/notification/count/')
def notification_count():
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 401
    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)


@ajax_bp.route('/group/hint/')
def get_group_hint():
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 401
    user_input = request.args.get('q')
    if user_input == '':
        return jsonify(hint=[])
    hint = [group.name for group in Group.query.whooshee_search(user_input).all()]
    return jsonify(hint=hint[:5])
