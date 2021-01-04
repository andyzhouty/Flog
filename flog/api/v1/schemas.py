"""
    flog.api.v1.schemas
    ~~~~~~~~~~~~~~~~~~~
    User schema and post schema

    :copyright: Andy Zhou
    :license: MIT
"""
from flask import url_for
from flog.models import Comment, User, Post


def user_schema(user: User) -> dict:
    """User schema

    Args:
        user (User): User Model

    Returns:
        dict: contains user profile and basic info
    """
    user_dict = dict(
        kind="User",
        id=user.id,
        url=url_for("api_v1.user", user_id=user.id, _external=True),
        username=user.username,
        member_since=user.member_since,
        last_seen=user.last_seen,
    )
    if user.name:
        user_dict["name"] = user.name
    if user.location:
        user_dict["location"] = user.location
    if user.about_me:
        user_dict["about_me"] = user.about_me
    return user_dict


def post_schema(post: Post, include_comments: bool = True) -> dict:
    """Post schema

    Args:
        post (Post): Post Model
        include_comments (bool): Whether the return value includes comments list.

    Returns:
        dict: contains post data
    """
    post_schema = dict(
        kind="Post",
        id=post.id,
        author=user_schema(post.author),
        title=post.title,
        content=post.content,
        url=url_for("api_v1.post", post_id=post.id, _external=True),
        comments_count=len(post.comments),
        private=post.private,
    )
    if len(post.comments) > 0 and include_comments:
        post_schema["comments"] = [
            dict(author=comment.author.username, body=comment.body)
            for comment in post.comments
        ]
    return post_schema


def comment_schema(comment: Comment) -> dict:
    """Comment schema

    Args:
        post (Comment): Comment Model

    Returns:
        dict: comment schema
    """
    comment_schema = dict(
        kind="Comments",
        author=user_schema(comment.author),
        post=post_schema(comment.post, False),
        id=comment.id,
        body=comment.body,
        url=url_for("api_v1.comment", comment_id=comment.id, _external=True),
    )
    return comment_schema
