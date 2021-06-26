"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask_babel import _
from flask import url_for
from .models import db, Notification


def push_follow_notification(follower, receiver):
    """
    Push a notification when someone is followed by another user.
    """
    message = _(
        """User <a href="{0}">{1}</a> followed you.""".format(
            url_for("user.profile", username=follower.username), follower.username
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(comment, receiver, page=1):
    """
    Push a notification when a post has a new comment or
    a comment is replied.
    """
    message = _(
        """<a href="{0}">This post</a> has a new comment/reply.""".format(
            url_for("main.full_post", id=comment.post.id, page=page)
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, post, receiver):
    """Push a notification when a post is collected."""
    message = _(
        """User <a href="{0}">{1}</a> collected your <a href="{2}">post</a>""".format(
            url_for("user.profile", username=collector.username),
            collector.username,
            post.url(),
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_group_join_notification(joiner, group, receiver):
    """Push a notification to the manager of a group when another user wants to join it."""
    message = _(
        """User <a href="{0}">{1}</a> wants to join your group {2}.
                    Click <a href="{3}">Here</a> to approve.""".format(
            joiner.profile_url(),
            joiner.username,
            group.name,
            group.join_url(user_id=joiner.id),
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_group_invite_notification(inviter, group, receiver):
    """Push a notfication to the invited user."""
    message = _(
        """User <a href="{0}">{1}</a> invited you to group {2}.
           Click <a href="{3}">Here</a> to join it.""".format(
            inviter.profile_url(), inviter.username, group.name, group.join_url()
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()


def push_new_message_notification(sender, receiver, group):
    message = _(
        """<a href="{}">{}</a> send a message in group {}""".format(
            sender.profile_url(), sender.username, group.name
        )
    )
    notification = Notification(message=message, receiver=receiver, is_read=False)
    db.session.add(notification)
    db.session.commit()
