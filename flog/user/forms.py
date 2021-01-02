"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.fields.core import SelectField
from wtforms.validators import Length, EqualTo, Email, ValidationError
from ..models import User, Group

# l_message is short for 'length_message'
l_message = _l('Field must be between %(min)d and %(max)d characters long.')
e_message = _l('Invalid email.')


class EditProfileForm(FlaskForm):
    name = StringField(_l('Real Name'), validators=[Length(0, 64, l_message)])
    location = StringField(_l('Location'), validators=[Length(0, 64, l_message)])
    about_me = TextAreaField(_l('About me'), validators=[Length(0, 300, l_message)])
    submit = SubmitField(_l('Submit'))


class PasswordChangeForm(FlaskForm):
    password = PasswordField(_l('New Password'))
    password_again = PasswordField(_l('Again'), validators=[EqualTo('password', _l("Passwords must match"))])
    submit = SubmitField(_l('Submit'))


class ValidateEmailForm(FlaskForm):
    email = StringField(_l('Email'), validators=[Email(message=e_message)])
    submit = SubmitField(_l('Submit'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).count() == 0:
            raise ValidationError(e_message)


class GroupCreationForm(FlaskForm):
    group_name = StringField(_l('Group Name'), validators=[Length(max=128, message=l_message)])
    submit = SubmitField(_l('Submit'))


class GroupFindForm(FlaskForm):
    group_name = StringField(_l('Group Name'))
    submit = SubmitField(_l('Submit'))

    def validate_group_name(self, field):
        if Group.query.filter_by(name=field.data).count() == 0:
            raise ValidationError(_l('No such group'))


class GroupInviteForm(FlaskForm):
    group_id = SelectField(_l('Group Name'), coerce=int)
    submit = SubmitField(_l('Submit'))

    def validate_group_id(self, field):
        if Group.query.get(field.data) is None:
            raise ValidationError(_l('No such group'))
