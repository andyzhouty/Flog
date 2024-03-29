"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import hashlib
from datetime import datetime, timedelta
from djask.auth.abstract import AbstractUser
from djask.db.models import Model
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for, abort
from flask_login.mixins import AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class Item:
    def __init__(
        self,
        name: str = "",
        category: str = "",
        exp: int = 0,
        gradient_deg: str = "45deg, ",
        expires: int = 0,
        color: str = "",
        **kwargs,
    ):
        self.name = name
        self.category = category
        self.exp = 0 if not exp else exp
        self.price = 0
        self.expires = timedelta(days=expires)
        if category == "":
            self.style = ""
            self.text_style = "color: inherit;"
        if category == "Classic":
            self.style = f"background-color: {color};"
            self.text_style = f"color: {color};"
            self.price = 5 * (expires / 30) - 2 * (expires / 30 - 1) - 0.01
        elif category == "Rare" or category == "Leveled":
            # gradient color
            gradient = f"linear-gradient({gradient_deg}{color})"
            self.style = f"background-image: {gradient};"
            self.text_style = f"""
                background: {gradient};
                -webkit-background-clip: text;
                color: transparent;
            """
            if category == "Rare":
                self.price = 9 * (expires / 30) - 2 * (expires / 30 - 1) - 0.01
        if "price" in kwargs.keys():
            self.price = kwargs["price"]


def items(id: int, mode="get") -> Item:
    item_list = (
        Item(category=""),
        Item(
            name="Rose",
            expires=30,
            color="#DE2344",
            category="Classic",
        ),
        Item(
            name="Orange",
            expires=30,
            color="#FE9A2E",
            category="Classic",
        ),
        Item(
            name="Sun",
            expires=30,
            color="#EBBC34",
            category="Classic",
        ),
        Item(
            name="Mint",
            expires=30,
            color="#2EFE9A",
            category="Classic",
        ),
        Item(
            name="Copper 2+",
            expires=30,
            exp=100,
            color="#2E64FE",
            category="Classic",
        ),
        Item(
            name="Violet",
            expires=30,
            color="#7401DF",
            category="Classic",
        ),
        Item(
            name="Fire",
            expires=30,
            color="#8000FF, #FE2E64, #FE9A2E",
            category="Rare",
        ),
        Item(
            name="Frozen",
            expires=30,
            color="#5882FA, #81F7F3",
            category="Rare",
        ),
        Item(
            name="Shore",
            expires=30,
            color="#04B486, #04B486, #F2F5A9",
            category="Rare",
        ),
        Item(
            name="Aurora",
            expires=30,
            color="#08088A, #04B486",
            category="Rare",
        ),
        Item(
            name="Sweet",
            expires=30,
            color="#F5A9D0, #BE81F7",
            category="Rare",
        ),
        Item(
            name="Helium",
            expires=30,
            color="#FF8000, #FF8000, #F6E3CE, #FF8000, #FF8000",
            gradient_deg="",
            category="Rare",
        ),
        Item(
            name="Rainbow",
            expires=30,
            color="#FFFF00, #FF00FF, #00FFFF",
            category="Rare",
        ),
        Item(
            name="Seven",
            expires=99999,
            color="#00FFBF, #2E64FE",
            exp=1100,
            category="Leveled",
        ),
        Item(
            name="Crown",
            expires=99999,
            exp=2500,
            color="#4000FF, #DF01A5",
            category="Leveled",
        ),
        Item(
            name="Black Sea",
            expires=99999,
            exp=3100,
            color="#2CD8D5, #6B8DD6, #8E37D7",
            gradient_deg="-225deg, ",
            category="Leveled",
            price=16.66,
        ),
        Item(
            name="Sky Five",
            expires=99999,
            exp=5500,
            color="#D4FFEC 0%, #57F2CC 48%, #4596FB 100%",
            gradient_deg="-225deg, ",
            category="Leveled",
            price=16.66,
        ),
        Item(
            name="Amour",
            expires=99999,
            exp=1500,
            color="#f77062, #fe5196",
            gradient_deg="to top, ",
            category="Leveled",
        ),
        Item(
            name="Harmony",
            expires=30,
            exp=0,
            color="#3D4E81 0%, #5753C9 48%, #6E7FF3 100%",
            gradient_deg="-225deg, ",
            category="Rare",
        ),
        Item(
            name="Phoenix",
            expires=30,
            exp=0,
            color="#f83600, #f9d423",
            gradient_deg="to right, ",
            category="Rare",
        ),
        Item(
            name="Life",
            expires=60,
            exp=0,
            color="#43e97b, #38f9d7",
            gradient_deg="to right, ",
            category="Rare",
        ),
        Item(
            name="Beach",
            expires=60,
            exp=0,
            color="#4facfe, #00f2fe",
            gradient_deg="to right, ",
            category="Rare",
        ),
    )
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


class Belong(Model):
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


class Post(Model):
    """
    A model for posts
    """

    # initialize columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    author = db.relationship("User", back_populates="posts")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", back_populates="post")
    content = db.Column(db.UnicodeText)
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    columns = db.relationship(
        "Column", secondary=column_post_table, back_populates="posts"
    )
    coins = db.Column(db.Integer, default=0)
    coiners = db.relationship(
        "User", secondary=coin_table, back_populates="coined_posts"
    )

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    @property
    def picked(self):
        return self.coins >= current_app.config["HOT_POST_COIN"]

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def url(self):
        return url_for("main.full_post", id=self.id, _external=True)

    def approve_url(self, column_id):
        return url_for(
            "main.approve_column", post_id=self.id, column_id=column_id, _external=True
        )

    def add_coin(self, coin_num: int, current_user):
        if coin_num not in (
            1,
            2,
        ):
            return "Invalid coin!"
        if self.author == current_user:  # pragma: no cover
            return "You can't coin yourself."
        if self in current_user.coined_posts:
            return "Invalid coin!"
        amount = coin_num
        if current_user.coins < amount:
            return "Not enough coins."
        current_user.coined_posts.append(self)
        current_user.coins -= amount
        current_user.experience += amount * 10
        self.coins += amount
        if self.author:
            self.author.coins += amount / 4
            self.author.experience += amount * 10
        db.session.commit()


class Column(Model):
    name = db.Column(db.String(128), unique=True)
    posts = db.relationship(
        "Post", secondary=column_post_table, back_populates="columns"
    )
    author = db.relationship("User", back_populates="columns")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def coins(self):
        return sum([post.coins for post in self.posts])

    @property
    def topped(self):
        return self.coins() >= current_app.config["HOT_COLUMN_COIN"]

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def url(self):
        return url_for("main.view_column", id=self.id, _external=True)

    def approve_url(self, post_id):
        return url_for(
            "main.approve_post", post_id=post_id, column_id=self.id, _external=True
        )


class Comment(Model):
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


class Notification(Model):
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


class Image(Model):
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


class Group(Model):
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


class Message(Model):
    body = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="messages")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="sent_messages")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


Collect = db.Table(
    "collect",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class User(AbstractUser, Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship("Post", back_populates="author")
    avatar_hash = db.Column(db.String(32))

    locked = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    collections = db.relationship(
        "Post", secondary=Collect, backref=db.backref("collectors")
    )

    locale = db.Column(db.String(16))

    columns = db.relationship("Column", back_populates="author")

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

    clicks = db.Column(db.Integer(), default=0)
    clicks_today = db.Column(db.Integer(), default=0)

    default_status = db.Column(db.String(64), default="online")
    # online, idle, focus, offline

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return f"<User '{self.username}'>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_administrator(self):
        return self.is_admin

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def can(self, perm) -> bool:
        return not self.locked

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
        self.coins = self.coins or 3.0  # maybe this account is processed
        if now - last_seen_day >= timedelta(days=1):
            self.coins += 1
            self.clicks_today = 0
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
            self.collections.append(post)
            db.session.commit()

    def uncollect(self, post):
        if post in self.collections:
            self.collections.remove(post)
            db.session.commit()

    def is_collecting(self, post):
        return post in self.collections

    def profile_url(self):
        return url_for("user.profile", username=self.username)

    def join_group(self, group) -> None:
        self.groups.append(group)
        db.session.add(self)
        db.session.add(group)
        db.session.commit()

    def in_group(self, group) -> bool:
        return self in group.members

    def lock(self):
        self.locked = True
        db.session.commit()

    def unlock(self):
        self.locked = False
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
        style = items(self.avatar_style_id).style
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style.format(size / 160)
        return ""

    def load_username_style(self):
        if self.avatar_style_id is None:
            self.avatar_style_id = 0
            db.session.commit()
        style = items(self.avatar_style_id).text_style
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style
        return ""

    def word_count(self):
        return sum([len(post.content) for post in self.posts])

    def get_alpha(self):
        def _get_recp(user):
            return [
                post
                for post in user.posts
                if (datetime.utcnow() - post.timestamp < timedelta(days=21))
            ]

        def _get_recc(user):
            return [
                comment
                for comment in user.comments
                if (datetime.utcnow() - comment.timestamp < timedelta(days=21))
            ]

        posts, comments = _get_recp(user=self), _get_recc(user=self)
        v5 = (
            (True if self.name else False)
            + (True if self.location else False)
            + (len(self.about_me or "hello world") >= 20)
        ) / 3

        def _get_recp_count(user):
            return sum([len(p.content) for p in _get_recp(user)])

        def _get_recc_count(user):
            return sum([len(c.body) for c in _get_recc(user)])

        def _get_recp_coins(user):
            return sum([p.coins for p in _get_recp(user)])

        def _get_recn(user):
            return [
                post
                for post in user.coined_posts
                if (datetime.utcnow() - post.timestamp < timedelta(40))
            ]

        def _get_recn_cc(user):
            return sum([p.coins for p in _get_recn(user)])

        pc, cc, tc, tc_ = (
            _get_recp_count(self),
            _get_recc_count(self),
            _get_recp_coins(self),
            _get_recn_cc(self),
        )
        try:
            v1 = pc / max([_get_recp_count(user) for user in User.query.all()])
        except ZeroDivisionError:
            v1 = 0
        try:
            v2 = cc / max([_get_recc_count(user) for user in User.query.all()])
        except ZeroDivisionError:
            v2 = 0
        try:
            v3 = tc / max([_get_recp_coins(user) for user in User.query.all()])
        except ZeroDivisionError:
            v3 = 0
        try:
            v4 = tc_ / max([_get_recn_cc(user) for user in User.query.all()])
        except ZeroDivisionError:
            v4 = 0

        pi = 3.141592653589793
        s2 = 1.4142135623730951
        return (
            (v1 * pi / 2 + v2 * pi / 2 + v3 * pi / 2 + v4 * pi / 4 + v5 * pi / 4)
            * 100
            / (4 * s2)
        ).__round__(2)

    def ping_update_ai(self):
        now = datetime.utcnow()
        sl = datetime.utcfromtimestamp(self.last_update) or datetime(
            2000, 1, 1, 0, 0, 0, 0
        )
        if now >= datetime(
            year=sl.year, month=sl.month, day=sl.day, hour=(sl.hour // 12 + 1) * 12
        ):
            self.alpha_index = self.get_alpha()
            self.last_update = now

    def post_count(self):
        return len([p for p in self.posts])

    def post_coins(self):
        return sum([post.coins for post in self.posts])

    def post_collects(self):
        return sum([len(post.collectors) for post in self.posts])


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    @property
    def id(self):
        return -1

    @property
    def is_admin(self):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

from .db_events import *  # noqa
