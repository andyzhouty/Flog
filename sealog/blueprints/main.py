# -*- coding:utf-8 -*-
from flask import render_template, Blueprint, current_app, abort, make_response, url_for, redirect
from ..utils import redirect_back

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
@main_bp.route('/main/')
def main():
    return render_template('main/main.html')


@main_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BOOTSTRAP_THEMES'].keys():
        abort(404)
    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30*24*60*60) # noqa
    return response


@main_bp.route('/register/')
def register():
    return redirect(url_for('auth.register'))


@main_bp.route('/login/')
def login():
    return redirect(url_for('auth.login'))
