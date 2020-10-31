from flask import url_for
from flog.models import User, Post


def user_schema(user: User) -> dict:
    return dict(
        id=user.id,
        url=url_for('api_v1.get_user', user_id=user.id, _external=True),
        kind='User',
        username=user.username,
        member_since=user.member_since,
        last_seen=user.last_seen,
    )


def post_schema(post: Post) -> dict:
    return dict(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        url=url_for('api_v1.post', post_id=post.id, _external=True),
        private=str(post.private)
    )
