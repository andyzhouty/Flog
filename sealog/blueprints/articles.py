"""
@author: andy zhou
Copyright(c) all rights reserved 2020
"""
# -*- coding:utf-8 -*-
from flask import (render_template, request, flash,
                   url_for, Blueprint, current_app)
from flask_login import current_user
from ..models import Post
from ..forms import ArticleForm
from ..extensions import db
from ..emails import send_email

articles_bp = Blueprint("articles", __name__)


@articles_bp.route('/')
def articles():
    page = request.args.get('page', 1, int)
    all_articles = Post().query.all()
    if all_articles:
        post = Post.query_by_id(page)
        pagination = Post.query.order_by(
            Post.timestamp.desc()).paginate(page, 1)
        return render_template('articles/articles.html',
                               this_article=post,
                               content=post.content,
                               pagination=pagination)
    flash("No Articles! Please Create one first!", "warning")
    return render_template("result.html", url=url_for("articles.new"))


@articles_bp.route('/new/', endpoint='new')
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            date=form.date.data,
            author=current_user.name,
            content=form.content.data
        )
        db.session.add(post)
        db.session.commit()
        email_data = {
            'title': form.title.data,
            'author': current_user.name,
            'content': form.content.data
        }
        recipients = current_app.config['ADMIN_EMAIL_LIST']
        send_email(
            recipients=recipients,
            subject="A new post was added just now!",
            template="articles/article_notification",
            **email_data
        )
    return render_template('articles/new.html', form=form)
