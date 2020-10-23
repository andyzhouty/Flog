"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import (
    render_template, redirect, url_for, flash, abort, make_response,
    request, current_app
)
from flask.signals import message_flashed
from flask_babel import _
from flask_login import current_user, login_required
from ..models import db, Post, Comment
from ..utils import redirect_back
from ..notifications import push_collect_notification, push_comment_notification
from .forms import PostForm, EditForm, CommentForm
from . import main_bp


@main_bp.before_app_request
def before_app_request():
    ua = request.user_agent.string
    if 'spider' in ua or 'bot' in ua or 'python' in ua:
        return 'F**k you, spider!' # anti-webcrawler :P


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


####################### Post Part ##################################
@main_bp.route('/write/', endpoint='write', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Add a post to the database.
        post = Post(
            author=current_user,
            title=form.title.data,
            content=form.content.data,
            private=form.private.data
        )
        db.session.add(post)
        db.session.commit()
        flash(_('Your post has been added'),  "success")
        return redirect(url_for('main.main'))
    return render_template('main/new_post.html', form=form)


@main_bp.route('/post/<slug>/', methods=['GET', 'POST'])
@login_required
def full_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not post.private:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENTS_PER_PAGE']
        pagination = (Comment.query.with_parent(post)
                                .order_by(Comment.timestamp.asc())
                                .paginate(page, per_page))
        comments = pagination.items
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(
                author=current_user,
                post=post,
                body=form.body.data,
            )
            replied_id = request.args.get('reply')
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
            db.session.add(comment)
            db.session.commit()
            push_comment_notification(comment=comment, receiver=post.author)
            flash(_('Comment published!'),  'success')
            return make_response(redirect_back())
        return render_template('main/full_post.html', post=post, pagination=pagination,
                            comments=comments, form=form)
    else:
        flash(_('The author has set this post to invisible.'))
        make_response(redirect_back())


@main_bp.route('/reply/comment/<int:comment_id>')
@login_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('main.full_post', slug=comment.post.slug, reply=comment_id,
                            author=comment.author.name) + '#comment-form')


@main_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.delete()
    return make_response(redirect_back())


@main_bp.route('/manage-post')
@login_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    pagination = (
        Post.query.filter_by(author=current_user)
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
    flash(_("Post id %d deleted" % id),  "success")
    post_str = str(post)
    current_app.logger.info(f"{post_str} deleted.")
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
        flash(_("Edit Succeeded!"),  "success")
        return redirect(url_for('main.main'))
    return render_template("main/edit_post.html", id=id, form=form)


@main_bp.route('/collect-post/<int:id>/')
@login_required
def collect_post(id):
    post = Post.query.get(id)
    if not post.private and post.author != current_user:
        current_user.collect(post)
        push_collect_notification(collector=current_user, post=post, receiver=post.author)
        flash(_('Post collected.'),  'success')
    elif post.author == current_user:
        flash(_('You cannot collect your own post.'))
    else:
        flash(_('The author has set this post to invisible.'))
    return make_response(redirect_back())


@main_bp.route('/uncollect-post/<int:id>/')
@login_required
def uncollect_post(id):
    post = Post.query.get(id)
    current_user.uncollect(post)
    flash(_('Post uncollected.'),  'info')
    return make_response(redirect_back())


@main_bp.route('/collected-posts/')
@login_required
def collected_posts():
    # Get current user's collection
    posts = [post for post in Post.query.all() if current_user.is_collecting(post)]
    return render_template('main/collections.html', posts=posts)

