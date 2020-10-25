"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import current_app, request, abort, make_response, url_for, redirect, render_template
from flask_login import current_user
from . import others_bp
from ..utils import redirect_back, get_markdown, convert_to_html


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
    try:
        if request.cookies.get('locale') == 'zh_Hans_CN' or current_user.locale == "zh_Hans_CN":
            markdown = get_markdown('https://gitee.com/andyzhouty/flog/raw/master/README_zh.md')
        else:
            markdown = get_markdown('https://gitee.com/andyzhouty/flog/raw/master/README.md')
    except AttributeError: # exception on anonymous users
        markdown = get_markdown('https://gitee.com/andyzhouty/raw/master/README.md')
    html = convert_to_html(markdown)
    return render_template('others/about_us.html', content=html)
