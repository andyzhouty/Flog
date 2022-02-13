"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import url_for, flash, redirect, request, render_template, abort
from flask.globals import current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from . import auth_bp
from .forms import DeleteAccountForm, LoginForm, RegisterationForm
from ..models import User, db
from ..emails import send_email
import os


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.main"))
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            name=form.name.data,
            username=form.username.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            [user.email],
            "Confirm your account",
            "auth/email/confirm",
            user=user,
            token=token,
        )
        flash(
            _("A confirmation email has been sent to you by email! You can now login!"),
            "blue",
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next")
    if next_url is None or next_url.startswith("/"):
        next_url = url_for("main.main")
    if current_user.is_authenticated:
        return redirect(next_url)
    if request.method == "POST":
        user_by_username = User.query.filter_by(
            username=request.form["user"]
        ).first()
        user_by_email = User.query.filter_by(
            email=request.form["user"].lower()
        ).first()
        user = user_by_username or user_by_email
        if user is not None:
            if user.verify_password(
                request.form["password"]
            ):
                login_user(user, True)
                return redirect(next_url)
            flash(_("Invalid username or password!"), "red")
        flash(_("Invalid username or password!"), "red")
    return render_template("auth/login.html")


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash(_("You have been logged out."), "blue")
    return redirect(url_for("main.main"))


@auth_bp.route("/confirm/<token>/")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.main"))
    if current_user.confirm(token):
        db.session.commit()
        flash(_("You have confirmed your account. Thanks !"), "green")
    else:
        flash(_("The confirmation link is invalid or has expired"), "yellow")
    return redirect(url_for("main.main"))


@auth_bp.route("/confirm/resend/")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        [current_user.email],
        "Confirm Your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash(_("A new confirmation email has been sent to you by email"), "blue")
    return redirect(url_for("main.main"))


@auth_bp.route("/account/delete/", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            username = current_user.username
            current_user.delete()
            current_app.logger.info(f"User {username} deleted.")
            flash(_("Your account has been deleted"), "blue")
        else:
            flash(_("Your password is invalid!"), "yellow")
        return redirect(url_for("main.main"))
    return render_template("auth/delete_account.html", form=form)
