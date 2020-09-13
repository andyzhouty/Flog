from flask import render_template, redirect, make_response, url_for, flash, request
from flask.globals import current_app
from flask_login import current_user, login_required
from . import user_bp
from .forms import EditProfileForm
from ..models import db, User, Permission
from ..decorators import permission_required
from ..utils import redirect_back


@user_bp.route('/edit-profile/', methods=['GET', 'POST'])
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
            flash('Your profile has been updated!', "success")
            return redirect(url_for('main.main'))
        form.name.data = current_user.name
        form.location.data = current_user.location
        form.about_me.data = current_user.about_me
        return render_template('user/edit_profile.html', form=form)
    flash("Your email has not been confirmed yet!", "warning")
    return redirect(url_for('main.main'))


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash('Already followed.', 'info')
        return make_response(redirect_back())
    current_user.follow(user)
    flash('User followed', 'success')
    return make_response(redirect_back())


@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not current_user.is_following(user):
        flash('Not following yet.', 'info')
        return make_response(redirect_back())
    current_user.unfollow(user)
    flash('User unfollowed.', 'info')
    return make_response(redirect_back())


@user_bp.route('/user/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/user_profile.html', user=user)


@user_bp.route('/<username>/followers')
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['USERS_PER_PAGE']
    )
    return render_template('user/followers.html', pagination=pagination, user=user)
