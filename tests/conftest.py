"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import os
import unittest
import warnings
from base64 import b64encode
from flog import create_app
from flog import fakes
from flog.fakes import fake
from flog.models import db, Role, User, Notification


class Base(unittest.TestCase):
    app = None

    def commonSetUp(self):
        warnings.simplefilter("ignore")
        self.context = self.app.test_request_context()
        self.client = self.app.test_client()
        self.context.push()
        if not os.path.exists(self.app.config["UPLOAD_DIRECTORY"]):
            os.mkdir(self.app.config["UPLOAD_DIRECTORY"])
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        self.admin = User(
            name=self.app.config["FLOG_ADMIN"],
            username=self.app.config["FLOG_ADMIN"],
            email=self.app.config["FLOG_ADMIN_EMAIL"],
            confirmed=True,
        )
        self.admin.set_password(self.app.config["FLOG_ADMIN_PASSWORD"])
        self.admin.role = Role.query.filter_by(name="Administrator").first()
        db.session.add(self.admin)
        db.session.commit()
        Role.insert_roles()
        fakes.users(5)
        fakes.posts(5)
        fakes.comments(5)

    def tearDown(self):
        filename = self.app.config["FLOG_ADMIN"] + "_" + "test.png"
        test_image_path = os.path.join(self.app.config["UPLOAD_DIRECTORY"], filename)
        test_image_path2 = os.path.join(
            self.app.config["UPLOAD_DIRECTORY"], "test_test.png"
        )
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        if os.path.exists(test_image_path2):
            os.remove(test_image_path2)
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login(
        self,
        username=os.getenv("FLOG_ADMIN"),
        password=os.getenv("FLOG_ADMIN_PASSWORD"),
    ):
        """Login helper function"""
        if username is None:
            username = self.app.config["FLOG_ADMIN"]
        if password is None:
            password = self.app.config["FLOG_ADMIN_PASSWORD"]
        return self.client.post(
            "/auth/login/",
            data=dict(username_or_email=username, password=password),
            follow_redirects=True,
        )

    def logout(self):
        """Logout helper function"""
        return self.client.get("/auth/logout/", follow_redirects=True)

    def register(
        self,
        name: str = "Test",
        username: str = "test",
        password: str = "password",
        email: str = "test@example.com",
    ):
        """Register helper function"""
        return self.client.post(
            "/auth/register/",
            data=dict(
                name=name,
                username=username,
                email=email,
                password=password,
                password_again=password,
            ),
            follow_redirects=True,
        )

    def generate_post(self, title=fake.sentence(), text=fake.text(), private=False, **kwargs) -> dict:
        """Create a post for test use"""
        if kwargs.get("login") is True:
            self.login(**kwargs)
        data = dict(title=title, content=f"<p>{text}</p>", private=private)

        return {
            "response": self.client.post("/write/", data=data, follow_redirects=True),
            "post": data,
            "text": text,
            "title": title,
        }

    def generate_column(self, name=fake.word(), columns=None) -> dict:
        if columns is None:
            columns = []
        data = dict(
            name=name,
            columns=columns,
        )
        response = self.client.post("/column/create/", data=data, follow_redirects=True)
        return dict(response=response, column_name=name)

    def send_notification(self) -> None:
        """Send notifications for test user"""
        self.login()
        admin = User.query.filter_by(
            role=Role.query.filter_by(name="Administrator").first()
        ).first()
        notification = Notification(message="test", receiver=admin)
        db.session.add(notification)
        db.session.commit()

    def get_api_v1_headers(
        self, username: str = "test", password: str = "password", **kwargs
    ) -> dict:
        """Returns auth headers for api v1"""
        if kwargs.get("content_type"):
            content_type = kwargs["content_type"]
        else:
            content_type = "application/json"
        return {
            "Authorization": "Basic "
            + b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-Type": content_type,
        }

    def get_api_v2_headers(
        self,
        username: str = "test",
        password: str = "password",
        custom_token: str = None,
        **kwargs,
    ) -> dict:
        """Returns auth headers for api v2"""
        response = self.client.post(
            "/api/v2/oauth/token/",
            data=dict(grant_type="password", username=username, password=password),
        )
        return self.get_token_from_response(response, custom_token, **kwargs)

    def get_api_v3_headers(
        self,
        username: str = "test",
        password: str = "password",
        custom_token: str = None,
        **kwargs,
    ) -> dict:
        """Returns auth headers for api v3"""
        response = self.client.post(
            "/api/v3/token",
            data=dict(username=username, password=password),
        )
        return self.get_token_from_response(response, custom_token, **kwargs)

    @staticmethod
    def get_token_from_response(response, custom_token: str, **kwargs):
        data = response.get_json()
        token = "Bearer " + str(data.get("access_token"))
        if custom_token is not None:
            token = custom_token
        if kwargs.get("content_type"):
            content_type = kwargs["content_type"]
        else:
            content_type = "application/json"
        return {
            "Authorization": token,
            "Accept": "application/json",
            "Content-Type": content_type,
        }

    def get_response_and_data_of_post(self, post_id: int) -> tuple:
        response = self.client.get(f"/post/{post_id}", follow_redirects=True)
        data = response.get_data(as_text=True)
        return response, data

    def upload_image(self):
        os.chdir(os.path.dirname(__file__))
        image_obj = open("test.png", "rb")
        data = {"upload": image_obj}
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        return self.client.post("/image/upload/", data=data, follow_redirects=True)

    def delete_image(self, image_id: int):
        return self.client.post(f"/image/delete/{image_id}/", follow_redirects=True)

    def api_upload_image(self, api_bp_prefix: str, headers: dict) -> dict:
        os.chdir(os.path.dirname(__file__))
        image_obj = open("test.png", "rb")
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        response = self.client.post(
            f"{api_bp_prefix}/image/upload",
            headers=headers,
            data=dict(upload=image_obj),
            follow_redirects=True,
        )
        return {
            "response": response,
            "data": response.get_json(),
        }


class Testing(Base):
    def setUp(self):
        self.app = create_app("testing")
        self.commonSetUp()


class Production(Base):
    def setUp(self) -> None:
        self.app = create_app("production")
        self.commonSetUp()
