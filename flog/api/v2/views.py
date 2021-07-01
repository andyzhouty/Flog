"""
    flog.api.v2.views
    ~~~~~~~~~~~~~~~~~

    The module for creating url routes.

    :copyright: Andy Zhou
    :license: MIT
"""
from flask import jsonify
from . import api_v2
from .resources import (
    IndexAPI,
    UserAPI,
    TokenAPI,
    PostAPI,
    NotificationAPI,
    FollowAPI,
    CommentAPI,
    ImageAPI,
    CollectionAPI,
)
from .schemas import user_schema, post_schema, comment_schema
from flog.models import User, Post

# index
api_v2.add_url_rule("/", view_func=IndexAPI.as_view("index"), methods=["GET"])
# get user schema
api_v2.add_url_rule(
    "/user/<int:user_id>/",
    view_func=UserAPI.as_view("user"),
    methods=["GET", "PUT", "DELETE"],
)
# get/put/patch/delete a post
api_v2.add_url_rule(
    "/post/<int:post_id>/",
    view_func=PostAPI.as_view("post"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)
api_v2.add_url_rule(
    "/post/new/", view_func=PostAPI.as_view("new_post"), methods=["POST"]
)
# collect
api_v2.add_url_rule(
    "/post/<any(collect,uncollect):collect_or_uncollect>/<int:post_id>/",
    view_func=CollectionAPI.as_view("collect"),
    methods=["GET"],
)
# follow
api_v2.add_url_rule(
    "/user/<any(follow,unfollow):follow_or_unfollow>/<int:user_id>/",
    view_func=FollowAPI.as_view("follow"),
    methods=["GET"],
)
# comment
api_v2.add_url_rule(
    "/comment/<int:comment_id>/",
    view_func=CommentAPI.as_view("comment"),
    methods=["GET", "DELETE"],
)
api_v2.add_url_rule(
    "/comment/new/", view_func=CommentAPI.as_view("new_comment"), methods=["POST"]
)
# auth token
api_v2.add_url_rule(
    "/oauth/token/", view_func=TokenAPI.as_view("oauth_token"), methods=["POST"]
)
# notification
api_v2.add_url_rule(
    "/notifications/unread/",
    view_func=NotificationAPI.as_view("notification"),
    methods=["GET"],
)
api_v2.add_url_rule(
    "/image/upload/", view_func=ImageAPI.as_view("image"), methods=["POST"]
)
api_v2.add_url_rule(
    "/image/<int:image_id>/",
    view_func=ImageAPI.as_view("image_delete"),
    methods=["DELETE"],
)


# folder-like urls
@api_v2.route("/post/<int:post_id>/comments/")
def comments_of_a_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    return jsonify([comment_schema(c) for c in post.comments])


@api_v2.route("/user/<int:user_id>/posts/")
def posts_of_an_author(user_id: int):
    user = User.query.get_or_404(user_id)
    return jsonify([post_schema(p) for p in user.posts])


@api_v2.route("/user/<int:user_id>/followers/")
def followers(user_id: int):
    user = User.query.get_or_404(user_id)
    return jsonify([user_schema(f.follower) for f in user.followers])


@api_v2.route("/user/<int:user_id>/following/")
def following(user_id: int):
    user = User.query.get_or_404(user_id)
    return jsonify([user_schema(f.followed) for f in user.following])


@api_v2.route("/user/<int:user_id>/comments/")
def comments_of_a_user(user_id: int):
    user = User.query.get_or_404(user_id)
    return jsonify([comment_schema(c) for c in user.comments])
