"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from .helpers import login
from flog.models import User, Role


def test_language_selection(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    admin.locale = 'en_US'
    print(client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True).get_data(as_text=True))
    assert admin.locale == 'zh_Hans_CN'


def test_no_login_language_selection(client):
    client.get("/language/set-locale/zh_Hans_CN/", follow_redirects=True)
    data = client.get('/').get_data(as_text=True)
    assert '加入我们' in data
