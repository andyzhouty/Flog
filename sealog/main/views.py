from flask import render_template, request, redirect, url_for, current_app
from flask_login import current_user
from flask_login.utils import login_required
from ..models import db, Post
from .forms import PostForm
from . import main_bp


@main_bp.route('/')
def main():
    if not current_user.is_authenticated:
        return render_template('main/not_authorized.html')
    page = request.args.get('page', 1 ,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('main/main.html', pagination=pagination, posts=posts)


@main_bp.route('/write/', endpoint='write')
@login_required
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
    return render_template('main/new_post.html', form=form)


@main_bp.route('/post/<slug>')
@login_required
def full_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('main/full_post.html', post=post)