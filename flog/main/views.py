"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from datetime import datetime
from flog.decorators import permission_required
import bleach
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    current_app,
)
from flask_babel import _
from flask_login import current_user, login_required
from ..models import Permission, db, Post, Comment, User, Group, Column
from ..utils import redirect_back
from ..notifications import push_collect_notification, push_comment_notification
from .forms import ColumnForm, PostForm, EditForm, CommentForm
from . import main_bp


@main_bp.route("/")
def main():
    if not (current_user.is_authenticated or request.args.get("force", False)):
        return render_template("main/not_authorized.html")
    page = request.args.get("page", 1, type=int)
    if current_user.is_administrator():
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config["POSTS_PER_PAGE"]
        )
    else:
        pagination = (
            Post.query.filter(~Post.private)
                .order_by(Post.timestamp.desc())
                .paginate(page, per_page=current_app.config["POSTS_PER_PAGE"])
        )
    posts = pagination.items
    return render_template("main/main.html", pagination=pagination, posts=posts)


@main_bp.route("/write/", endpoint="write", methods=["GET", "POST"])
@login_required
@permission_required(Permission.WRITE)
def create_post():
    form = PostForm()
    form.columns.choices = [
        (column.id, column.name)
        for column in Column.query.filter_by(author=current_user).all()
    ]
    if form.validate_on_submit():
        cleaned_content = bleach.clean(
            form.content.data,
            tags=current_app.config["FLOG_ALLOWED_TAGS"],
            attributes=current_app.config["FLOG_ALLOWED_HTML_ATTRIBUTES"],
            strip_comments=True,
        )
        post = Post(
            author=current_user,
            title=form.title.data,
            content=cleaned_content,
            private=form.private.data,
        )
        print("Here")
        for col_id in form.columns.data:
            column = Column.query.get(col_id)
            post.columns.append(column)
            print(current_user.columns)
        db.session.add(post)
        # Add the post to the database.
        db.session.commit()
        current_app.logger.info(f"{str(post)} is added.")
        flash(_("Your post has been added"), "success")
        return redirect(url_for("main.main"))
    return render_template("main/new_post.html", form=form)


@main_bp.route("/post/<int:id>/", methods=["GET", "POST"])
def full_post(id: int):
    post = Post.query.get_or_404(id)
    if (
            (not post.private)
            or post.author == current_user
            or current_user.is_administrator()
    ):
        page = request.args.get("page", 1, type=int)
        per_page = current_app.config["COMMENTS_PER_PAGE"]
        pagination = (
            Comment.query.with_parent(post)
                .order_by(Comment.timestamp.asc())
                .paginate(page, per_page)
        )
        comments = pagination.items
        form = CommentForm()

        if form.validate_on_submit():
            if not current_user.can(Permission.COMMENT):
                flash(_("Blocked users cannot post a comment!"))
                return redirect_back()
            if post.private:
                flash(_("You cannot comment a private post!"))
                return redirect_back()
            comment = Comment(
                author=current_user,
                post=post,
                body=form.body.data,
            )
            replied_id = request.args.get("reply")
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
            db.session.add(comment)
            db.session.commit()
            if post.author is not None and post.author != current_user:
                push_comment_notification(comment=comment, receiver=post.author)
            flash(_("Comment published!"), "success")
            return redirect(url_for("main.full_post", id=post.id))

        kwargs = dict(
            post=post,
            pagination=pagination,
            comments=comments,
            form=form,
        )
        replied_id = request.args.get("reply")
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            kwargs["replied_comment"] = replied_comment
            print(replied_comment)
        return render_template("main/full_post.html", **kwargs)
    else:
        flash(_("The author has set this post to invisible."))
        return redirect_back()


@main_bp.route("/reply/comment/<int:comment_id>/")
@login_required
@permission_required(Permission.COMMENT)
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(
        url_for("main.full_post", id=comment.post.id, reply=comment_id)
        + "#reply-comment-form"
    )


@main_bp.route("/comment/delete/<int:comment_id>/", methods=["POST"])
@login_required
@permission_required(Permission.COMMENT)
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.delete()
    return redirect_back()


@main_bp.route("/post/manage/")
@login_required
@permission_required(Permission.WRITE)
def manage_posts():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Post.query.filter_by(author=current_user)
            .order_by(Post.timestamp.desc())
            .paginate(page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    )
    return render_template("main/personal_posts.html", pagination=pagination)


@main_bp.route("/post/delete/<int:id>/", methods=["POST"])
@login_required
@permission_required(Permission.WRITE)
def delete_post(id):
    post = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post.author):
        abort(403)
    post.delete()
    flash(_("Post id %d deleted" % id), "success")
    post_str = str(post)
    current_app.logger.info(f"{post_str} deleted.")
    return redirect(url_for("main.main"))


@main_bp.route("/post/edit/<int:id>/", methods=["GET", "POST"])
@login_required
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get(id)
    if not (current_user.is_administrator() or current_user == post.author):
        abort(403)
    form = EditForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.timestamp = datetime.utcnow()
        post.private = form.private.data
        db.session.add(post)
        db.session.commit()
        current_app.logger.info(f"Post id {id} editted.")
        flash(_("Edit Succeeded!"), "success")
        return redirect(url_for("main.main"))
    form.title.data = post.title
    form.content.data = post.content
    form.private.data = post.private
    return render_template("main/edit_post.html", form=form)


@main_bp.route("/post/collect/<int:id>/")
@login_required
def collect_post(id):
    post = Post.query.get(id)
    if (
            not post.private
            and post.author != current_user
            and not current_user.is_collecting(post)
    ):
        current_user.collect(post)
        push_collect_notification(
            collector=current_user,
            post=post,
            receiver=post.author,
        )
        flash(_("Post collected."), "success")
    elif current_user.is_collecting(post):
        flash(_("Already collected."))
    elif post.author == current_user:
        flash(_("You cannot collect your own post."))
    else:
        flash(
            _(
                "The author has set this post to invisible. So you cannot collect this post."
            )
        )
    return redirect_back()


@main_bp.route("/post/uncollect/<int:id>/")
@login_required
def uncollect_post(id):
    post = Post.query.get(id)
    current_user.uncollect(post)
    flash(_("Post uncollected."), "info")
    return redirect_back()


@main_bp.route("/post/collected/")
@login_required
def collected_posts():
    # Get current user's collection
    posts = [post for post in Post.query.all() if current_user.is_collecting(post)]
    return render_template("main/collections.html", posts=posts)


@main_bp.route("/search/")
@login_required
def search():
    q = request.args.get("q", "")
    q = q.lower()
    if q == "":
        flash(_("Enter keyword about post or user."), "warning")
        return redirect_back()

    category = request.args.get("category", "post")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["SEARCH_RESULT_PER_PAGE"]
    if category == "user":
        query = User.query.filter(User.username.ilike(f"%{q}%"))
    elif category == "group":
        query = Group.query.filter(Group.name.ilike(f"%{q}%"))
    elif category == "column":
        query = Column.query.filter(Column.name.ilike(f"%{q}%"))
    else:
        query = Post.query.filter(Post.title.ilike(f"%{q}%"))
    results_count = query.count()
    pagination = query.paginate(page, per_page)

    results = pagination.items
    return render_template(
        "main/search.html",
        q=q,
        results=results,
        results_count=results_count,
        pagination=pagination,
        category=category,
    )


@main_bp.route("/column/create/", methods=["GET", "POST"])
@login_required
@permission_required(Permission.WRITE)
def create_column():
    form = ColumnForm()
    form.posts.choices = [
        (post.id, post.title)
        for post in Post.query.filter_by(author=current_user).all()
    ]
    if form.validate_on_submit():
        column = Column(name=form.name.data, author=current_user)
        for post_id in form.posts.data:
            post = Post.query.get(post_id)
            if post.author != current_user:
                flash(_("You can't add others' posts to your column!"))
                return redirect_back()
            column.posts.append(post)
        db.session.add(column)
        db.session.commit()
        flash(_("Your column was successfully created."))
        return redirect_back()
    return render_template("main/create_column.html", form=form)


@main_bp.route("/column/<int:id>/")
@login_required
def view_column(id: int):
    column = Column.query.get_or_404(id)
    page = request.args.get("page", 1)
    pagination = Post.query.with_parent(column).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    return render_template("main/column.html", column=column, pagination=pagination)
