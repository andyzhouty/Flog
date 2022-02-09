from flask_sqlalchemy import event
from .models import Column, User


@event.listens_for(Column.posts, "append")
def connect_column_post_to_user(target, value, initiator):
    if target.author is not None:
        target.author.posts.append(value)


@event.listens_for(User.columns, "append")
def add_column_to_useR(author, column, *args):
    for post in column.posts:
        author.posts.append(post)
