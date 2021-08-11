"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
from os.path import abspath, dirname
from flask.globals import current_app
from flog.models import Image

from .conftest import Testing


class ImageTestCase(Testing):
    def setUp(self):
        super().setUp()
        self.login()

    def test_basic_operations(self):
        filename = current_app.config["FLOG_ADMIN"] + "_test.png"
        uploaded_path = os.path.join(current_app.config["UPLOAD_DIRECTORY"], filename)
        if os.path.exists(uploaded_path):
            os.remove(uploaded_path)
        assert not os.path.exists(uploaded_path)
        response = self.upload_image()
        assert response.status_code == 200
        assert os.path.exists(uploaded_path)
        image = Image.query.filter_by(filename=filename).first()
        assert image is not None
        assert image.path() == uploaded_path
        assert image.url().endswith(f"/image/{image.filename}")
        assert not image.private
        response = self.client.post(f"/image/toggle/{image.id}/", follow_redirects=True)
        assert response.status_code == 200
        assert image.private
        response = self.delete_image(image.id)
        assert response.status_code == 200
        assert Image.query.filter_by(filename=filename).first() is None
        assert not os.path.exists(uploaded_path)

    def test_get_image(self):
        self.upload_image()
        # test duplicate images
        self.upload_image()
        self.logout()
        # test if the image can be got without authentication
        filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
        response = self.client.get(f"/image/{filename}")
        assert response.status_code == 200
        filename = current_app.config["FLOG_ADMIN"] + "_" + "test_.png"
        response = self.client.get(f"/image/{filename}")
        self.login()
        image = Image.query.filter_by(filename=filename).first()
        self.delete_image(image.id)

    def test_manage_images(self):
        self.upload_image()
        response = self.client.get("/image/manage/")
        data = response.get_data(as_text=True)
        filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
        assert f"/image/{filename}" in data
        image = Image.query.filter_by(filename=filename).first()
        self.delete_image(image.id)
        self.logout()

        self.register()
        self.login("test", "password")
        self.upload_image()
        response = self.client.get("/image/manage/")
        data = response.get_data(as_text=True)
        filename = "test_test.png"

        assert f"/image/{filename}" in data
        image = Image.query.filter_by(filename=filename).first()
        self.delete_image(image.id)

    def test_image_errors(self):
        self.upload_image()
        filename = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
        image = Image.query.filter_by(filename=filename).first()
        image.toggle_visibility()
        assert image.private
        self.logout()
        self.register()
        self.login("test", "password")
        response = self.client.get(f"/image/{filename}")
        assert response.status_code == 403
        response = self.client.post(f"/image/toggle/{image.id}/", follow_redirects=True)
        assert response.status_code == 403
        response = self.delete_image(image.id)
        assert response.status_code == 403
        self.logout()
        self.login()
        self.delete_image(image.id)
