"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import url_for
from .models import db, Notification


def push_follow_notification(follower, receiver):
    """
    Push a notification when someone is followed by another user.
    """
    message = f""""
        User <a href="{url_for('user.user_profile', username=follower.username)}">
        {follower.username}</a> followed you."""
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(comment, receiver, page=1):
    """
    Push a notification when a post has a new comment or
    a comment is replied.
    """
    message = f"""
        <a href="{url_for('main.full_post', slug=comment.post.slug, author=comment.post.username, page=page)}">
        This post</a> has a new comment/reply.
    """
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, post, receiver):
    """Push a notifications when a post is collected."""
    message = f"""
        User <a href="{url_for('user.user_profile', username=collector.username)}">
        {collector.username}</a> collected your <a href="{post.url()}">post</a>
    """
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
