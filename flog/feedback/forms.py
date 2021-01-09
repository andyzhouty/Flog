"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


dr_message = _l("Please fill out this field.")
l_message = _l("Field must be between %(min)d and %(max)d characters long.")


class FeedbackForm(FlaskForm):
    body = TextAreaField(
        _l("Feedback"), validators=[DataRequired(), Length(1, 200)]
    )  # noqa
    submit = SubmitField(_l("Feedback"))
