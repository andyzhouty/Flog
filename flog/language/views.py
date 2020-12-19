"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import current_app, make_response, abort, flash
from flask_login import current_user
from flask_babel import _
from ..models import db
from ..utils import redirect_back
from . import language_bp


@language_bp.route('/set-locale/<locale>/')
def set_locale(locale):
    if locale not in current_app.config['LOCALES'].keys():
        abort(404)
    response = make_response(redirect_back())
    if current_user.is_authenticated:
        current_user.locale = locale
        db.session.add(current_user)
        db.session.commit()
    else:
        response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)
    flash(_('Language updated.'))
    return response
