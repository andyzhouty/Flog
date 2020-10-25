from flask import url_for
from flog.models import User, Post

def user_schema(user: User) -> dict:
    return dict(
        id=user.id,
        url=url_for('api_v1.get_user', username=user.username),
        kind='User',
        username=user.username,
        member_since=user.member_since,
        last_seen=user.last_seen,
    )
