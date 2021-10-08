"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import hashlib
from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin
from flask_login.mixins import AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


def items(id: int, mode="get"):
    item_list = {
        0: {"style": "", "text_style": "color: inherit;"},
        1: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 0,
            "style": "background-color: #DE2344;",
            "text_style": "color: #DE2344;",
            "name": "Rose",
            "class": "Classic",
        },
        2: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 0,
            "style": "background-color: #FE9A2E;",
            "text_style": "color: #FE9A2E;",
            "name": "Orange",
            "class": "Classic",
        },
        3: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 0,
            "style": "background-color: #EBBC34;",
            "text_style": "color: #EBBC34;",
            "name": "Sun",
            "class": "Classic",
        },
        4: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 0,
            "style": "background-color: #2EFE9A;",
            "text_style": "color: #2EFE9A;",
            "name": "Mint",
            "class": "Classic",
        },
        5: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 100,
            "style": "background-color: #2E64FE;",
            "text_style": "color: #2E64FE;",
            "name": "Copper 2+",
            "class": "Classic",
        },
        6: {
            "expires": timedelta(days=30),
            "price": 7.99,
            "exp": 0,
            "style": "background-color: #7401DF;",
            "text_style": "color: #7401DF;",
            "name": "Violet",
            "class": "Classic",
        },
        7: {
            "expires": timedelta(days=30),
            "price": 14.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(45deg, #8000FF, #FE2E64, #FE9A2E);
            """,
            "text_style": """
                background: linear-gradient(45deg, #8000FF, #FE2E64, #FE9A2E);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Fire",
            "class": "Rare",
        },
        8: {
            "expires": timedelta(days=30),
            "price": 14.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(45deg, #5882FA, #81F7F3);
            """,
            "text_style": """
                background: linear-gradient(45deg, #5882FA, #81F7F3);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Frozen",
            "class": "Rare",
        },
        9: {
            "expires": timedelta(days=30),
            "price": 14.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(45deg, #04B486, #04B486, #F2F5A9);
            """,
            "text_style": """
                background: linear-gradient(45deg, #04B486, #04B486, #F2F5A9);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Shore",
            "class": "Rare",
        },
        10: {
            "expires": timedelta(days=30),
            "price": 14.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(45deg, #08088A, #04B486);
            """,
            "text_style": """
                background: linear-gradient(45deg, #08088A, #04B486);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Aurora",
            "class": "Rare",
        },
        11: {
            "expires": timedelta(days=30),
            "price": 19.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(45deg, #F5A9D0, #BE81F7);
            """,
            "text_style": """
                background: linear-gradient(45deg, #F5A9D0, #BE81F7);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Sweet",
            "class": "Rare",
        },
        12: {
            "expires": timedelta(days=30),
            "price": 19.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(#FF8000, #FF8000, #F6E3CE, #FF8000, #FF8000);
            """,
            "text_style": """
                background: linear-gradient(#FF8000, #FF8000, #F6E3CE, #FF8000, #FF8000);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Helium",
            "class": "Rare",
        },
        13: {
            "expires": timedelta(days=30),
            "price": 19.99,
            "exp": 0,
            "style": """
                background-image: linear-gradient(#FFFF00, #FF00FF, #00FFFF);
            """,
            "text_style": """
                background: linear-gradient(#FFFF00, #FF00FF, #00FFFF);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Rainbow",
            "class": "Rare",
        },
        14: {
            "expires": timedelta(days=99999),
            "price": 0,
            "exp": 1100,
            "style": """
                background-image: linear-gradient(45deg, #00FFBF, #2E64FE);
            """,
            "text_style": """
                background: linear-gradient(45deg, #00FFBF, #2E64FE);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Seven",
            "class": "Leveled",
        },
        15: {
            "expires": timedelta(days=99999),
            "price": 0,
            "exp": 2500,
            "style": """
                background-image: linear-gradient(45deg, #4000FF, #DF01A5);
            """,
            "text_style": """
                background: linear-gradient(45deg, #4000FF, #DF01A5);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Crown",
            "class": "Leveled",
        },
        16: {
            "expires": timedelta(days=99999),
            "price": 0,
            "exp": 3100,
            "style": """
                background-image: linear-gradient(45deg, #2EFE2E, #0B614B);
            """,
            "text_style": """
                background: linear-gradient(45deg, #2EFE2E, #0B614B);
                -webkit-background-clip: text;
                color: transparent;
            """,
            "name": "Iron 2+",
            "class": "Leveled",
        },
    }
    return (
        item_list[id] if mode == "get" else (len(item_list) if mode == "len" else None)
    )


group_user_table = db.Table(
    "group_user",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    extend_existing=True,
)
column_post_table = db.Table(
    "column_post",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("column_id", db.Integer, db.ForeignKey("column.id")),
    extend_existing=True,
)
coin_table = db.Table(
    "coin_table",
    db.Column("owner_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    extend_existing=True,
)


class Belong(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    owner_id = db.Column(
        db.Integer(),
        db.ForeignKey("user.id"),
    )
    goods_id = db.Column(
        db.Integer(),
    )
    expires = db.Column(db.DateTime)

    owner = db.relationship("User", back_populates="belongings")

    def __str__(self):
        return f"<Belong relationship {self.goods_id} -> User {self.owner_id}>"

    def load_expiration_delta(self):
        delta = self.expires - datetime.utcnow()
        return delta


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
    content = db.Column(db.UnicodeText)
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    columns = db.relationship(
        "Column", secondary=column_post_table, back_populates="posts"
    )
    picked = db.Column(db.Boolean, default=False)
    coins = db.Column(db.Integer, default=0)
    coiners = db.relationship(
        "User", secondary=coin_table, back_populates="coined_posts"
    )

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def url(self):
        return url_for("main.full_post", id=self.id, _external=True)

    def approve_url(self, column_id):
        return url_for(
            "main.approve_column", post_id=self.id, column_id=column_id, _external=True
        )


class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    posts = db.relationship(
        "Post", secondary=column_post_table, back_populates="columns"
    )
    author = db.relationship("User", back_populates="columns")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    topped = db.Column(db.Boolean, default=False)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def url(self):
        return url_for("main.view_column", id=self.id, _external=True)

    def approve_url(self, post_id):
        return url_for(
            "main.approve_post", post_id=post_id, column_id=self.id, _external=True
        )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.UnicodeText)
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

    def push(self):
        db.session.add(self)
        db.session.commit()

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
        return url_for("image.uploaded_files", filename=self.filename, _external=True)

    def path(self) -> str:
        return os.path.join(current_app.config["UPLOAD_DIRECTORY"], self.filename)

    def toggle_visibility(self) -> None:
        self.private = not self.private
        db.session.commit()

    def delete(self) -> None:
        try:
            os.remove(self.path())
        except FileNotFoundError:
            pass
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

    def generate_join_token(self, expiration: int = 3600 * 24 * 30):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"group_id": self.id}).decode("utf-8")

    def join_url(self, **kwargs):
        return url_for("group.join", token=self.generate_join_token(), **kwargs)

    def info_url(self):
        return url_for("group.info", id=self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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

    coins = db.Column(db.Float, default=3)
    experience = db.Column(db.Integer, default=0)
    coined_posts = db.relationship(
        "Post", secondary=coin_table, back_populates="coiners"
    )

    belongings = db.relationship("Belong", back_populates="owner")

    avatar_style_id = db.Column(db.Integer(), default=0)

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

    def avatar_url(self, size=30):
        if self.custom_avatar_url:
            return self.custom_avatar_url
        url = "https://rice0208.pythonanywhere.com/silicon/v1"  # use silicon generator
        hash = self.avatar_hash or self.gravatar_hash()
        return f"{url}/{hash}?s={size}"

    def ping(self, force_time=None):
        now = datetime.utcnow() if force_time is None else force_time
        last_seen_day = datetime(
            self.last_seen.year, self.last_seen.month, self.last_seen.day
        )
        if now - last_seen_day >= timedelta(days=1):
            self.coins += 1
        self.last_seen = now
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

    def level(self) -> int:
        if self.experience < 100:
            return 1
        elif self.experience < 200:
            return 2
        elif self.experience < 350:
            return 3
        elif self.experience < 550:
            return 4
        elif self.experience < 800:
            return 5
        elif self.experience < 1100:
            return 6
        elif self.experience < 1500:
            return 7
        elif self.experience < 2500:
            return 8
        else:
            lv = 9
            while (lv - 8) * (lv - 7) * 100 + 2500 <= self.experience:
                lv += 1
            return lv

    def level_badge_link(self) -> str:
        lv = self.level()
        prefix = "https://img.shields.io/badge/Lv" + str(min(lv, 9)) + "%20"
        if lv <= 8:
            color = ""
            if lv == 1:
                color = "eee"
            elif lv == 2:
                color = "ff9"
            elif lv == 3:
                color = "afa"
            elif lv == 4:
                color = "5d5"
            elif lv == 5:
                color = "0dd"
            elif lv == 6:
                color = "00f"
            elif lv == 7:
                color = "da3"
            elif lv == 8:
                color = "f00"
            return prefix + "-" + color
        else:
            plus = lv - 9
            return prefix + "%2B" + str(plus) + "-808"

    def load_belongings(self):
        belongings = [
            item for item in self.belongings if item.expires > datetime.utcnow()
        ]
        return belongings

    def load_belongings_id(self):
        return [item.goods_id for item in self.load_belongings()]

    def load_avatar_style(self, size=36):
        if self.avatar_style_id is None:
            self.avatar_style_id = 0
            db.session.commit()
        style = items(self.avatar_style_id)["style"]
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style.format(size / 160)
        return ""

    def load_username_style(self):
        if self.avatar_style_id is None:
            self.avatar_style_id = 0
            db.session.commit()
        style = items(self.avatar_style_id)["text_style"]
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style
        return ""


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

from .db_events import *  # noqa
