"""
    flog.api.v1.resources
    ~~~~~~~~~~~~~~~~~~~~~
    This module contains functions and APIs of this website.

    :copyright: Andy Zhou
    :license: MIT License
"""

from flask import g, request, jsonify, url_for
from flask.views import MethodView
from .errors import ValidationError, bad_request, forbidden  # noqa
from .authentication import auth
from .schemas import comment_schema, user_schema, post_schema
from flog.models import db, User, Post, Comment, Notification, Image
from flog.utils import clean_html, get_image_path_and_url
from ..api_utils import get_post_data, can_edit_post, can_edit_profile


class IndexAPI(MethodView):
    def get(self):
        return jsonify(
            {
                "api_version": "1.0",
                "api_base_url": url_for("api_v1.index", _external=True),
            }
        )


class UserAPI(MethodView):
    """API for user operations"""

    decorators = [auth.login_required]

    def get(self, user_id: int):
        """Get User"""
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema(user))

    def put(self, user_id: int):
        """Change user profile"""
        user = User.query.get_or_404(user_id)
        if not can_edit_profile(user):
            return forbidden("You cannot edit this user's profile.")
        user.username = request.json.get("username", user.username)
        user.name = request.json.get("name", user.name)
        user.location = request.json.get("location", user.location)
        user.about_me = request.json.get("about_me", user.about_me)
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema(user))

    def delete(self, user_id: int):
        """Delete user"""
        user = User.query.get_or_404(user_id)
        if not can_edit_profile(user):
            return forbidden("You cannot delete this user.")
        user.delete()
        return f"User id {user_id} deleted.", 200


class PostAPI(MethodView):
    """API for post operations"""

    decorators = [auth.login_required]

    def get(self, post_id: int):
        """Get Post"""
        post = Post.query.get_or_404(post_id)
        if (not post.private) or (post.author == g.current_user):
            return jsonify(post_schema(post))
        else:
            return forbidden("The post is private!")

    def post(self) -> "201":
        """Create a post"""
        data = request.get_json()
        title, content, private = get_post_data(data, ValidationError)
        # remove javascript and css from the content
        cleaned_content = clean_html(content)

        post = Post(
            author=g.current_user,
            title=title,
            content=cleaned_content,
            private=private,
        )
        db.session.add(post)
        try:
            db.session.commit()
        except Exception as e:
            return bad_request(e)
        return jsonify(post_schema(post))

    def put(self, post_id: int) -> "204" or "403" or "404":
        """Edit Post"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden("You cannot edit this post.")
        data = request.get_json()
        title, content, private = get_post_data(data, ValidationError)
        cleaned_content = clean_html(content)
        post.title, post.content, post.private = title, cleaned_content, private
        db.session.commit()
        return "", 204

    def patch(self, post_id) -> "204" or "403":
        """Toggle Post Visibility"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden("You cannot change this post's visiblity.")
        post.private = not post.private
        db.session.add(post)
        db.session.commit()
        return "", 204

    def delete(self, post_id: int) -> "204" or "403":
        """Delete Post"""
        post = Post.query.get_or_404(post_id)
        if not can_edit_post(post):
            return forbidden("You cannot delete this post.")
        post.delete()
        return "", 204


class CollectionAPI(MethodView):
    """API for collections."""

    decorators = [auth.login_required]

    def get(self, collect_or_uncollect: str, post_id: int) -> "200" or "404":
        post = Post.query.get_or_404(post_id)
        if collect_or_uncollect == "collect":
            g.current_user.collect(post)
            return f"Post id {post.id} collected.", 200
        else:
            g.current_user.uncollect(post)
            return f"Post id {post.id} uncollected.", 200


class CommentAPI(MethodView):
    """API for comments."""

    decorators = [auth.login_required]

    def get(self, comment_id: int) -> dict:
        comment = Comment.query.get_or_404(comment_id)
        return jsonify(comment_schema(comment))

    def post(self) -> "200":
        data = request.get_json()
        body = clean_html(data.get("body").strip())
        post_id = data.get("post_id")
        if not (isinstance(body, str) and body != "" and isinstance(post_id, int)):
            return bad_request("Invalid input")
        post = Post.query.get_or_404(post_id)
        comment = Comment(author=g.current_user, body=body, post=post)
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment_schema(comment))

    def delete(self, comment_id: int) -> "204" or "403":
        comment = Comment.query.get_or_404(comment_id)
        if g.current_user is not None and comment.author == g.current_user:
            comment.delete()
            return "", 204
        else:
            return forbidden("You cannot delete this comment.")


class TokenAPI(MethodView):
    decorators = [auth.login_required]

    def get(self):
        return dict(access_token=g.current_user.gen_api_auth_token(), expires_in=3600)


class NotificationAPI(MethodView):
    decorators = [auth.login_required]

    def get(self):
        # fmt: off
        unread_num = Notification.query.with_parent(g.current_user).count()
        unread_items = [
            (notification.message, notification.id)
            for notification in
            Notification.query.with_parent(g.current_user).all()
        ]
        # fmt: on
        return jsonify({"unread_num": unread_num, "unread_items": unread_items})


class ImageAPI(MethodView):
    decorators = [auth.login_required]

    def post(self):
        image_obj = request.files.get("upload")
        if image_obj is None:
            return bad_request("No file was uploaded!")
        response = get_image_path_and_url(image_obj, g.current_user)
        if response.get("error") is not None:
            return bad_request(response["error"])
        image_url = response["image_url"]
        image_id = response["image_id"]
        return (
            jsonify(
                message="Upload Success",
                image_url=image_url,
                image_id=image_id,
                filename=response["filename"],
            ),
            201,
        )

    def delete(self, image_id):
        image = Image.query.get_or_404(image_id)
        image.delete()
        return "", 204
