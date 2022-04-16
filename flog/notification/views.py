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
    notifications = [n for n in Notification.query.with_parent(current_user)]
    return render_template("main/notifications.html", notifications=notifications)


@notification_bp.route("/read/all/", methods=["POST"])
@login_required
def read_all():
    for notification in current_user.notifications:
        db.session.delete(notification)
    db.session.commit()
    flash(_("All notifications are read."), "green")
    return redirect_back()
