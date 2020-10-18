"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import current_app, abort, make_response, url_for, redirect
from flask.globals import request
from flask.templating import render_template, render_template_string
from . import others_bp
from ..utils import redirect_back


@others_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BOOTSTRAP_THEMES'].keys():
        abort(404)
    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30*24*60*60) # noqa
    return response


@others_bp.route('/register/')
def register():
    return redirect(url_for('auth.register'))


@others_bp.route('/login/')
def login():
    return redirect(url_for('auth.login'))

@others_bp.route('/about-us')
def about_us():
    return render_template('others/about_us.html')
