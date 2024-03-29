from flask import g, request
from ..models import Post, User


def get_post_data(data: dict, validation_error: ValueError()) -> tuple:
    title = data.get("title")
    content = data.get("content")
    private = data.get("private")
    if (
        content is None
        or str(content).strip() == ""
        or title is None
        or str(title).strip() == ""
    ):
        raise validation_error("The post is invalid or empty.")
    if private is not None and private != 0:
        private = True
    else:
        private = False
    return title, content, private


def can_edit_post(post: Post) -> bool:
    return g.current_user is not None and (g.current_user == post.author)


def can_edit_profile(user: User) -> bool:
    return g.current_user is not None and (g.current_user == user)


def get_current_user():
    auth = request.headers.get("Authorization")
    if auth:
        if not auth.startswith("Bearer"):
            return None
        token = auth[7:]
        user = User.verify_auth_token_api(token)
        return user
