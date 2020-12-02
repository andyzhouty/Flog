"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import abort, render_template, redirect, make_response, url_for, flash, request, current_app
from flask_login import current_user, login_required, login_user
from flask_babel import _
from itsdangerous import Serializer
from . import user_bp
from .forms import EditProfileForm, PasswordChangeForm, ValidateEmailForm
from ..models import db, User, Permission
from ..decorators import permission_required
from ..utils import redirect_back
from ..notifications import push_follow_notification
from ..emails import send_email


@user_bp.route('/profile/edit/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_administrator():
        return redirect(url_for('admin.edit_user_profile', id=current_user.id))
    if current_user.confirmed:
        form = EditProfileForm()
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.location = form.location.data
            current_user.about_me = form.about_me.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash(_('Your profile has been updated!'),  "success")
            return redirect(url_for('main.main'))
        form.name.data = current_user.name
        form.location.data = current_user.location
        form.about_me.data = current_user.about_me
        return render_template('user/edit_profile.html', form=form)
    flash(_("Your email has not been confirmed yet!"),  "warning")
    return redirect(url_for('main.main'))


@user_bp.route('/follow/<username>/', methods=['POST'])
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash(_('Already followed.'),  'info')
        return make_response(redirect_back())
    current_user.follow(user)
    if not current_app.testing:
        push_follow_notification(follower=current_user, receiver=user)
    flash(_('User followed.'),  'success')
    return make_response(redirect_back())


@user_bp.route('/unfollow/<username>/', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not current_user.is_following(user):
        flash(_('Not following yet.'),  'info')
        return make_response(redirect_back())
    current_user.unfollow(user)
    flash(_('User unfollowed.'),  'info')
    return make_response(redirect_back())


@user_bp.route('/user/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/user_profile.html', user=user)


@user_bp.route('/user/<username>/followers/')
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['USERS_PER_PAGE']
    )
    return render_template('user/followers.html', pagination=pagination, user=user)


@user_bp.route('/user/all/')
def all_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config['USERS_PER_PAGE']
    )
    return render_template('user/all_users.html', pagination=pagination)


@user_bp.route('/password/change/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        current_user.set_password(form.password)
        flash(_("Password Changed"))
        return redirect(url_for('user.user_profile', username=current_user.username))
    return render_template('user/change_password.html', form=form)


@user_bp.route('/password/forget/', methods=['GET', 'POST'])
def forget_password():
    form = ValidateEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not current_app.config['TESTING']:
            token = user.gen_auth_token()
            send_email([user.email], 'Reset Password', '/user/email/reset_password', user=user, token=token)
        flash(_("A confirmation email has been sent."))
        return redirect(url_for('user.forget_password'))
    return render_template('user/forget_password.html', form=form)


@user_bp.route('/password/reset/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_auth_token(token)
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        login_user(user)
        flash(_("Password Changed"))
        return redirect(url_for('main.main'))
    return render_template('user/change_password.html', form=form)
