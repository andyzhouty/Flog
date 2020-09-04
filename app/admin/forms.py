from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.core import BooleanField, StringField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import Role, User


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(5, 64),
                                             Email()])
    username = StringField(
        'Username', validators=[DataRequired(), Length(1, 32),
        Regexp(r'^[A-Za-z][A-Za-z0-0_\-.]*$', 0,
               'Usernames must have only letters, numbers, dots, underscores or dashes')
    ])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None and self.user != user:
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        user = User.query.filter_by(name=field.data).first()
        if user is not None and self.user != user:
            raise ValidationError('Username already in use.')
