from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp, ValidationError
from ..models import User


class RegisterationForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(), Length(1, 32),
        Regexp(r'^[A-Za-z][A-Za-z0-9_\-.]*$', 0,
               'Usernames must have only letters, numbers, dots, underscores or dashes')
    ])
    name = StringField('Real Name', validators=[DataRequired(), Length(2, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(2, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField(
        'Password (Again)', validators=[
            DataRequired(), EqualTo('password', "Passwords must match")])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

class LoginForm(FlaskForm):
    username_or_email = StringField('Username / Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remeber me')
    submit = SubmitField('Login')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete Account')
