from flask import g
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
    return g.current_user is not None and (
        g.current_user == post.author or g.current_user.is_administrator()
    )


def can_edit_profile(user: User) -> bool:
    return g.current_user is not None and (
        g.current_user == user or g.current_user.is_administrator()
    )
