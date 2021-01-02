"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import abort, render_template, redirect, make_response, url_for, flash, request, current_app
from flask_login import current_user, login_required, login_user
from flask_babel import _
from . import user_bp
from .forms import EditProfileForm, GroupCreationForm, GroupFindForm, GroupInviteForm, PasswordChangeForm, ValidateEmailForm
from ..models import Group, db, User, Permission
from ..decorators import permission_required
from ..utils import redirect_back
from ..notifications import push_follow_notification, push_group_invite_notification, push_group_join_notification
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
        return redirect_back()
    current_user.follow(user)
    if not current_app.testing:
        push_follow_notification(follower=current_user, receiver=user)
    flash(_('User followed.'),  'success')
    return redirect_back()


@user_bp.route('/unfollow/<username>/', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not current_user.is_following(user):
        flash(_('Not following yet.'),  'info')
        return redirect_back()
    current_user.unfollow(user)
    flash(_('User unfollowed.'),  'info')
    return redirect_back()


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
    user_count = User.query.count()
    return render_template('user/all_users.html', pagination=pagination, user_count=user_count)


@user_bp.route('/password/change/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        flash(_("Password Changed"))
        return redirect(url_for('user.user_profile', username=current_user.username))
    return render_template('user/change_password.html', form=form)


@user_bp.route('/password/forget/', methods=['GET', 'POST'])
def forget_password():
    form = ValidateEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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


@user_bp.route('/group/create/', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupCreationForm()
    if form.validate_on_submit():
        group = Group(name=form.group_name.data)
        current_user.join_group(group)
        group.manager = current_user
        db.session.commit()
        flash(_("Created group {0}.".format(group.name)))
        return redirect_back()
    return render_template('user/create_group.html', form=form)


@user_bp.route('/group/find/', methods=['GET', 'POST'])
@login_required
def explore_group():
    form = GroupFindForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(name=form.group_name.data).first_or_404()
        push_group_join_notification(joiner=current_user, group=group, receiver=group.manager)
        flash(_("""We have sent a notification to the manager of the group.
                All you should do is to wait the manager's reply."""))
        return redirect_back()
    return render_template('user/explore_group.html', form=form)


@user_bp.route('/group/join/<token>/')
@login_required
def join_group(token):
    group = Group.verify_join_token(token)
    if group is None:
        abort(404)
    else:
        user_id = request.args.get('user_id', type=int)
        if user_id is None:
            user = current_user
        else:
            user = User.query.get(user_id)
        user.join_group(group)
        flash(_("Joined group {0}".format(group.name)))
        return redirect_back()


@user_bp.route('/group/invite/<int:user_id>/', methods=['GET', 'POST'])
@login_required
def invite_user(user_id: int):
    form = GroupInviteForm()
    form.group_id.choices = [
        (g.id, g.name)
        for g in Group.query.filter_by(manager=current_user).order_by('name')
    ]
    print(len(form.group_id.choices))
    if len(form.group_id.choices) == 0:
        flash(_("""
            You are not managing any groups.
            Please create a group first to invite other users.
        """))
        return redirect_back()
    if form.validate_on_submit():
        group = Group.query.get_or_404(form.group_id.data)
        invited_user = User.query.get_or_404(user_id)
        push_group_invite_notification(current_user, group, invited_user)
        flash(_("Notification sent to user {0}".format(invited_user.username)))
        return redirect_back()
    return render_template('user/group_invite.html', form=form)
