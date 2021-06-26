"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import pytest
from flog import create_app
from flog import fakes
from flog.models import db, Role, User


def setup(app, context):
    context.push()
    if not os.path.exists(app.config["UPLOAD_DIRECTORY"]):
        os.mkdir(app.config["UPLOAD_DIRECTORY"])
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    admin = User(
        name=app.config["FLOG_ADMIN"],
        username=app.config["FLOG_ADMIN"],
        email=app.config["FLOG_ADMIN_EMAIL"],
        confirmed=True,
    )
    admin.set_password(app.config["FLOG_ADMIN_PASSWORD"])
    admin.role = Role.query.filter_by(name="Administrator").first()
    db.session.add(admin)
    db.session.commit()
    Role.insert_roles()
    fakes.users(5)
    fakes.posts(5)
    fakes.comments(5)


def clean_up(app, context):
    filename = app.config["FLOG_ADMIN"] + "_" + "test.png"
    test_image_path = os.path.join(app.config["UPLOAD_DIRECTORY"], filename)
    test_image_path2 = os.path.join(app.config["UPLOAD_DIRECTORY"], "test_test.png")
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    if os.path.exists(test_image_path2):
        os.remove(test_image_path2)
    db.session.remove()
    db.drop_all()
    context.pop()


@pytest.fixture
def production():
    app = create_app("production")
    context = app.app_context()
    client = app.test_client()
    setup(app, context)
    yield client
    clean_up(app, context)


@pytest.fixture
def client_with_request_ctx():
    app = create_app("testing")
    context = app.test_request_context()
    client = app.test_client()
    setup(app, context)
    yield client
    clean_up(app, context)


@pytest.fixture
def client():
    app = create_app("testing")
    context = app.app_context()
    client = app.test_client()
    setup(app, context)
    yield client
    clean_up(app, context)
