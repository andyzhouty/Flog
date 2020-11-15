import os
from faker import Faker
from flog.notifications import (
    push_collect_notification, push_comment_notification, push_follow_notification
)
from flog.models import db, Comment, Notification, Post, User, Role

fake = Faker()

def login(client, username=os.getenv('FLOG_ADMIN'),
          password=os.getenv('FLOG_ADMIN_PASSWORD')):
    """Login helper function"""
    return client.post(
        "/auth/login/",
        data=dict(username_or_email=username, password=password),
        follow_redirects=True
    )

def logout(client):
    """Logout helper function"""
    return client.get('/auth/logout/', follow_redirects=True)


def register(client, name='Test', username='test', password='password', email='test@example.com'):
    """Register helper function"""
    return client.post('/auth/register/', data=dict(
        name=name,
        username=username,
        email=email,
        password=password,
        password_again=password
    ), follow_redirects=True)

def create_article(client):
    """Create a post for test use"""
    login(client)
    text = fake.text()
    data = {
        'title': fake.sentence(),
        'content': f"<p>{text}</p>",
    }
    return {
        'response': client.post('/write/', data=data, follow_redirects=True),
        'post': data,
        'text': text,
    }

def send_notification(client):
    """Send notifications for test user"""
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    notification = Notification(
        message='test',
        receiver=admin
    )
    db.session.add(notification)
    db.session.commit()
