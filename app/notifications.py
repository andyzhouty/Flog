from flask import url_for

from .models import db, Notification


def push_follow_notification(follower, receiver):
    message = f""""
        User <a href="{url_for('user.user_profile', username=follower.username)}">
        {follower.username}</a> followed you."""
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(comment, receiver, page=1):
    message = f"""
        User <a href="{url_for('main.full_post', slug=comment.post.slug, page=page)}">
        This post</a> has a new comment/reply.
    """
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, post, receiver):
    message = f"""
        User <a href="{url_for('user.user_profile', username=collector.username)}">
        {collector.username}</a> collected your <a href="{post.url()}">post</a>
    """
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
