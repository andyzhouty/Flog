# -*- coding:utf-8 -*-
from flask import (render_template, request, flash,
                   redirect, url_for, session, current_app)
from flask_login.utils import current_user
from ..models import db, Article, Feedback
from ..forms import AdminLoginForm, EditForm
from ..decorators import admin_required
from . import admin_bp


@admin_bp.before_request
def before_request():
    session.setdefault('admin', False)
    if 'Mozilla' not in request.user_agent.string and not current_app.config['TESTING']:
        return redirect(url_for('main.main'))


@admin_bp.route('/', methods=['GET', 'POST'])
@admin_bp.route('/articles/', methods=['GET', 'POST'])
@admin_required
def admin():
    return render_template(
        'admin/admin.html',
    )


@admin_bp.route('/articles/delete/<int:id>/', methods=['POST'])
@admin_required
def delete_article(id):
    """
    A view function for administrators to delete an articles.
    """
    article = Article.query_by_id(id)
    article.delete()
    flash(f"Article id {id} deleted", "success")
    current_app.logger.info(f"{str(article)} deleted.")
    return render_template("result.html", url=url_for("admin.admin"))


@admin_bp.route('/articles/edit/<int:id>')
@admin_required
def edit_article(id):
    form = EditForm()
    content = Article.query_by_id(id).content
    return render_template("admin/edit.html", id=id, form=form, old_content=content)


@admin_bp.route('/articles/edit_result/<int:id>', methods=['POST'])
@admin_required
def article_edit_result(id):
    article_content = request.form['ckeditor']
    id = id
    article = Article.query_by_id(id)
    article.content = article_content
    db.session.add(article)
    db.session.commit()
    flash("Edit Succeeded!")
    return render_template("result.html", url=url_for("admin.admin"))


@admin_bp.route('/feedbacks/')
@admin_required
def manage_feedback():
    return render_template("admin/feedbacks.html")


@admin_bp.route('/feedback/delete/<int:id>', methods=['POST'])
@admin_required
def delete_feedback(id):
    feedback = Feedback.query_by_id(id)
    feedback.delete()
    flash(f"{str(feedback)} deleted.", "success")
    current_app.logger.info(f"Feedback id {id} deleted.")
    return render_template("result.html", url=url_for("admin.manage_feedback"))
