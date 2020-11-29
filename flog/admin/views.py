"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import render_template, request, flash, url_for, current_app, make_response
from werkzeug.utils import redirect
from flask_babel import _
from ..models import db, Feedback, User, Role
from ..decorators import admin_required
from ..utils import redirect_back
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
    feedback_str = str(feedback)
    flash(_("%s deleted." % feedback_str),  "success")
    current_app.logger.info(f"Feedback id {id} deleted.")
    return redirect(url_for('admin.manage_feedback'))


@admin_bp.route('/users/')
@admin_required
def manage_users():
    page = request.args.get('page', default=1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config['USERS_PER_PAGE'], error_out=False
    )
    return render_template("user/all_users.html", pagination=pagination)


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
        flash(_('%s\'s profile has been updated.' % user.username),  'info')
        return redirect(url_for('user.user_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/edit_user_profile.html', form=form, user=user)


@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user_account(id):
    User.query.get(id).delete()
    flash(_('User Deleted'),  'info')
    return make_response(redirect_back())
