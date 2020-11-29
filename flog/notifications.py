"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask_babel import lazy_gettext as _l
from flask import url_for
from .models import db, Notification


def push_follow_notification(follower, receiver):
    """
    Push a notification when someone is followed by another user.
    """
    message = _l("""User <a href="{0}">{1}</a> followed you.""".
                 format(url_for('user.user_profile', username=follower.username),
                        follower.username)
                 )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(comment, receiver, page=1):
    """
    Push a notification when a post has a new comment or
    a comment is replied.
    """
    message = _l("""<a href="{0}">This post</a> has a new comment/reply."""
                 .format(url_for('main.full_post', id=comment.post.id, page=page))
                 )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, post, receiver):
    """Push a notifications when a post is collected."""
    message = _l("""User <a href="{0}">{1}</a> collected your <a href="{2}">post</a>"""
                 .format(url_for('user.user_profile', username=collector.username),
                         collector.username, post.url())
                 )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()
