"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField


# dr_message means data_required_message
dr_message = _l("Please fill out this field with valid values.")
l_message = _l("Field must be between %(min)d and %(max)d characters long.")


class PostForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    private = BooleanField(_l("Private"))
    submit = SubmitField(_l("Submit"))


class EditForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    private = BooleanField(_l("Private"))
    submit = SubmitField(_l("Publish"))


class CommentForm(FlaskForm):
    body = TextAreaField("", validators=[DataRequired(dr_message)])
    submit = SubmitField(_l("Comment"))


class ColumnForm(FlaskForm):
    name = StringField(_l("Column Name"), validators=[DataRequired(dr_message), Length(0, 128, l_message)])
    posts = SelectMultipleField(_l("Posts to add"), coerce=int)
    submit = SubmitField(_l("Submit"))
