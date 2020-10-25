import pytest
from flog import create_app, db, fakes
from flog.models import Role, User

@pytest.fixture()
def client():
    app = create_app('testing')
    context = app.app_context()
    client = app.test_client()
    context.push()
    db.create_all()
    Role.insert_roles()
    admin = User(
        name=app.config['FLOG_ADMIN'],
        username=app.config['FLOG_ADMIN'],
        email=app.config['FLOG_ADMIN_EMAIL'],
        confirmed=True
    )
    admin.set_password(app.config['FLOG_ADMIN_PASSWORD'])
    admin.role = Role.query.filter_by(name='Administrator').first()
    db.session.add(admin)
    db.session.commit()
    Role.insert_roles()
    fakes.users(10)
    fakes.posts(10)
    fakes.comments(10)
    yield client
    db.session.remove()
    db.drop_all()
    context.pop()
