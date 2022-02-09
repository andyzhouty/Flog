"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
from flask.globals import current_app
from flog.models import Image
from .conftest import Testing


class ImageTestCase(Testing):
    def test_basic_operations(self):
        self.login()
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
        self.login()
        self.upload_image()
        # test duplicate images
        self.upload_image()
        self.logout()
        # test if the image can be got without authentication
        filename1 = current_app.config["FLOG_ADMIN"] + "_" + "test.png"
        response = self.client.get(f"/image/{filename1}")
        assert response.status_code == 200
        filename2 = current_app.config["FLOG_ADMIN"] + "_" + "test_.png"
        response = self.client.get(f"/image/{filename2}")
        self.login()
        for filename in (filename1, filename2):
            image = Image.query.filter_by(filename=filename).first()
            self.delete_image(image.id)

    def test_manage_images(self):
        self.login()
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
        self.login()
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

    def test_api_v1(self):
        admin_username = current_app.config["FLOG_ADMIN"]
        admin_password = current_app.config["FLOG_ADMIN_PASSWORD"]
        image_dict = self.api_upload_image(
            "/api/v1",
            headers=self.get_api_v1_headers(
                username=admin_username,
                password=admin_password,
                content_type="multipart/form-data",
            ),
        )
        response = image_dict["response"]
        data = image_dict["data"]
        assert response.status_code == 201
        assert data["filename"] == f"{admin_username}_test.png"
        response = self.client.get(f"/image/{admin_username}_test.png")
        assert response.status_code == 200
        image_id = data["image_id"]
        response = self.client.delete(
            f"/api/v1/image/{image_id}/",
            headers=self.get_api_v1_headers(
                username=admin_username, password=admin_password
            ),
        )
        assert response.status_code == 204
        assert Image.query.get(image_id) is None

    def test_api_v2(self):
        admin_username = current_app.config["FLOG_ADMIN"]
        admin_password = current_app.config["FLOG_ADMIN_PASSWORD"]
        image_dict = self.api_upload_image(
            "/api/v2",
            headers=self.get_api_v2_headers(
                username=admin_username,
                password=admin_password,
                content_type="multipart/form-data",
            ),
        )
        response = image_dict["response"]
        data = image_dict["data"]
        assert response.status_code == 201
        assert data["filename"] == f"{admin_username}_test.png"
        response = self.client.get(f"/image/{admin_username}_test.png")
        assert response.status_code == 200
        image_id = data["image_id"]
        response = self.client.delete(
            f"/api/v2/image/{image_id}/",
            headers=self.get_api_v2_headers(
                username=admin_username, password=admin_password
            ),
        )
        assert response.status_code == 204
        assert Image.query.get(image_id) is None

    def test_api_v3(self):
        self.register()
        data = self.api_upload_image(
            "/api/v3",
            self.get_api_v3_headers(content_type="multipart/form-data"),
        )["data"]
        assert data["filename"] == "test_test.png"
        image_id = data["id"]
        response = self.client.delete(
            f"/api/v3/image/{image_id}", headers=self.get_api_v3_headers()
        )
        assert response.status_code == 204
