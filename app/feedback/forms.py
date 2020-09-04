from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class FeedbackForm(FlaskForm):
    body = TextAreaField('Feedback', validators=[DataRequired(), Length(1, 200)])  # noqa
    submit = SubmitField()

