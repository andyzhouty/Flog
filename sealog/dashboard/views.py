from flask import render_template, request
from flask_login import current_user
from ..models import db, Post
from .forms import PostForm
from . import dashboard_bp


@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard/dashboard.html')


@dashboard_bp.route('/write/', endpoint='write')
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            date=form.date.data,
            author=current_user.name,
            content=request.form.get('ckeditor')
        )
        db.session.add(post)
    return render_template('dashboard/new_post.html', form=form)
