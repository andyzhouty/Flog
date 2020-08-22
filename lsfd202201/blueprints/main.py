# -*- coding:utf-8 -*-
from flask import render_template, Blueprint, current_app, abort, make_response
from ..utils import get_html_from, redirect_back

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
@main_bp.route('/main/')
def main():
    return render_template('main/main.html')


@main_bp.route('/members/')
def members():
    return render_template('main/members.html')


@main_bp.route('/video/')
def video():
    return render_template('main/video.html')


@main_bp.route("/about/")
@main_bp.route("/about/<any(en, zh):language>/")
def about(language="en"):
    if language == "en":
        zh = False
        html = get_html_from(
            "https://raw.githubusercontent.com/z-t-y/LSFD202201/master/README.md")
    else:
        zh = True
        html = get_html_from(
            "https://raw.githubusercontent.com/z-t-y/LSFD202201/master/README_zh.md")
    return render_template('main/about.html', content=html, zh=zh)


@main_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BOOTSTRAP_THEMES'].keys():
        abort(404)
    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30*24*60*60) # noqa
    return response


@main_bp.route('/kzkt/')
def kzkt():
    return render_template('main/kzkt.html')
