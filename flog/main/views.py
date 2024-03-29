"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
import os
from datetime import datetime
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
from sqlalchemy import or_
from urllib.parse import quote
from flog.decorators import permission_required
from flog.extensions import csrf

# User and Group are necessary for line 328
from ..models import db, Post, Comment, User, Group, Column, Notification
from ..utils import redirect_back, clean_html
from ..notifications import (
    push_coin_notification,
    push_collect_notification,
    push_comment_notification,
    push_submitting_post_to_column_notification,
    push_transposting_to_column_notification,
)
from .forms import ColumnForm, PostForm, CommentForm
from . import main_bp


@main_bp.before_app_request
def before_request():
    ban_ip_list = os.getenv("BAN_IP_LIST", "").split(":")
    ban_username_list = os.getenv("BAN_USERNAME_LIST", "").split(":")
    if request.remote_addr in ban_ip_list:
        return (
            render_template("errors/error.html", error_message="Your ip is banned"),
            403,
        )
    if current_user.is_authenticated and current_user.username in ban_username_list:
        return (
            render_template(
                "errors/error.html", error_message="Your username is banned"
            ),
            403,
        )


@main_bp.route("/")
def main():
    target = request.args.get("target", "posts", type=str)
    if not (current_user.is_authenticated or request.args.get("force", False)):
        return render_template("main/not_authorized.html")
    posts = Post.query.filter(
        or_(~Post.private, Post.author_id == current_user.id)
    ).order_by(Post.timestamp.desc())[0:12]
    notifications = (
        Notification.query.with_parent(current_user)
        if current_user.is_authenticated
        else None
    )
    return render_template(
        "main/main.html", posts=posts, notifications=notifications, target=target
    )


@main_bp.route("/write/", endpoint="write", methods=["GET", "POST"])
@login_required
@permission_required
def create_post():
    current_app.config["CKEDITOR_PKG_TYPE"] = "standard"
    form = PostForm()
    form.columns.choices = [
        (column.id, column.name)
        for column in Column.query.filter_by(author=current_user).all()
    ]
    if form.validate_on_submit():
        cleaned_content = clean_html(form.content.data)
        post = Post(
            author=current_user,
            title=form.title.data,
            content=cleaned_content,
            private=form.private.data,
        )
        post.columns += [Column.query.get(column_id) for column_id in form.columns.data]
        if not post.private:
            current_user.experience += 5
        db.session.add(post)
        # Add the post to the database.
        db.session.commit()
        current_app.logger.info(f"{str(post)} is added.")
        flash(_("Your post has been added"), "green")
        return redirect(url_for(".full_post", id=post.id))
    return render_template("main/new_post.html", form=form)


@main_bp.route("/post/<int:id>/", methods=["GET", "POST"])
def full_post(id: int):
    current_app.config["CKEDITOR_PKG_TYPE"] = "basic"
    post = Post.query.get(id)
    if post is None:
        abort(404)
    if (not post.private) or post.author == current_user:
        page = request.args.get("page", 1, type=int)
        per_page = current_app.config["COMMENTS_PER_PAGE"]
        pagination = (
            Comment.query.with_parent(post)
            .order_by(Comment.timestamp.asc())
            .paginate(page, per_page)
        )
        form = CommentForm()

        if form.validate_on_submit():
            if not current_user.can:
                flash(_("Blocked users cannot post a comment!"))
                return redirect_back()
            if post.private:
                flash(_("You cannot comment a private post!"))
                return redirect_back()
            comment = Comment(
                author=current_user,
                post=post,
                body=clean_html(form.body.data),
            )
            replied_id = request.args.get("reply")
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
                push_comment_notification(
                    comment=replied_comment, receiver=replied_comment.author
                )
            db.session.add(comment)
            db.session.commit()
            if post.author is not None and post.author != current_user:
                push_comment_notification(comment=comment, receiver=post.author)
            flash(_("Comment published!"), "green")
            return redirect(url_for("main.full_post", id=post.id))

        kwargs = dict(
            post=post,
            pagination=pagination,
            comments=Comment.query.with_parent(post).all(),
            form=form,
        )
        replied_id = request.args.get("reply")
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            kwargs["replied_comment"] = replied_comment
        if post.author:
            post.author.clicks += 1
            post.author.clicks_today += 1
            db.session.commit()
        return render_template("main/full_post.html", **kwargs)
    else:
        flash(_("The author has set this post to invisible."))
        return redirect_back()


@main_bp.route("/post/all/")
def all_posts():
    posts = Post.query.filter(
        or_(~Post.private, Post.author_id == current_user.id)
    ).order_by(Post.timestamp.desc())
    last_post = posts[-1]
    post_date = [
        last_post.timestamp.year,
        last_post.timestamp.month,
    ]
    now = [datetime.utcnow().year, datetime.utcnow().month]
    dates = []

    def _date_next(date: list):
        if date[1] == 12:
            return [date[0] + 1, 1]
        else:
            return [date[0], date[1] + 1]

    while post_date != _date_next(now):
        dates.append(post_date)
        post_date = _date_next(post_date)
    return render_template(
        "main/all_posts.html",
        dates=dates[::-1],
        months=[
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
    )


@main_bp.route("/reply/comment/<int:comment_id>/")
@login_required
@permission_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(
        url_for("main.full_post", id=comment.post.id, reply=comment_id)
        + "#reply-comment-form"
    )


@main_bp.route("/comment/delete/<int:comment_id>/", methods=["POST"])
@login_required
@permission_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.delete()
    return redirect_back()


@main_bp.route("/post/manage/")
@login_required
@permission_required
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
@permission_required
def delete_post(id):
    post = Post.query.get(id)
    if current_user != post.author:
        abort(403)
    post.delete()
    flash(_("Post id %(id)d deleted", id=id), "green")
    post_str = str(post)
    current_app.logger.info(f"{post_str} deleted.")
    return redirect(url_for("main.main"))


@main_bp.route("/post/edit/<int:id>/", methods=["GET", "POST"])
@login_required
@permission_required
def edit_post(id):
    current_app.config["CKEDITOR_PKG_TYPE"] = "standard"
    post = Post.query.get(id)
    if current_user != post.author:
        abort(403)
    form = PostForm()
    form.columns.choices = [(column.id, column.name) for column in current_user.columns]
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.timestamp = datetime.utcnow()
        post.private = form.private.data
        post.columns += [Column.query.get(col_id) for col_id in form.columns.data]
        db.session.commit()
        current_app.logger.info(f"Post id {id} editted.")
        flash(_("Edit Succeeded!"), "green")
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
        flash(_("Post collected."), "green")
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
def uncollect_post(id: int):
    post = Post.query.get_or_404(id)
    current_user.uncollect(post)
    flash(_("Post uncollected."), "blue")
    return redirect_back()


@main_bp.route("/post/collected/")
@login_required
def collected_posts():
    # Get current user's collection
    posts = [post for post in Post.query.all() if current_user.is_collecting(post)]
    return render_template("main/collections.html", posts=posts)


@main_bp.route("/post/picks/")
@login_required
def picks():
    posts = Post.query.filter_by(picked=True).all()
    return render_template("main/picked.html", posts=posts)


@main_bp.route("/post/coin/<int:post_id>/", methods=["POST"])
@login_required
@csrf.exempt
def coin_post(post_id):
    post = Post.query.get_or_404(post_id)
    coins = request.form.get("coins", type=int)
    if (
        post.author == current_user
        or post in current_user.coined_posts
        or coins is None
        or coins < 1
        or coins > 2
        or current_user.coins < coins
    ):  # pragma: no cover
        abort(400)
    post.coins += coins
    current_user.coined_posts.append(post)
    current_user.coins -= coins
    current_user.experience += 10 * coins
    if post.author:
        post.author.coins += coins / 4
        post.author.experience += 10 * coins
        push_coin_notification(current_user, post.author, post, coins)
    db.session.commit()
    return redirect_back()


@main_bp.route("/search/")
@login_required
def search():
    q = request.args.get("q", "").lower()
    if q == "":
        flash(_("Enter keyword about post or user."), "yellow")
        return redirect_back()

    category = request.args.get("category", "post")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["SEARCH_RESULT_PER_PAGE"]
    name_key = dict(user="username", group="name", column="name", post="title")
    query = eval(
        "{0}.query.filter({0}.{1}.ilike('%{2}%'))".format(
            category.capitalize(), name_key[category], q
        )
    )
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
@permission_required
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
    page = request.args.get("page", 1, type=int)
    pagination = (
        Post.query.with_parent(column)
        .order_by(Post.timestamp.desc())
        .paginate(page, per_page=current_app.config["POSTS_PER_PAGE"])
    )
    return render_template("main/column.html", column=column, pagination=pagination)


@main_bp.route("/column/all/")
@login_required
def all_columns():
    page = request.args.get("page", default=1, type=int)
    pagination = Column.query.order_by(Column.timestamp.desc()).paginate(
        page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    return render_template("main/columns.html", pagination=pagination)


@main_bp.route("/column/<int:column_id>/request/<int:post_id>/", methods=["POST"])
@login_required
def request_post_to_column(column_id: int, post_id: int):
    post = Post.query.get_or_404(post_id)
    column = Column.query.get_or_404(column_id)
    if current_user != post.author:
        flash(_("You can't request others' posts to the column"))
    if post in column.posts:
        flash(_("The post is already in the column."))
        return redirect_back()
    if column.author is not None:
        push_submitting_post_to_column_notification(
            current_user, column.author, post, column
        )
    flash(_("Your request has been submitted to the manager of the column."))
    return redirect_back()


@main_bp.route("/post/<int:post_id>/transpost/<int:column_id>/", methods=["POST"])
@login_required
def transpost_post_to_column(
    post_id: int,
    column_id: int,
):
    post = Post.query.get_or_404(post_id)
    column = Column.query.get_or_404(column_id)
    if current_user != column.author:
        flash(_("You are not the manager of the column."))
        return redirect_back()
    if post in column.posts:
        flash(_("The post is already in the column."))
        return redirect_back()
    current_app.logger.debug(post.author)
    if post.author is not None:
        push_transposting_to_column_notification(
            current_user, post.author, post, column
        )
    flash(_("Your request has been submitted to the column"))
    return redirect_back()


@main_bp.route("/post/<int:post_id>/approve/<int:column_id>/")
@login_required
def approve_column(post_id: int, column_id: int):
    """
    Allow transposting the post to a column.
    This route should only be visited by the post's author.
    """
    post = Post.query.get_or_404(post_id)
    column = Column.query.get_or_404(column_id)
    if current_user != post.author:
        abort(403)
    if post not in column.posts:
        column.posts.append(post)
        db.session.commit()
        return redirect_back()
    flash(_("The post is already in the column."))
    return redirect_back()


@main_bp.route("/column/<int:column_id>/approve/<int:post_id>/")
@login_required
def approve_post(column_id: int, post_id: int):
    """
    Allow a post to be added to the column.
    This route should only be visited by the column's author.
    """
    post = Post.query.get_or_404(post_id)
    column = Column.query.get_or_404(column_id)
    if current_user != column.author:
        abort(403)
    if post not in column.posts:
        column.posts.append(post)
        db.session.commit()
        return redirect_back()
    flash(_("The post is already in the column."))
    return redirect_back()


@main_bp.route(
    "/tools/tex",
    methods=(
        "GET",
        "POST",
    ),
)
def textools():
    if request.method == "POST":
        tex = request.form["tex"]
        return render_template(
            "main/tex.html",
            url=f"https://www.zhihu.com/equation?tex={ quote(tex) }",
            tex_data=tex,
        )
    return render_template("main/tex.html", url="", tex_data="")
