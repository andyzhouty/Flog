"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from datetime import datetime
import bleach
from flask import (
    render_template, redirect, url_for, flash, abort, make_response,
    request, current_app
)
from flask_babel import _
from flask_login import current_user, login_required
from ..models import db, Post, Comment, User, Group
from ..utils import redirect_back
from ..notifications import push_collect_notification, push_comment_notification
from .forms import PostForm, EditForm, CommentForm
from . import main_bp


@main_bp.before_app_request
def before_app_request():
    ua = request.user_agent.string
    if ('spider' in ua or 'bot' in ua or 'python' in ua) and '/api/v1/' not in request.url:
        return 'F**k you, spider!'  # anti-webcrawler :P


@main_bp.route('/')
def main():
    if not (current_user.is_authenticated or request.args.get('force', False)):
        return render_template('main/not_authorized.html')
    page = request.args.get('page', 1, type=int)
    if current_user.is_administrator():
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE']
        )
    else:
        pagination = Post.query.filter(~Post.private).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE']
        )
    print(current_app.config['POSTS_PER_PAGE'])
    posts = pagination.items
    print(len(posts))
    return render_template('main/main.html', pagination=pagination, posts=posts)


@main_bp.route('/write/', endpoint='write', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        cleaned_content = bleach.clean(
            form.content.data,
            tags=current_app.config['FLOG_ALLOWED_TAGS'],
            attributes=['href', 'src', 'style'],
            strip_comments=True
        )
        post = Post(
            author=current_user,
            title=form.title.data,
            content=cleaned_content,
            private=form.private.data
        )
        db.session.add(post)
        # Add the post to the database.
        db.session.commit()
        current_app.logger.info(f'{str(post)} is added.')
        flash(_('Your post has been added'), "success")
        return redirect(url_for('main.main'))
    return render_template('main/new_post.html', form=form)


@main_bp.route('/post/<int:id>/', methods=['GET', 'POST'])
def full_post(id: int):
    post = Post.query.get_or_404(id)
    if ((not post.private) or post.author == current_user
            or current_user.is_administrator()):
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENTS_PER_PAGE']
        pagination = (Comment.query.with_parent(post)
                      .order_by(Comment.timestamp.asc())
                      .paginate(page, per_page))
        comments = pagination.items
        form = CommentForm()
        if form.validate_on_submit():
            if post.private:
                flash(_('You cannot comment a private post!'))
                return redirect_back()
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
            flash(_('Comment published!'), 'success')
            return redirect(url_for('main.full_post', id=post.id))
        return render_template('main/full_post.html', post=post, pagination=pagination,
                               comments=comments, form=form)
    else:
        flash(_('The author has set this post to invisible.'))
        return redirect_back()


@main_bp.route('/reply/comment/<int:comment_id>')
@login_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('main.full_post', id=comment.post.id, reply=comment_id) + '#comment-form')


@main_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.delete()
    return redirect_back()


@main_bp.route('/post/manage/')
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


@main_bp.route('/post/delete/<int:id>/', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post.author):
        abort(403)
    post.delete()
    flash(_("Post id %d deleted" % id), "success")
    post_str = str(post)
    current_app.logger.info(f"{post_str} deleted.")
    return redirect(url_for('main.main'))


@main_bp.route('/post/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post.author):
        abort(403)
    form = EditForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        current_app.logger.info(f'Post id {id} editted.')
        flash(_("Edit Succeeded!"), "success")
        return redirect(url_for('main.main'))
    form.title.data = post.title
    form.content.data = post.content
    return render_template("main/edit_post.html", form=form)


@main_bp.route('/post/collect/<int:id>/')
@login_required
def collect_post(id):
    post = Post.query.get(id)
    if not post.private and post.author != current_user and not current_user.is_collecting(post):
        current_user.collect(post)
        push_collect_notification(
            collector=current_user,
            post=post,
            receiver=post.author,
        )
        flash(_('Post collected.'), 'success')
    elif current_user.is_collecting(post):
        flash(_('Already collected.'))
    elif post.author == current_user:
        flash(_('You cannot collect your own post.'))
    else:
        flash(_('The author has set this post to invisible. So you cannot collect this post.'))
    return redirect_back()


@main_bp.route('/post/uncollect/<int:id>/')
@login_required
def uncollect_post(id):
    post = Post.query.get(id)
    current_user.uncollect(post)
    flash(_('Post uncollected.'), 'info')
    return redirect_back()


@main_bp.route('/post/collected/')
@login_required
def collected_posts():
    # Get current user's collection
    posts = [post for post in Post.query.all() if current_user.is_collecting(post)]
    return render_template('main/collections.html', posts=posts)


@main_bp.route('/search/')
@login_required
def search():
    q = request.args.get('q', '')
    q = q.lower()
    print(q)
    if q == '':
        flash(_('Enter keyword about post or user.'), 'warning')
        return redirect_back()

    category = request.args.get('category', 'post')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SEARCH_RESULT_PER_PAGE']
    if category == 'user':
        query = User.query.filter(User.username.ilike(f"%{q}%"))
        pagination = query.paginate(page, per_page)
        results_count = query.count()
    elif category == 'group':
        query = Group.query.filter(Group.name.ilike(f"%{q}%"))
        pagination = query.paginate(page, per_page)
        results_count = query.count()
    else:
        query = Post.query.filter(Post.title.ilike(f"%{q}%"))
        pagination = query.paginate(page, per_page)
        results_count = query.count()
    results = pagination.items
    print(results)
    return render_template('main/search.html', q=q,
                           results=results, results_count=results_count,
                           pagination=pagination, category=category)
