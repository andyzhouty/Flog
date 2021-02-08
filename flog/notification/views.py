"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import request, current_app, render_template, flash, abort, redirect, url_for
from flask_babel import _
from flask_login import login_required, current_user
from ..models import db, Notification
from ..utils import redirect_back
from . import notification_bp


@notification_bp.route("/")
@login_required
def show():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["NOTIFICATIONS_PER_PAGE"]
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get("filter")
    if filter_rule == "unread":
        notifications = notifications.filter_by(is_read=False)

    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(
        page, per_page
    )
    notifications = pagination.items
    return render_template(
        "main/notifications.html", pagination=pagination, notifications=notifications
    )


@notification_bp.route("/read/<int:id>/", methods=["POST"])
@login_required
def read(id: int):
    notification = Notification.query.get_or_404(id)
    if notification.receiver != current_user:
        abort(403)
    notification.is_read = True
    db.session.add(notification)
    db.session.commit()
    return redirect_back()


@notification_bp.route("/read/all/", methods=["POST"])
@login_required
def read_all():
    for notification in current_user.notifications:
        notification.is_read = True
        db.session.add(notification)
    db.session.commit()
    flash(_("All notifications are read."), "success")
    return redirect_back()


@notification_bp.route("/delete/<int:id>/", methods=["POST"])
@login_required
def delete(id: int):
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    flash(_("Notification Deleted"))
    return redirect(url_for(".show"))


@notification_bp.route("/delete/all/", methods=["POST"])
@login_required
def delete_all():
    notifications = Notification.query.filter_by(receiver=current_user).all()
    for notification in notifications:
        notification.delete()
    flash(_("All your notifications are deleted."))
    return redirect_back(".show")
