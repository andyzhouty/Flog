"""
MIT License
Copyright (c) 2021 Andy Zhou
"""
from flask import render_template, flash, abort, request
from flask_babel import _
from flask_login import login_required, current_user
from . import group_bp
from .forms import GroupCreationForm, GroupFindForm, GroupInviteForm
from ..models import db, Group, User, Message
from ..utils import redirect_back
from ..notifications import push_group_join_notification, push_group_invite_notification


@group_bp.route("/create/", methods=["GET", "POST"])
@login_required
def create():
    form = GroupCreationForm()
    if form.validate_on_submit():
        group = Group(name=form.group_name.data)
        current_user.join_group(group)
        group.manager = current_user
        db.session.commit()
        flash(_("Created group {0}.".format(group.name)))
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
        flash(_("Joined group {0}".format(group.name)))
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
        push_group_invite_notification(current_user, group, invited_user)
        flash(_("Notification sent to user {0}".format(invited_user.username)))
        return redirect_back()
    return render_template("group/invite.html", form=form)


@group_bp.route("/info/<int:id>/", methods=["GET", "POST"])
@login_required
def group_info(id: int):
    group = Group.query.get_or_404(id)
    return render_template("group/info.html", group=group)


@group_bp.route("/<int:id>/discussion", methods=["GET", "POST"])
def discussion(id: int):
    group = Group.query.get_or_404(id)
    if current_user not in group.members:
        abort(403)
    if request.method == "POST":
        body = request.form.get("body")
        message = Message(author=current_user, body=body)
        group.messages.append(message)
        db.session.commit()
    return render_template("group/discussion.html", group=group)
