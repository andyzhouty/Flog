from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


dr_message = _l('Please fill out this field.')

class PostForm(FlaskForm):
    date = DateField(_l("Date(yyyy-mm-dd)(2020-01-01)"),
                     validators=[DataRequired(dr_message)])
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    submit = SubmitField(_l("Submit"))


class EditForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    submit = SubmitField(_l("Publish"), validators=[DataRequired(dr_message)])


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired(dr_message)])
    submit = SubmitField(_l('Comment'))
