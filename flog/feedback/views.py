"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import flash, render_template, current_app, url_for, redirect
from flask_login import login_required
from flask_login.utils import current_user
from flask_babel import _
from ..emails import send_email
from ..models import Feedback, db
from .forms import FeedbackForm
from . import feedback_bp


@feedback_bp.route("/", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    feedbacks = Feedback.query.all()
    if form.validate_on_submit():
        body = form.body.data
        message = Feedback(body=body, author=current_user)
        db.session.add(message)
        db.session.commit()
        recipients = [current_app.config["FLOG_ADMIN_EMAIL"]]
        send_email(
            recipients=recipients,
            subject="A new feedback was added!",
            template="feedback/feedback_notification",
            **dict(author=current_user.username, content=body)
        )
        flash(_("Your feedback has been sent to the admins!"), "success")
        return redirect(url_for("feedback.feedback"))
    return render_template("feedback/feedback.html", form=form, feedbacks=feedbacks)
