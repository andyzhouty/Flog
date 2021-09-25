"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from functools import wraps
from flask_babel import _, force_locale, ngettext
from flask import url_for
from .models import Message, db, Notification


def with_receiver_locale(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if len(args) > 1:
            receiver = args[1]
        else:
            receiver = kwargs["receiver"]
        locale = ""
        if receiver is not None and receiver.locale is not None:
            locale = receiver.locale
        else:
            locale = "en_US"
        with force_locale(locale):
            return f(*args, **kwargs)

    return decorated_function


@with_receiver_locale
def push_follow_notification(follower, receiver):
    """
    Push a notification when someone is followed by another user.
    """
    message = _(
        """User <a href="%(profile_url)s">%(username)s</a> followed you.""",
        profile_url=url_for("user.profile", username=follower.username),
        username=follower.username,
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_comment_notification(comment, receiver, page=1):
    """
    Push a notification when a post has a new comment or
    a comment is replied.
    """
    message = _(
        """<a href="%(post_url)s">This post</a> has a new comment/reply.""",
        post_url=url_for("main.full_post", id=comment.post.id, page=page),
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_collect_notification(collector, receiver, post):
    """Push a notification when a post is collected."""
    message = _(
        """User <a href="%(profile_url)s">%(username)s</a> collected your <a href="%(post_url)s">post</a>""",
        profile_url=url_for("user.profile", username=collector.username),
        username=collector.username,
        post_url=post.url(),
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_group_join_notification(joiner, receiver, group):
    """Push a notification to the manager of a group when another user wants to join it."""
    message = _(
        """User <a href="%(profile_url)s">%(username)s</a> wants to join your group %(name)s.
                    Click <a href="%(join_url)s">Here</a> to approve.""",
        profile_url=joiner.profile_url(),
        username=joiner.username,
        name=group.name,
        join_url=group.join_url(user_id=joiner.id),
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_group_invite_notification(inviter, receiver, group):
    """Push a notification to the invited user."""
    message = _(
        """User <a href="%(profile_url)s">%(username)s</a> invited you to group %(name)s.
           Click <a href="%(join_url)s">Here</a> to join it.""",
        profile_url=inviter.profile_url(),
        username=inviter.username,
        name=group.name,
        join_url=group.join_url(user_id=receiver.id),
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_new_message_notification(sender, receiver, group):
    message = _(
        """<a href="%(profile_url)s">%(username)s</a> send a message in <a href="%(info_url)s">Group %(name)s</a>""",
        profile_url=sender.profile_url(),
        username=sender.username,
        info_url=group.info_url(),
        name=group.name,
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_coin_notification(sender, receiver, post, amount):
    message = ngettext(
        """<a href="%(profile_url)s">%(username)s</a> gives %(num)s coin to your post
           <a href="%(post_url)s">%(post_title)s</a>.""",
        """<a href="%(profile_url)s">%(username)s</a> gives %(num)s coins to your post
           <a href="%(post_url)s">%(post_title)s</a>.""",
        profile_url=sender.profile_url(),
        username=sender.username,
        post_url=post.url(),
        post_title=post.title,
        num=amount,
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_submitting_post_to_column_notification(sender, receiver, post, column):
    message = _(
        """<a href="%(profile_url)s">%(username)s</a> wanted to add post
           <a href="%(post_url)s">%(post_title)s</a> to
           <a href="%(column_url)s">&lt; Column %(column_name)s &lgt;</a>.
           Click <a href="%(approve_url)s">here</a> to approve.
           """,
        profile_url=sender.profile_url(),
        username=sender.username,
        post_url=post.url(),
        post_title=post.title,
        column_url=column.url(),
        column_name=column.name,
        approve_url=column.approve_url(post.id),
    )
    Notification(message=message, receiver=receiver).push()


@with_receiver_locale
def push_transposting_to_column_notification(sender, receiver, post, column):
    message = _(
        """<a href="%(profile_url)s">%(username)s</a> wanted to transpost your
           <a href="%(post_url)s">Post %(post_title)s</a> to
           <a href="%(column_url)s">&lt; Column %(column_name)s &lgt;</a>.
           Click <a href="%(approve_url)s">here</a> to approve""",
        profile_url=sender.profile_url(),
        username=sender.username,
        post_url=post.url(),
        post_title=post.title,
        column_url=column.url(),
        column_name=column.name,
        approve_url=post.approve_url(column.id),
    )
    Notification(message=message, receiver=receiver).push()
