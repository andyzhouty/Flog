"""
    flog.api.v1.schemas
    ~~~~~~~~~~~~~~~~~~~
    User schema and post schema

    :copyright: Andy Zhou
    :license: MIT
"""
from flask import url_for
from flog.models import User, Post


def user_schema(user: User) -> dict:
    """User schema

    Args:
        user (User): User Model

    Returns:
        dict: contains user profile and basic info
    """
    user_dict = dict(
        id=user.id,
        url=url_for('api_v1.user', user_id=user.id, _external=True),
        kind='User',
        username=user.username,
        member_since=user.member_since,
        last_seen=user.last_seen,
    )
    if user.name:
        user_dict['name'] = user.name
    if user.location:
        user_dict['location'] = user.location
    if user.about_me:
        user_dict['about_me'] = user.about_me
    return user_dict


def post_schema(post: Post) -> dict:
    """Post schema

    Args:
        post (Post): Post Model

    Returns:
        dict: contains post data
    """
    post_schema = dict(
        id=post.id,
        author=user_schema(post.author),
        title=post.title,
        content=post.content,
        url=url_for('api_v1.post', post_id=post.id, _external=True),
        comments_count=len(post.comments),
        private=post.private
    )
    if len(post.comments) > 0:
        post_schema['comments'] = [dict(author=comment.author.username, body=comment.body)
                                   for comment in post.comments]
    return post_schema
