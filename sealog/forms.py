from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     DateField, TextAreaField)
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from flask_ckeditor import CKEditorField
from .models import User


class ArticleForm(FlaskForm):
    name = StringField("Your name(English, Chinese, Arabic Numbers):",
                       validators=[DataRequired()])
    password = PasswordField("You will need a password to create an article",
                             validators=[DataRequired()])
    date = DateField("Date(yyyy-mm-dd)(2020-01-01)",
                     validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AdminLoginForm(FlaskForm):
    name = StringField("Your name: ", validators=[DataRequired()])
    password = PasswordField("ADMIN PASSWORD", validators=[DataRequired()])
    submit = SubmitField("Login")


class EditForm(FlaskForm):
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Publish", validators=[DataRequired()])


class FeedbackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    body = TextAreaField('Feedback', validators=[DataRequired(), Length(1, 200)])  # noqa
    submit = SubmitField()


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
