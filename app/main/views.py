from flask import (
    render_template, request, redirect, url_for, current_app, flash, abort,
    make_response
)
from flask_login import current_user
from flask_login.utils import login_required
from ..models import db, Post
from ..utils import redirect_back
from .forms import PostForm, EditForm
from . import main_bp


@main_bp.before_app_request
def before_app_request():
    ua = request.user_agent.string
    if 'spider' in ua or 'bot' in ua or 'python' in ua:
        return 'F**k you, web crawler!'

@main_bp.route('/')
def main():
    if not (current_user.is_authenticated or request.args.get('force', False)):
        return render_template('main/not_authorized.html')
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('main/main.html', pagination=pagination, posts=posts)



############################文章部分#################################
@main_bp.route('/write/', endpoint='write', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            date=form.date.data,
            content=form.content.data
        )
        post.author = current_user
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added', "success")
        return redirect(url_for('main.main'))
    return render_template('main/new_post.html', form=form)


@main_bp.route('/post/<slug>/')
@login_required
def full_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('main/full_post.html', post=post)


@main_bp.route('/manage-post')
@login_required
def manage_posts():
    page = request.args.get('page', 1, int)
    pagination = (Post.query.filter_by(author=current_user)
                            .order_by(Post.timestamp.desc())
                            .paginate(
                                page,
                                per_page=current_app.config['POSTS_PER_PAGE'],
                                error_out=False
                            ))
    return render_template('main/personal_posts.html', pagination=pagination)


@main_bp.route('/posts/delete/<int:id>/', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post.author):
        abort(403)
    post.delete()
    flash(f"Post id {id} deleted", "success")
    current_app.logger.info(f"{str(post)} deleted.")
    return redirect(url_for('main.main'))


@main_bp.route('/posts/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    post2edit = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post2edit.author):
        abort(403)
    form = EditForm()
    if form.validate_on_submit():
        editted_post = Post.query.get(id)
        editted_post.title = form.title.data
        editted_post.content = form.content.data
        editted_post.update_slug()
        db.session.add(editted_post)
        db.session.commit()
        flash("Edit Succeeded!", "success")
        return redirect(url_for('main.main'))
    if not current_app.config['TESTING']:
        form.title.data = post2edit.title
        form.content.data = post2edit.content
    return render_template("main/edit_post.html", id=id, form=form)


@main_bp.route('/collect-post/<int:id>/')
@login_required
def collect_post(id):
    post = Post.query.get(id)
    current_user.collect(post)
    print(current_user.collections)
    flash('Post collected.', 'success')
    return make_response(redirect_back())


@main_bp.route('/uncollect-post/<int:id>/')
@login_required
def uncollect_post(id):
    post = Post.query.get(id)
    current_user.uncollect(post)
    flash('Post uncollected.', 'info')
    return make_response(redirect_back())


@main_bp.route('/collected-posts/')
@login_required
def collected_posts():
    print(current_user.collections)
    posts = [post for post in Post.query.all() if current_user.is_collecting(post)]
    return render_template('main/collections.html', posts=posts)
