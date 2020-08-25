"""
 models.py
 A python module for database storing
"""
import hashlib
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from flask_login.mixins import AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .extensions import login_manager
from .utils import slugify


class Post(db.Model):
    """
    A model for posts
    """
    __tablename__ = 'posts'
    # initialize columns
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(64), index=True)
    author = db.relationship('User', back_populates='posts')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    slug = db.Column(db.String(128))
    date = db.Column(db.String(64))
    content = db.Column(db.Text(2048))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self) -> str:
        return f'<Post {self.title}>'

    def delete(self):
        if self in db.session:
            db.session.delete(self)
            db.session.commit()


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer(), primary_key=True)
    body = db.Column(db.String(200))
    author = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Feedback {self.body[:10]}...>'

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


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
    email = db.Column(db.String(255))
    name = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', back_populates='author')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', back_populates='users')
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config['ADMIN_EMAIL_LIST']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return f"<User '{self.name}'>"

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm): return False

    def is_administrator(self): return False

login_manager.anonymous_user = AnonymousUser
