"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import (
    Length,
    EqualTo,
    Email,
    ValidationError,
    URL,
    Regexp,
)
from ..models import User

# l_message is short for 'length_message'
l_message = _l("Field must be between %(min)d and %(max)d characters long.")
e_message = _l("Invalid email.")
u_message = _l("Invalid url.")


class EditProfileForm(FlaskForm):
    username = StringField(
        _l("Username"),
        validators=[
            Length(0, 32),
            Regexp(
                r"^[A-Za-z]([A-Za-z0-9_\-.])*$",
                0,
                _l(
                    "Usernames must have only letters, numbers, dots, underscores or dashes"
                ),
            ),
        ],
    )
    name = StringField(_l("Real Name"), validators=[Length(0, 64, l_message)])
    location = StringField(_l("Location"), validators=[Length(0, 64, l_message)])
    about_me = TextAreaField(_l("About me"), validators=[Length(0, 300, l_message)])
    custom_avatar_url = StringField(_l("Avatar URL"), validators=[URL(True, u_message)])
    submit = SubmitField(_l("Submit"))


class PasswordChangeForm(FlaskForm):
    password = PasswordField(_l("New Password"))
    password_again = PasswordField(
        _l("Again"), validators=[EqualTo("password", _l("Passwords must match"))]
    )
    submit = SubmitField(_l("Submit"))


class ValidateEmailForm(FlaskForm):
    email = StringField(_l("Email"), validators=[Email(message=e_message)])
    submit = SubmitField(_l("Submit"))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).count() == 0:
            raise ValidationError(e_message)
