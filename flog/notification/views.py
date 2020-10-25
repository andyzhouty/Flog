"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import request, current_app, render_template, make_response, flash, abort
from flask_babel import _
from flask_login import login_required, current_user
from ..models import db, Notification
from ..utils import redirect_back
from . import notification_bp

@notification_bp.route('/')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NOTIFICATIONS_PER_PAGE']
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get('filter')
    if filter_rule == 'unread':
        notifications = notifications.filter_by(is_read=False)

    pagination = (notifications.order_by(Notification.timestamp.desc())
                               .paginate(page, per_page))
    notifications = pagination.items
    return render_template('main/notifications.html', pagination=pagination,
                           notifications=notifications)


@notification_bp.route('/read/<int:id>/', methods=['POST'])
@login_required
def read(id):
    notification = Notification.query.get_or_404(id)
    if notification.receiver != current_user:
        abort(403)
    notification.is_read = True
    db.session.add(notification)
    db.session.commit()
    return make_response(redirect_back())


@notification_bp.route('/read/all/', methods=['POST'])
@login_required
def read_all():
    for notification in current_user.notifications:
        notification.is_read = True
        db.session.add(notification)
    db.session.commit()
    flash(_('All notifications are read.'),  "success")
    return make_response(redirect_back())
