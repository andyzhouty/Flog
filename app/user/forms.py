from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length


# l_message is short for 'length_message'
l_message = _l('Field must be between %(min)d and %(max)d characters long.')

class EditProfileForm(FlaskForm):
    name = StringField(_l('Real Name'), validators=[Length(0, 64, l_message)])
    location = StringField(_l('Location'), validators=[Length(0, 64, l_message)])
    about_me = TextAreaField(_l('About me'), validators=[Length(0, 300, l_message)])
    submit = SubmitField(_l('Submit'))
