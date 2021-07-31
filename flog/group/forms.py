"""
MIT License
Copyright (c) 2021 Andy Zhou
"""
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    PasswordField,
)
from wtforms.validators import Length, DataRequired
from ..models import Group

dr_message = _l("Please fill out this field with valid values.")
l_message = _l("Field must be between %(min)d and %(max)d characters long.")


class GroupCreationForm(FlaskForm):
    group_name = StringField(
        _l("Group Name"), validators=[Length(max=128, message=l_message)]
    )
    private = BooleanField(_l("Private"))
    submit = SubmitField(_l("Submit"))


class GroupFindForm(FlaskForm):
    group_name = StringField(
        _l("Group Name"), validators=[DataRequired(message=dr_message)]
    )
    submit = SubmitField(_l("Submit"))

    def validate_group_name(self, field):
        if Group.query.filter_by(name=field.data).count() == 0:
            raise ValidationError(_l("No such group"))


class GroupInviteForm(FlaskForm):
    group_id = SelectField(_l("Group Name"), coerce=int)
    submit = SubmitField(_l("Submit"))

    def validate_group_id(self, field):
        if Group.query.get(field.data) is None:
            raise ValidationError(_l("No such group"))


class ManagerConfirmForm(FlaskForm):
    password = PasswordField(
        _l("Password"), validators=[DataRequired(message=dr_message)]
    )
    submit = SubmitField(_l("Submit"))
