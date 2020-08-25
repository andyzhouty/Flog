from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from ..models import User


class RegisterationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(2, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(2, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password (Again)', validators=[DataRequired(), EqualTo('password', "Passwords must match")])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Username already in use')

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')
