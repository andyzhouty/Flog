from flask import current_app, make_response, jsonify
from flask_login import current_user
from ..models import db
from . import language_bp


@language_bp.route('/set-locale/<locale>')
def set_locale(locale):
    if locale not in current_app.config['LOCALES']:
        return jsonify(message='Invalid locale.'), 404
    response = make_response(jsonify(message='Settings updated.'))
    if current_user.is_authenticated:
        current_user.locale = locale
        db.session.add(current_user)
        db.session.commit()
    else:
        response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)
    return response
