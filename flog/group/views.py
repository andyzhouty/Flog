"""
MIT License
Copyright (c) 2021 Andy Zhou
"""
from flask import render_template, flash, abort, request
from flask_babel import _
from flask_login import login_required, current_user
from . import group_bp
from .forms import GroupCreationForm, GroupFindForm, GroupInviteForm, ManagerConfirmForm
from ..models import db, Group, User, Message
from ..utils import redirect_back
from ..notifications import (
    push_group_join_notification,
    push_group_invite_notification,
    push_new_message_notification,
)


@group_bp.route("/all/")
@login_required
def all():
    return render_template("user/groups.html", groups=Group.query.filter(~Group.private).all())


@group_bp.route("/create/", methods=["GET", "POST"])
@login_required
def create():
    form = GroupCreationForm()
    if form.validate_on_submit():
        group = Group(name=form.group_name.data, private=form.private.data)
        current_user.join_group(group)
        group.manager = current_user
        db.session.commit()
        flash(_("Created group %(name)s", name=group.name))
        return redirect_back()
    return render_template("group/create.html", form=form)


@group_bp.route("/find/", methods=["GET", "POST"])
@login_required
def explore():
    form = GroupFindForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(name=form.group_name.data).first_or_404()
        push_group_join_notification(
            joiner=current_user, group=group, receiver=group.manager
        )
        flash(
            _(
                """We have sent a notification to the manager of the group.
                All you should do is to wait the manager's reply."""
            )
        )
        return redirect_back()
    return render_template("group/find.html", form=form)


@group_bp.route("/join/<token>/")
@login_required
def join(token):
    group = Group.verify_join_token(token)
    if group is None:
        abort(404)
    else:
        user_id = request.args.get("user_id", type=int)
        if user_id is None:
            user = current_user
        else:
            user = User.query.get(user_id)
        user.join_group(group)
        flash(_("Joined group %(name)s", name=group.name))
        return redirect_back()


@group_bp.route("/invite/<int:user_id>/", methods=["GET", "POST"])
@login_required
def invite_user(user_id: int):
    form = GroupInviteForm()
    form.group_id.choices = [
        (g.id, g.name)
        for g in Group.query.filter_by(manager=current_user).order_by("name")
    ]
    if len(form.group_id.choices) == 0:
        flash(
            _(
                """
            You are not managing any groups.
            Please create a group first to invite other users.
        """
            )
        )
        return redirect_back()
    if form.validate_on_submit():
        group = Group.query.get_or_404(form.group_id.data)
        invited_user = User.query.get_or_404(user_id)
        push_group_invite_notification(current_user, invited_user, group)
        flash(
            _("Notification sent to user %(username)s", username=invited_user.username)
        )
        return redirect_back()
    return render_template("group/invite.html", form=form)


@group_bp.route("/<int:id>/info/", methods=["GET", "POST"])
@login_required
def info(id: int):
    group = Group.query.get_or_404(id)
    if group.private and current_user not in group.members:
        abort(403)
    return render_template("group/info.html", group=group)


@group_bp.route("/<int:id>/discussion/", methods=["GET", "POST"])
@login_required
def discussion(id: int):
    group = Group.query.get_or_404(id)
    if current_user not in group.members:
        abort(403)
    if request.method == "POST":
        body = request.form.get("body")
        message = Message(author=current_user, body=body)
        group.messages.append(message)
        db.session.commit()
        for member in group.members:
            if member != current_user:
                push_new_message_notification(current_user, member, group)
    return render_template("group/discussion.html", group=group)


@group_bp.route("/<int:group_id>/kick/<int:user_id>/", methods=["POST"])
@login_required
def kick_out(group_id: int, user_id: int):
    group = Group.query.get_or_404(group_id)
    if current_user != group.manager:
        abort(403)
    user = User.query.get_or_404(user_id)
    group.members.remove(user)
    db.session.commit()
    return redirect_back()


@group_bp.route("/<int:group_id>/set-manager/<int:user_id>/", methods=["GET", "POST"])
@login_required
def set_manager(group_id: int, user_id: int):
    group = Group.query.get_or_404(group_id)
    if current_user != group.manager:
        abort(403)
    form = ManagerConfirmForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            abort(403)
        user = User.query.get_or_404(user_id)
        group.manager = user
        db.session.commit()
        return redirect_back()
    return render_template("group/set_manager.html", form=form)
