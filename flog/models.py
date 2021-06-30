"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import hashlib
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin
from flask_login.mixins import AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

group_user_table = db.Table(
    "group_user",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
)
column_post_table = db.Table(
    "column_post",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("column_id", db.Integer, db.ForeignKey("column.id")),
)


class Collect(db.Model):
    """Collect Model"""

    collector_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    collected_id = db.Column(db.Integer(), db.ForeignKey("post.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collector = db.relationship("User", back_populates="collections", lazy="joined")
    collected = db.relationship("Post", back_populates="collectors", lazy="joined")


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship(
        "User", foreign_keys=[follower_id], back_populates="following", lazy="joined"
    )
    followed = db.relationship(
        "User", foreign_keys=[followed_id], back_populates="followers", lazy="joined"
    )

    def __repr__(self):
        return f"<Follow follower: '{self.follower}' following: '{self.followed}'"


class Post(db.Model):
    """
    A model for posts
    """

    # initialize columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    author = db.relationship("User", back_populates="posts")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    collectors = db.relationship("Collect", back_populates="collected", cascade="all")
    comments = db.relationship("Comment", back_populates="post")
    content = db.Column(db.Text)
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    columns = db.relationship(
        "Column", secondary=column_post_table, back_populates="posts"
    )

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    def delete(self):
        if self in db.session:
            db.session.delete(self)
            db.session.commit()

    def url(self):
        return url_for("main.full_post", id=self.id, _external=True)


class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    posts = db.relationship(
        "Post", secondary=column_post_table, back_populates="columns"
    )
    author = db.relationship("User", back_populates="columns")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def delete(self):
        if self in db.session:
            db.session.delete(self)
            db.session.commit()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    replies = db.relationship("Comment", back_populates="replied", cascade="all")
    replied = db.relationship("Comment", back_populates="replies", remote_side=[id])

    def delete(self):
        """Delete comment"""
        db.session.delete(self)
        db.session.commit()


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="feedbacks")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Feedback {self.body[:10]}...>"

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver = db.relationship("User", back_populates="notifications")

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(512), unique=True)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="images")
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def url(self) -> str:
        return url_for("image.uploaded_files", filename=self.filename)

    def path(self) -> str:
        return os.path.join(current_app.config["UPLOAD_DIRECTORY"], self.filename)

    def toggle_visibility(self) -> None:
        self.private = not self.private
        db.session.commit()

    def delete(self) -> None:
        os.remove(self.path())
        db.session.delete(self)
        db.session.commit()


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    members = db.relationship(
        "User", secondary=group_user_table, back_populates="groups"
    )
    manager = db.relationship("User", back_populates="managed_groups")
    manager_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    messages = db.relationship("Message", back_populates="group")
    private = db.Column(db.Boolean, default=False)

    def generate_join_token(self, expiration: int = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"group_id": self.id}).decode("utf-8")

    def join_url(self, **kwargs):
        return url_for("group.join", token=self.generate_join_token(), **kwargs)

    def info_url(self):
        return url_for("group.info", id=self.id)

    @staticmethod
    def verify_join_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return None
        return Group.query.get(data.get("group_id"))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="messages")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="sent_messages")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", back_populates="role")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f"<Role: {self.name}>"

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        """
        Check if a single permission is in a combined permission
        """
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            "Moderator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
            ],
            "Administrator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
                Permission.ADMIN,
            ],
            "LOCKED": [Permission.FOLLOW],
        }
        default_role = "User"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship("Post", back_populates="author")
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", back_populates="users")
    feedbacks = db.relationship("Feedback", back_populates="author")
    avatar_hash = db.Column(db.String(32))

    locked = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    collections = db.relationship("Collect", back_populates="collector", cascade="all")
    locale = db.Column(db.String(16))

    columns = db.relationship("Column", back_populates="author")

    following = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        back_populates="follower",
        lazy="dynamic",
        cascade="all",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        back_populates="followed",
        lazy="dynamic",
        cascade="all",
    )

    comments = db.relationship("Comment", back_populates="author", cascade="all")
    notifications = db.relationship(
        "Notification", back_populates="receiver", cascade="all"
    )
    images = db.relationship("Image", back_populates="author", cascade="all")

    groups = db.relationship(
        "Group", secondary=group_user_table, back_populates="members"
    )
    managed_groups = db.relationship("Group", back_populates="manager")

    custom_avatar_url = db.Column(db.String(128), default="")

    sent_messages = db.relationship("Message", back_populates="author")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["FLOG_ADMIN_EMAIL"]:
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        self.follow(self)

    def __repr__(self):
        return f"<User '{self.username}'>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def can(self, perm) -> bool:
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

    def avatar_url(self, size=30, default="identicon", rating="g"):
        if self.custom_avatar_url:
            return self.custom_avatar_url
        url = "https://sdn.geekzu.org/avatar"  # use gravatar cdn by geekzu.cn
        hash = self.avatar_hash or self.gravatar_hash()
        return f"{url}/{hash}?s={size}&d={default}&r={rating}"

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    @staticmethod
    def from_confirmation_token(token: str):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return None
        return User.query.get(data.get("confirm"))

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def gen_api_auth_token(self, expiration=3600 * 24 * 365):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"id": self.id}).decode("ascii")

    @staticmethod
    def verify_auth_token_api(token: str):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("ascii"))
        except:
            return None
        return User.query.get(data.get("id"))

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def collect(self, post):
        if not self.is_collecting(post):
            collect = Collect(collector=self, collected=post)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, post):
        collect = (
            Collect.query.with_parent(self).filter_by(collected_id=post.id).first()
        )
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, post):
        return (
            Collect.query.with_parent(self).filter_by(collected_id=post.id).first()
        ) is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None

    def profile_url(self):
        return url_for("user.profile", username=self.username)

    def join_group(self, group) -> None:
        self.groups.append(group)
        db.session.add(self)
        db.session.add(group)
        db.session.commit()

    def in_group(self, group) -> bool:
        return self in group.members

    def lock(self) -> bool:
        self.locked = True
        self.role = Role.query.filter_by(name="LOCKED").first()
        db.session.commit()

    def unlock(self) -> bool:
        self.locked = False
        self.role = Role.query.filter_by(name="User").first()
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

from .db_events import *  # noqa
