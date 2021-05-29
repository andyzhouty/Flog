"""
    flog.api.v2.resources
    ~~~~~~~~~~~~~~~~~~~~~
    This module contains functions and APIs of this website.

    :copyright: Andy Zhou
    :license: MIT License
"""
from flog.utils import clean_html, get_image_path_and_url
from flask import g, request, jsonify, url_for
from flask.views import MethodView
from .errors import ValidationError, bad_request, forbidden  # noqa
from .authentication import auth_required
from .schemas import user_schema, post_schema, comment_schema
from flog.models import db, User, Post, Comment, Notification, Image
from ..api_utils import get_post_data, can_edit_post, can_edit_profile


class IndexAPI(MethodView):
    def get(self):
        return jsonify(
            {
                "api_version": "2.0",
                "api_base_url": url_for("api_v2.index", _external=True),
            }
        )


class UserAPI(MethodView):
    """API for user operations"""

    decorators = [auth_required]

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

    decorators = [auth_required]

    def get(self, post_id: int):
        """Get Post"""
        post = Post.query.get_or_404(post_id)
        return jsonify(post_schema(post))

    def post(self) -> "201":
        """Create a post"""
        data = request.get_json()
        title, content, private = get_post_data(data, ValidationError)
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
        post_data = get_post_data(data, ValidationError)
        post.title = post_data[0]
        post.content = post_data[1]
        post.private = post_data[2]
        db.session.add(post)
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

    decorators = [auth_required]

    def get(self, collect_or_uncollect: str, post_id: int) -> "200" or "404":
        post = Post.query.get_or_404(post_id)
        if collect_or_uncollect == "collect":
            g.current_user.collect(post)
            return f"Post id {post.id} collected.", 200
        else:
            g.current_user.uncollect(post)
            return f"Post id {post.id} uncollected.", 200


class FollowAPI(MethodView):
    """API for following operations."""

    decorators = [auth_required]

    def get(self, follow_or_unfollow: str, user_id: int) -> "204":
        user = User.query.get_or_404(user_id)
        if follow_or_unfollow == "follow":
            g.current_user.follow(user)
        else:
            g.current_user.unfollow(user)
        return "", 204


class CommentAPI(MethodView):
    """API for comments."""

    decorators = [auth_required]

    def get(self, comment_id: int) -> dict:
        comment = Comment.query.get_or_404(comment_id)
        return jsonify(comment_schema(comment))

    def post(self) -> "201":
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
    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            return bad_request("Either the username or the password was invalid.")
        token = user.gen_api_auth_token()
        response = jsonify(
            {"access_token": token, "expires_in": 3600, "token_type": "Bearer"}
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


class NotificationAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        unread_num = (
            Notification.query.with_parent(g.current_user)
            .filter_by(is_read=False)
            .count()
        )
        unread_items = [
            (notification.message, notification.id)
            for notification in Notification.query.with_parent(g.current_user)
            .filter_by(is_read=False)
            .all()
        ]
        return jsonify({"unread_num": unread_num, "unread_items": unread_items})


class ImageAPI(MethodView):
    decorators = [auth_required]

    def post(self):
        image_obj = request.files.get("upload")
        if image_obj is None:
            return bad_request("No file was uploaded!")
        response = get_image_path_and_url(image_obj, g.current_user)
        if response.get("error") is not None:
            return bad_request(response["error"])
        image_url = response["image_url"]
        image_id = response["image_id"]
        return jsonify(
            message="Upload Success",
            image_url=image_url,
            image_id=image_id
        ), 201

    def delete(self, image_id):
        image = Image.query.get_or_404(image_id)
        image.delete()
        return "", 204
