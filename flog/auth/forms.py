"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp, ValidationError
from ..models import User


# dr_message is short for 'data required message'
dr_message = _l('Please fill out this field.')
# l_message is short for 'length message'
l_message = _l('Field must be between %(min)d and %(max)d characters long.')
# e_message is short for 'email message'
e_message = _l('Invalid email.')

class RegisterationForm(FlaskForm):
    username = StringField(
        _l('Username'), validators=[
            DataRequired(dr_message),
            Length(1, 32),
            Regexp(r'^[A-Za-z][A-Za-z0-9_\-.]*$', 0,
                   _l('Usernames must have only letters, numbers, dots, underscores or dashes'))
    ])
    name = StringField(_l('Real Name'), validators=[DataRequired(dr_message), Length(2, 64)])
    email = StringField(
        _l('Email (Requires Verification)'),
        validators=[DataRequired(dr_message), Length(2, 64, l_message), Email(e_message)]
    )
    password = PasswordField(_l('Password'), validators=[DataRequired(dr_message)])
    password_again = PasswordField(
        _l('Password (Again)'),
        validators=[
            DataRequired(dr_message),
            EqualTo('password', _l("Passwords must match"))
    ])
    submit = SubmitField(_l('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_l('Email already registered'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('Username already in use'))

class LoginForm(FlaskForm):
    username_or_email = StringField(_l('Username / Email'), validators=[DataRequired(dr_message)])
    password = PasswordField(_l('Password'), validators=[DataRequired(dr_message)])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Login'))


class DeleteAccountForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired(dr_message)])
    submit = SubmitField(_l('Delete Account'))
