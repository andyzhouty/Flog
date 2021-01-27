"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
from faker import Faker
from flask import current_app
from base64 import b64encode
from flog.models import db, Notification, User, Role

fake = Faker()


def login(
    client, username=os.getenv("FLOG_ADMIN"), password=os.getenv("FLOG_ADMIN_PASSWORD")
):
    """Login helper function"""
    if username is None:
        username = current_app.config["FLOG_ADMIN"]
    if password is None:
        password = current_app.config["FLOG_ADMIN_PASSWORD"]
    return client.post(
        "/auth/login/",
        data=dict(username_or_email=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/auth/logout/", follow_redirects=True)


def register(
    client,
    name: str = "Test",
    username: str = "test",
    password: str = "password",
    email: str = "test@example.com",
):
    """Register helper function"""
    return client.post(
        "/auth/register/",
        data=dict(
            name=name,
            username=username,
            email=email,
            password=password,
            password_again=password,
        ),
        follow_redirects=True,
    )


def create_article(client, title=fake.sentence(), text=fake.text(), **kwargs) -> dict:
    """Create a post for test use"""
    login(client, **kwargs)
    data = {
        "title": title,
        "content": f"<p>{text}</p>",
    }
    return {
        "response": client.post("/write/", data=data, follow_redirects=True),
        "post": data,
        "text": text,
    }


def send_notification(client) -> None:
    """Send notifications for test user"""
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(name="Administrator").first()
    ).first()
    notification = Notification(message="test", receiver=admin)
    db.session.add(notification)
    db.session.commit()


def get_api_v1_headers(
    username: str = "test", password: str = "password", **kwargs
) -> dict:
    """Returns auth headers for api v1"""
    if kwargs.get("content_type"):
        content_type = kwargs["content_type"]
    else:
        content_type = "application/json"
    return {
        "Authorization": "Basic "
        + b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8"),
        "Accept": "application/json",
        "Content-Type": content_type
    }


def get_api_v2_headers(
    client,
    username: str = "test",
    password: str = "password",
    custom_token: str = None,
    **kwargs,
) -> dict:
    """Returns auth headers for api v2"""
    response = client.post(
        "/api/v2/oauth/token/",
        data=dict(grant_type="password", username=username, password=password),
    )
    data = response.get_json()
    token = data.get("access_token")
    if custom_token is not None:
        token = custom_token
    if kwargs.get("content_type"):
        content_type = kwargs["content_type"]
    else:
        content_type = "application/json"
    return {
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "Content-Type": content_type,
    }


def get_response_and_data_of_post(client, post_id: int) -> tuple:
    response = client.get(f"/post/{post_id}", follow_redirects=True)
    data = response.get_data(as_text=True)
    return response, data


def upload_image(client):
    os.chdir(os.path.dirname(__file__))
    image_obj = open("test.png", "rb")
    data = {"upload": image_obj}
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    response = client.post("/image/upload/", data=data, follow_redirects=True)
    return response


def delete_image(client, image_id: int):
    response = client.post(f"/image/delete/{image_id}/", follow_redirects=True)
    return response


def api_upload_image(client, api_bp_prefix: str, headers: dict) -> dict:
    os.chdir(os.path.dirname(__file__))
    image_obj = open("test.png", "rb")
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    response = client.post(
        f"{api_bp_prefix}/upload/",
        headers=headers,
        data=dict(upload=image_obj),
    )
    return {
        "response": response,
        "data": response.get_json(),
    }
