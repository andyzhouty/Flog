"""
    flog.api.v1.views
    ~~~~~~~~~~~~~~~~~

    The module for creating url routes.

    :copyright: Andy Zhou
    :license: MIT
"""
from . import api_v1
from .resources import (
    CollectionAPI,
    CommentAPI,
    FollowAPI,
    IndexAPI,
    TokenAPI,
    UserAPI,
    PostAPI,
    NotificationAPI,
)

# index
api_v1.add_url_rule("/", view_func=IndexAPI.as_view("index"), methods=["GET"])
# get user schema
api_v1.add_url_rule(
    "/user/<int:user_id>/",
    view_func=UserAPI.as_view("user"),
    methods=["GET", "PUT", "DELETE"],
)
# get/put/patch/delete a post
api_v1.add_url_rule(
    "/post/<int:post_id>/",
    view_func=PostAPI.as_view("post"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)
api_v1.add_url_rule(
    "/post/new/", view_func=PostAPI.as_view("new_post"), methods=["POST"]
)
# collect
api_v1.add_url_rule(
    "/post/<any(collect, uncollect):collect_or_uncollect>/<int:post_id>/",
    view_func=CollectionAPI.as_view("collect"),
    methods=["GET"],
)
# follow
api_v1.add_url_rule(
    "/user/<any(follow, unfollow):follow_or_unfollow>/<int:user_id>/",
    view_func=FollowAPI.as_view("follow"),
    methods=["GET"],
)
# comment
api_v1.add_url_rule(
    "/comment/<int:comment_id>/",
    view_func=CommentAPI.as_view("comment"),
    methods=["GET", "DELETE"],
)
api_v1.add_url_rule(
    "/comment/new/", view_func=CommentAPI.as_view("new_comment"), methods=["POST"]
)
# auth token
api_v1.add_url_rule(
    "/auth/token/", view_func=TokenAPI.as_view("auth_token"), methods=["GET"]
)
# notification
api_v1.add_url_rule(
    "/notifications/unread/",
    view_func=NotificationAPI.as_view("notification"),
    methods=["GET"],
)
