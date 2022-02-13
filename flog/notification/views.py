"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import request, current_app, render_template, flash, abort
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
    # delete notifications directly after reading it
    notification = Notification.query.get_or_404(id)
    if notification.receiver != current_user:
        abort(403)
    db.session.delete(notification)
    db.session.commit()
    return redirect_back()


@notification_bp.route("/read/all/", methods=["POST"])
@login_required
def read_all():
    for notification in current_user.notifications:
        db.session.delete(notification)
    db.session.commit()
    flash(_("All notifications are read."), "green")
    return redirect_back()
