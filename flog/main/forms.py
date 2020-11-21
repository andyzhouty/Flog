"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from flask_ckeditor import CKEditorField
from flask_login import current_user
from ..utils import slugify
from ..models import db, Post


dr_message = _l('Please fill out this field with valid values.')

class PostForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    private = BooleanField(_l('Private'))
    submit = SubmitField(_l("Submit"))
    
    def validate_title(self, field):
        slug = slugify(field.data)
        if Post.query.filter(Post.slug==slug, Post.author==current_user).count() != 0:
            raise ValidationError(_l("The title is duplicated with your other post(s). Please change it."))


class EditForm(FlaskForm):
    title = StringField(_l("Title"), validators=[DataRequired(dr_message)])
    content = CKEditorField(_l("Content"), validators=[DataRequired(dr_message)])
    private = BooleanField(_l('Private'))
    submit = SubmitField(_l("Publish"))


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired(dr_message)])
    submit = SubmitField(_l('Comment'))
