"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.core import BooleanField, StringField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import Role, User

dr_message = _l("Please fill out this field.")
l_message = _l("Field must be between %(min)d and %(max)d characters long.")
e_message = _l("Invalid email.")


class EditProfileAdminForm(FlaskForm):
    email = StringField(
        _l("Email"),
        validators=[DataRequired(dr_message), Length(5, 64), Email(e_message)],
    )
    username = StringField(
        _l("Username"),
        validators=[
            DataRequired(dr_message),
            Length(1, 32),
            Regexp(
                r"^[A-Za-z][A-Za-z0-9_\-.]*$",
                0,
                _l(
                    "Usernames must have only letters, numbers, dots, underscores or dashes"
                ),
            ),
        ],
    )
    confirmed = BooleanField(_l("Confirmed"))
    role = SelectField(_l("Role"), coerce=int)
    name = StringField(_l("Real Name"), validators=[Length(0, 64, l_message)])
    location = StringField(_l("Location"), validators=[Length(0, 64, l_message)])
    about_me = TextAreaField(_l("About me"))
    submit = SubmitField(_l("Submit"))

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None and self.user != user:
            raise ValidationError(_l("Email already registered."))

    def validate_username(self, field):
        user = User.query.filter_by(name=field.data).first()
        if user is not None and self.user != user:
            raise ValidationError(_l("Username already in use."))
