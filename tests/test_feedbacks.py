"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from faker import Faker
from flog.models import Feedback
from .helpers import login

fake = Faker()


def test_feedback(client):
    login(client)
    data = {
        "body": fake.text(),
    }
    response = client.post("/feedback/", data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert data["body"] in response_data
    # test delete
    comment = Feedback.query.filter_by(body=data["body"]).first()
    response = client.post(
        f"/admin/feedback/delete/{comment.id}/", follow_redirects=True
    )
    assert response.status_code == 200
    assert Feedback.query.filter_by(body=data["body"]).count() == 0
