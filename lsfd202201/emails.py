"""
@author: andy zhou
Copyright(c) all rights reserved 2020
"""
from flask_mail import Message
from flask import render_template
from .extensions import mail


def send_email(recipients: list,
               subject=None,
               template=None,
               **kwargs):
    msg = Message(
        subject=subject,
        recipients=recipients
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)  # No threading because it is unnecessary
