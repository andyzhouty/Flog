"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import (
    current_app,
    request,
    abort,
    url_for,
    redirect,
    render_template,
)
from flask_login import current_user
from . import others_bp
from ..utils import redirect_back


@others_bp.route("/change-theme/<theme_name>/")
def change_theme(theme_name):
    if theme_name not in current_app.config["BOOTSTRAP_THEMES"].keys():
        abort(404)
    response = redirect_back()
    response.set_cookie("theme", theme_name, max_age=30 * 24 * 60 * 60)  # noqa
    return response


@others_bp.route("/register/")
def register():
    return redirect(url_for("auth.register"))


@others_bp.route("/login/")
def login():
    return redirect(url_for("auth.login"))


@others_bp.route("/about/")
def about_us():
    try:
        if (
            request.cookies.get("locale") == "zh_Hans_CN"
            or current_user.locale == "zh_Hans_CN"
        ):
            return render_template("others/about_us_zh.html")
        else:
            return render_template("others/about_us_en.html")
    except AttributeError:  # exception on anonymous users
        return render_template("others/about_us_en.html")
