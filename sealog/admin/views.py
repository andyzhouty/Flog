# -*- coding:utf-8 -*-
from flask import render_template, request, flash, url_for, current_app
from werkzeug.utils import redirect
from ..models import db, Post, Feedback
from ..decorators import admin_required
from .forms import EditForm
from . import admin_bp


@admin_bp.route('/posts/delete/<int:id>/', methods=['POST'])
@admin_required
def delete_post(id):
    post = Post.query.get(id)
    post.delete()
    flash(f"Post id {id} deleted", "success")
    current_app.logger.info(f"{str(post)} deleted.")
    return redirect(url_for('main.main'))


@admin_bp.route('/posts/edit/<int:id>', methods=['POST', 'GET'])
@admin_required
def edit_post(id):
    form = EditForm()
    content = Post.query.get(id).content
    if form.validate_on_submit():
        post = Post.query.get(id)
        post.content = request.form.get('ckeditor')
        db.session.add(post)
        db.session.commit()
        flash("Edit Succeeded!", "success")
    return render_template("admin/edit.html", id=id, form=form, old_content=content)


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
