from flog.models import User, Role, Group, Notification
from .helpers import register, login, logout


def test_join_group(client):
    register(client)
    login(client, 'test', 'password')
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    data = {
        'name': 'test_group'
    }
    client.post('/group/create/', data=data, follow_redirects=True)
    group = Group.query.filter_by(name=data['name']).first()
    logout(client)
    login(client)
    assert not admin.in_group(group)
    token = group.generate_join_token()
    response = client.get(f'/group/join/{token}/', follow_redirects=True)
    assert response.status_code == 200
    assert admin.in_group(group)


def test_explore_group(client):
    register(client)
    login(client, 'test', 'password')
    admin = User.query.filter_by(
        role=Role.query.filter_by(
            name='Administrator'
        ).first()
    ).first()
    data = {
        'name': 'test_group'
    }
    client.post('/group/create/', data=data, follow_redirects=True)
    logout(client)
    login(client)
    notifaction_count = Notification.query.count()
    response = client.get('/group/explore/')
    assert response.status_code == 200
    fake_data = {
        'name': 'not existing'
    }
    response = client.post('/group/explore/', data=fake_data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert 'No such group' in response_data
    response = client.post('/group/explore/', data=data, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "We have sent a notification to the manager of the group." in response_data
    assert Notification.query.count() == notifaction_count + 1


def test_group_invite(client):
    register(client)
    login(client, 'test', 'password')
    data = {
        'name': 'test_group'
    }
    client.post('/group/create/', data=data, follow_redirects=True)
    notification_count = Notification.query.count()
    group = Group.query.filter_by(name=data['name']).first()
    response = client.get(f'/group/invite/1/?group_id={group.id}', follow_redirects=True)
    response_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert Notification.query.count() == notification_count + 1
    assert f"Notification sent to user" in response_data


def test_group_hint_ajax(client):
    login(client)
    data1 = {'name': 'test_group'}
    data2 = {'name': 'test_group1234abcd'}
    client.post('/group/create/', data=data1, follow_redirects=True)
    client.post('/group/create/', data=data2, follow_redirects=True)
    response = client.get('/ajax/group/hint/?q=test')
    response_data = response.get_json()
    assert response.status_code == 200
    assert data1['name'] in response_data["hint"]
    assert data2['name'] in response_data["hint"]
    assert len(response_data["hint"]) == 2
    response = client.get('/ajax/group/hint/?q=1234')
    response_data = response.get_json()
    assert data2['name'] in response_data["hint"]
    assert data1['name'] not in response_data["hint"]
