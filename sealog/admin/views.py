# -*- coding:utf-8 -*-
from flask import render_template, request, flash, url_for, current_app
from werkzeug.utils import redirect
from ..models import db, Feedback, User, Role
from ..decorators import admin_required
from .forms import EditProfileAdminForm
from . import admin_bp


@admin_bp.route('/')
@admin_required
def admin():
    return redirect(url_for('main.main'))


@admin_bp.route('/feedbacks/')
@admin_required
def manage_feedback():
    return render_template("admin/feedbacks.html")


@admin_bp.route('/feedbacks/delete/<int:id>', methods=['POST'])
@admin_required
def delete_feedback(id):
    feedback = Feedback.query.get(id)
    feedback.delete()
    flash(f"{str(feedback)} deleted.", "success")
    current_app.logger.info(f"Feedback id {id} deleted.")
    return redirect(url_for('admin.manage_feedback'))


@admin_bp.route('/users/')
@admin_required
def manage_users():
    page = request.args.get('page', default=1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    return render_template("admin/users.html", pagination=pagination)

@admin_bp.route('/users/<int:id>/edit-profile/', methods=['GET', 'POST'])
@admin_required
def edit_user_profile(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(f'{user.username}\'s profile has been updated.', 'info')
        return redirect(url_for('main.user_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/edit_user_profile.html', form=form, user=user)
