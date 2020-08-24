from flask import render_template, current_app
from flask_login import current_user
from ..forms import ArticleForm
from ..models import db, Article
from . import user_bp


@user_bp.route('/write/', endpoint='new')
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            date=form.date.data,
            author=current_user.name,
            content=form.content.data
        )
        db.session.add(article)
    return render_template('articles/new_article.html', form=form)
