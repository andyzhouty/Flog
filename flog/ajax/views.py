"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from datetime import datetime, timedelta
from random import sample
from flask import render_template, jsonify, request, current_app
from apiflask import abort
from flask_babel import _
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import or_, and_
from . import ajax_bp
from ..models import Notification, User, Group, Post, Column, db
from ..extensions import csrf, limiter


@ajax_bp.route("/profile/<int:user_id>/")
def get_profile(user_id):
    u = User.query.get_or_404(user_id)
    return {
        "id": u.id,
        "username": u.username,
        "avatar": u.avatar_url,
        "avatar_style": u.load_avatar_style(),
        "profile_url": u.profile_url,
    }


@ajax_bp.route("/notification/count/")
def notification_count():
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 401
    count = Notification.query.with_parent(current_user).count()
    return jsonify(count=count)


@ajax_bp.route("/group/hint/")
def get_group_hint():
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 401
    user_input = request.args.get("q")
    hint = [
        group.name
        for group in Group.query.all()
        if (
            user_input.lower() in group.name.lower()
            and user_input != ""
            and (not group.private or current_user.is_administrator())
        )
    ]
    return jsonify(hint=hint[:5])


@ajax_bp.post("/post/<int:post_id>/coin/<int:coin_num>/")
@csrf.exempt
def coin_post(post_id: int, coin_num):
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 401
    post = Post.query.get_or_404(post_id)
    message = post.add_coin(coin_num, current_user)
    if message:
        print(message)
        return jsonify(message=message), 400
    return {"message": "ok"}


@ajax_bp.post("/post/<int:post_id>/collect/")
@csrf.exempt
def collect_post(post_id: int):
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 401
    post = Post.query.get_or_404(post_id)
    current_user.collect(post)
    if current_user.is_collecting(post):
        return {"message": "ok"}, 200
    return {"message": "failed"}, 400


@ajax_bp.post("/post/<int:post_id>/uncollect/")
@csrf.exempt
def uncollect_post(post_id: int):
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 401
    post = Post.query.get_or_404(post_id)
    current_user.uncollect(post)
    if not current_user.is_collecting(post):
        return {"message": "ok"}, 200
    return {"message": "failed"}, 400


@ajax_bp.route("/get_posts/<int:post_id>/")
def get_post(post_id: int):
    posts = Post.query.filter(
        or_(~Post.private, Post.author_id == current_user.id)
    ).order_by(Post.timestamp.desc())[::1]
    if post_id != 0:
        post = Post.query.get_or_404(post_id)
        index = posts.index(post)
    else:
        index = -1
    target = {
        "message": [
            {
                "id": p.id,
                "author": (p.author.username if p.author else _("Deleted Flog User")),
                "columns": [
                    {"id": column.id, "name": column.name} for column in p.columns
                ],
                "title": p.title,
                "avatar": p.author.avatar_url(),
                "avatar_style": p.author.load_avatar_style(),
                "timestamp": [
                    (datetime.utcnow() - p.timestamp).days,
                    (datetime.utcnow() - p.timestamp).seconds // 3600,
                    ((datetime.utcnow() - p.timestamp).seconds // 60) % 60,
                    (datetime.utcnow() - p.timestamp).seconds % 60,
                ],
                "content": (
                    Markup(p.content).striptags()[:220] + "..."
                    if len(Markup(p.content).striptags()) >= 220
                    else Markup(p.content).striptags()
                ),
                "coins": p.coins,
                "private": p.private,
            }
            for p in posts[index + 1 : index + 13]
            if p.author.username != p.title
        ]
    }
    return target


@ajax_bp.route("/notifications/read/<int:id>/")
def read_notification(id):
    notification = Notification.query.get_or_404(id)
    if notification.receiver != current_user:
        return {"message": "forbidden"}, 403
    db.session.delete(notification)
    db.session.commit()
    return {"message": "ok"}, 200


@ajax_bp.route("/get_posts/hot_posts/")
def get_hot_posts():
    posts = [
        post
        for post in Post.query.filter(
            and_(Post.coins >= current_app.config["HOT_POST_COIN"], ~Post.private)
        ).order_by(Post.timestamp.desc())
    ]
    columns = [column for column in Column.query.all() if column.topped]
    if len(posts) > 15:
        posts = posts[:15]
    if len(posts) > 3:
        posts = sample(posts, 3)
    if len(columns) > 2:
        columns = sample(columns, 2)
    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "author": post.author.username,
                "coins": post.coins,
                "timestamp": [
                    (datetime.utcnow() - post.timestamp).days,
                    (datetime.utcnow() - post.timestamp).seconds // 3600,
                    ((datetime.utcnow() - post.timestamp).seconds // 60) % 60,
                    (datetime.utcnow() - post.timestamp).seconds % 60,
                ],
                "collectors": len(post.collectors),
                "comments": len(post.comments),
            }
            for post in posts
        ],
        "columns": [
            {
                "id": column.id,
                "name": column.name,
                "author": column.author.username,
                "coins": sum([post.coins for post in column.posts]),
                "collects": sum([len(post.collectors) for post in column.posts]),
                "posts": len(column.posts),
            }
            for column in columns
        ],
    }


@ajax_bp.route("/get_posts/<int:y>/<int:m>/")
def get_post_list(y: int, m: int):
    posts = Post.query.filter(
        or_(
            ~Post.private,
            Post.author_id == current_user.id,
        ),
    ).order_by(Post.timestamp.desc())
    posts = [
        post
        for post in posts
        if (post.timestamp.year == y and post.timestamp.month == m)
    ]
    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "day": post.timestamp.day,
                "author": post.author.username,
            }
            for post in posts
        ]
    }


@ajax_bp.route("/get_status/<int:id>")
@limiter.exempt
def get_status(id: int):
    u = User.query.get(id)
    if datetime.utcnow() - u.last_seen > timedelta(seconds=60):
        return {"status": "offline"}
    else:
        return {"status": u.default_status or "online"}


@ajax_bp.route("/get_all_status/")
@limiter.exempt
def get_all_status():
    users = User.query.all()
    return {
        u.id: get_status(u.id)["status"]
        for u in users
        if get_status(u.id)["status"] != "offline"
    }


@ajax_bp.route("/ping_status/")
@limiter.exempt
def ping_status():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    return {"message": "ok"}
