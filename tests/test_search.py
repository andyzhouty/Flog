"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from flog.models import db, Group, User, Role, Group
from .helpers import create_article, login

def test_search(client):
    login(client)
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    create_article(client, "abcd")
    create_article(client, "efgh")
    create_article(client, "ijklmn")
    response = client.get("/search/?q=ab&category=post")
    assert response.status_code == 200
    response_data = response.get_data(as_text=True)
    assert "abcd" in response_data
    assert "efgh" not in response_data
    assert "ijklmn" not in response_data
    group1 = Group(manager=admin, name="xyz")
    db.session.add(group1)
    db.session.commit()
    response_data = client.get("/search/?q=xyz&category=post").get_data(as_text=True)
    print(response_data)
    assert "Group name: xyz" not in response_data
    response_data = client.get("/search/?q=xyz&category=group").get_data(as_text=True)
    assert "Group name: xyz" in response_data
    response_data = client.get(f"/search/?q={admin.username[:2]}&category=user")\
                          .get_data(as_text=True)
    assert admin.username in response_data
