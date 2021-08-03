"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
from os.path import abspath, dirname
from flask.globals import current_app
from flog.models import Image
from .helpers import login, logout, register, upload_image, delete_image


def test_basic_operations(client_with_request_ctx):
    client = client_with_request_ctx
    login(client)
    filename = current_app.config["FLOG_ADMIN"] + "_test.png"
    uploaded_path = os.path.join(current_app.config["UPLOAD_DIRECTORY"], filename)
    if os.path.exists(uploaded_path):
        os.remove(uploaded_path)
    assert not os.path.exists(uploaded_path)
    response = upload_image(client)
    assert response.status_code == 200
    assert os.path.exists(uploaded_path)
    image = Image.query.filter_by(filename=filename).first()
    assert image is not None
    assert image.path() == uploaded_path
    assert image.url().endswith(f"/image/{image.filename}")
    assert not image.private
    response = client.post(f"/image/toggle/{image.id}/", follow_redirects=True)
    assert response.status_code == 200
    assert image.private
    response = delete_image(client, image.id)
    assert response.status_code == 200
    assert Image.query.filter_by(filename=filename).first() is None
    assert not os.path.exists(uploaded_path)


def test_get_image(client):
    login(client)
    upload_image(client)
    # test duplicate images
    upload_image(client)
    logout(client)
    # test if the image can be got without authentication
    filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
    response = client.get(f"/image/{filename}")
    assert response.status_code == 200
    filename = current_app.config["FLOG_ADMIN"] + "_" + "test_.png"
    response = client.get(f"/image/{filename}")
    login(client)
    image = Image.query.filter_by(filename=filename).first()
    delete_image(client, image.id)


def test_manage_images(client):
    login(client)
    upload_image(client)
    response = client.get("/image/manage/")
    data = response.get_data(as_text=True)
    filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
    assert f'/image/{filename}' in data
    image = Image.query.filter_by(filename=filename).first()
    delete_image(client, image.id)
    logout(client)

    register(client)
    login(client, "test", "password")
    upload_image(client)
    response = client.get("/image/manage/")
    data = response.get_data(as_text=True)
    filename = "test_test.png"
    print(data)

    assert f'/image/{filename}' in data
    image = Image.query.filter_by(filename=filename).first()
    delete_image(client, image.id)


def test_image_errors(client):
    login(client)
    upload_image(client)
    filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
    image = Image.query.filter_by(filename=filename).first()
    image.toggle_visibility()
    assert image.private
    logout(client)
    register(client)
    login(client, "test", "password")
    response = client.get(f"/image/{filename}")
    assert response.status_code == 403
    response = client.post(f"/image/toggle/{image.id}/", follow_redirects=True)
    assert response.status_code == 403
    response = delete_image(client, image.id)
    assert response.status_code == 403
    logout(client)
    login(client)
    delete_image(client, image.id)
