"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from datetime import datetime
from flask import render_template, jsonify, request
from apiflask import abort
from flask_babel import _
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import or_, and_
from . import ajax_bp
from ..models import Notification, User, Group, Post, db
from ..extensions import csrf, moment


@ajax_bp.route("/profile/<int:user_id>/")
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("ajax/profile_popup.html", user=user)


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
    posts = Post.query.filter(or_(~Post.private, Post.author_id == current_user.id)).order_by(Post.timestamp.desc())[::1]
    if post_id != 0:
        post = Post.query.get_or_404(post_id)
        index = posts.index(post)
    else:
        index = -1
    target = {"message": [{
        "id": p.id, "author": (p.author.username if p.author else _("Deleted Flog User")),
        "columns": p.columns, "title": p.title,
        "avatar": p.author.avatar_url(),
        "avatar_style": p.author.load_avatar_style(),
        "timestamp": [
            (datetime.utcnow() - p.timestamp).days,
            (datetime.utcnow() - p.timestamp).seconds // 3600,
            ((datetime.utcnow() - p.timestamp).seconds // 60) % 60,
            (datetime.utcnow() - p.timestamp).seconds % 60
        ],
        "content": (Markup(p.content).striptags()[:220] + "..." if len(Markup(p.content).striptags())>=220 else Markup(p.content).striptags()), "coins": p.coins,
        "private": p.private,
    } for p in posts[index + 1 : index + 13] if p.author.username != p.title]}
    return target
