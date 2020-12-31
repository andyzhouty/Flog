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
    'group_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Collect(db.Model):
    """Collect Model"""
    collector_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    collected_id = db.Column(db.Integer(), db.ForeignKey('post.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collector = db.relationship('User', back_populates='collections', lazy='joined')
    collected = db.relationship('Post', back_populates='collectors', lazy='joined')


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id],
                               back_populates='following', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id],
                               back_populates='followers', lazy='joined')


class Post(db.Model):
    """
    A model for posts
    """
    # initialize columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    author = db.relationship('User', back_populates='posts')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    collectors = db.relationship(
        'Collect',
        back_populates='collected',
        cascade='all'
    )
    comments = db.relationship('Comment', back_populates='post')
    content = db.Column(db.Text)
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f'<Post {self.title}>'

    def delete(self):
        if self in db.session:
            db.session.delete(self)
            db.session.commit()

    def url(self):
        return url_for('main.full_post', id=self.id, _external=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    def delete(self):
        """Delete comment"""
        db.session.delete(self)
        db.session.commit()


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='feedbacks')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Feedback {self.body[:10]}...>'

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', back_populates='notifications')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(512), unique=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='images')
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def url(self) -> str:
        return url_for('image.uploaded_files', filename=self.filename)

    def path(self) -> str:
        return os.path.join(current_app.config['UPLOAD_DIRECTORY'], self.filename)

    def toggle_visibility(self) -> None:
        self.private = not self.private
        db.session.commit()


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    members = db.relationship(
        'User',
        secondary=group_user_table,
        back_populates='groups'
    )
    manager = db.relationship('User', back_populates='managed_groups')
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def generate_join_token(self, expiration: int=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'group_id': self.id}).decode('utf-8')

    def join_url(self):
        return url_for('user.join_group', token=self.generate_join_token())

    @staticmethod
    def verify_join_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None
        return Group.query.get(data.get('group_id'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', back_populates='role')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return self.name

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
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', back_populates='author')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', back_populates='users')
    feedbacks = db.relationship('Feedback', back_populates='author')
    avatar_hash = db.Column(db.String(32))

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    collections = db.relationship(
        'Collect',
        back_populates='collector',
        cascade='all'
    )
    locale = db.Column(db.String(16))

    following = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                back_populates='follower', lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                back_populates='followed', lazy='dynamic', cascade='all')

    comments = db.relationship('Comment', back_populates='author')
    notifications = db.relationship('Notification', back_populates='receiver', cascade='all')
    images = db.relationship('Image', back_populates='author', cascade='all')

    groups = db.relationship(
        'Group',
        secondary=group_user_table,
        back_populates='members'
    )
    managed_groups = db.relationship('Group', back_populates='manager')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLOG_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
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
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://cdn.v2ex.com/gravatar/'
        hash = self.avatar_hash or self.gravatar_hash()
        return f"{url}/{hash}?s={size}&d={default}&r={rating}"

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def gen_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token: str):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('ascii'))
        except:
            return None
        return User.query.get(data.get('id'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def collect(self, post):
        if not self.is_collecting(post):
            collect = Collect(collector=self, collected=post)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, post):
        collect = Collect.query.with_parent(self).filter_by(collected_id=post.id).first()
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
        return url_for('user.user_profile', username=self.username)

    def join_group(self, group) -> None:
        self.groups.append(group)
        db.session.add(self)
        db.session.add(group)
        db.session.commit()

    def in_group(self, group) -> bool:
        return (self in group.members)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm): return False

    def is_administrator(self): return False


login_manager.anonymous_user = AnonymousUser
