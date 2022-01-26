"""
MIT License
Copyright (c) 2021 Andy Zhou
"""
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required, login_user
from flask_babel import _
from sqlalchemy import and_

from . import user_bp
from .forms import (
    EditProfileForm,
    PasswordChangeForm,
    ValidateEmailForm,
)
from ..models import db, User, Post
from ..decorators import permission_required
from ..utils import redirect_back
from ..notifications import (
    push_follow_notification,
)
from ..emails import send_email


@user_bp.route("/profile/edit/", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.is_administrator():
        return redirect(url_for("admin.edit_profile", id=current_user.id))
    form = EditProfileForm()
    if form.validate_on_submit():
        post_desc = Post.query.filter_by(title=current_user.username)
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.custom_avatar_url = form.custom_avatar_url.data
        post_desc.title = form.username.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash(_("Your profile has been updated!"), "success")
        return redirect(url_for("main.main"))
    form.username.data = current_user.username
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.custom_avatar_url.data = current_user.custom_avatar_url
    return render_template("user/edit_profile.html", form=form)


@user_bp.route("/follow/<username>/", methods=["POST"])
@login_required
@permission_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash(_("Already followed."), "info")
        return redirect_back()
    current_user.follow(user)
    push_follow_notification(follower=current_user, receiver=user)
    flash(_("User followed."), "success")
    return redirect_back()


@user_bp.route("/unfollow/<username>/", methods=["POST"])
@login_required
@permission_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not current_user.is_following(user):
        flash(_("Not following yet."), "info")
        return redirect_back()
    current_user.unfollow(user)
    flash(_("User unfollowed."), "info")
    return redirect_back()


@user_bp.route("/user/<username>/")
def profile(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    if current_user and (current_user == user or current_user.is_administrator()):
        posts = Post.query.filter(
            and_(Post.author == user, Post.title != user.username)
        )
    posts = Post.query.filter(
        and_(Post.author == user, ~Post.private, Post.title != user.username)
    )
    post_pagination = posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    description = Post.query.filter(
        and_(Post.author == user, Post.title == user.username)
    )
    user.clicks += 1
    user.clicks_today += 1
    db.session.commit()
    return render_template(
        "user/user_profile.html",
        user=user,
        posts=posts.all(),
        post_pagination=post_pagination,
        description=description.first(),
    )


@user_bp.route("/user/<username>/followers/")
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config["USERS_PER_PAGE"]
    )
    return render_template("user/followers.html", pagination=pagination, user=user)


@user_bp.route("/user/all/")
def all():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config["USERS_PER_PAGE"]
    )
    user_count = User.query.count()
    return render_template(
        "user/all.html", pagination=pagination, user_count=user_count
    )


@user_bp.route("/password/change/", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash(_("Password Changed"))
        return redirect(url_for("user.profile", username=current_user.username))
    return render_template("user/change_password.html", form=form)


@user_bp.route("/password/forget/", methods=["GET", "POST"])
def forget_password():
    form = ValidateEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(
            [user.email],
            "Reset Password",
            "/user/email/reset_password",
            user=user,
            token=token,
        )
        flash(_("A confirmation email has been sent."))
        return redirect(url_for("user.forget_password"))
    return render_template("user/forget_password.html", form=form)


@user_bp.route("/password/reset/<token>/", methods=["GET", "POST"])
def reset_password(token):
    user = User.from_confirmation_token(token)
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        login_user(user)
        flash(_("Password Changed"))
        return redirect(url_for("main.main"))
    return render_template("user/change_password.html", form=form)


@user_bp.route("/groups/")
def groups():
    return render_template("user/groups.html", groups=current_user.groups)
