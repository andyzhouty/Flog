"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flask import url_for
from faker import Faker
from .helpers import login

fake = Faker()


def test_send_feedback(client):
    login(client)
    data = {'body': fake.text(), }
    response = client.post(url_for('feedback.feedback'), data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert data['body'] in response_data


def test_change_theme(client):
    client.get(url_for('others.change_theme', theme_name='lite'), follow_redirects=True)
    cookie = next(
        (cookie for cookie in client.cookie_jar if cookie.name == "theme"),
        None
    )
    assert cookie is not None
    assert cookie.value == 'lite'
