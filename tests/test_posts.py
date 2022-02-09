"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from tests.conftest import Testing
from flog import fakes
from faker import Faker
from sqlalchemy import and_
from flog.models import Comment, Notification, User, Post, Column, db

fake = Faker()


class PostTestCase(Testing):
    def test_create_post(self):
        self.login()
        data = self.generate_post()
        post = data["post"]
        response = self.client.get("/")
        response_data = response.get_data(as_text=True)
        assert post["title"] in response_data
        # test if filter 'striptag' work
        assert not (post["content"] in response_data)

        col_name = self.generate_column()["column_name"]
        column = Column.query.filter_by(name=col_name).first()

        # test add post to column when submit
        title = fake.sentence()
        data = dict(title=title, content=fake.text(), columns=[column.id])
        response = self.client.post("/write/", data=data, follow_redirects=True)
        assert response.status_code == 200

        post = Post.query.filter_by(title=title).first()

        assert post in column.posts
        assert column in self.admin.columns

    def test_collect_uncollect(self):
        self.login()

        post_not_private = Post.query.filter(
            Post.author != self.admin, ~Post.private
        ).first()
        while post_not_private is None:  # ensure the post exists
            fakes.posts(5)
            post_not_private = Post.query.filter(
                Post.author != self.admin, ~Post.private
            ).first()
        post_id = post_not_private.id
        self.client.get(f"/post/collect/{post_id}", follow_redirects=True).get_data(
            as_text=True
        )
        assert self.admin.is_collecting(post_not_private)

        # test if the collected post appears in the collection page
        response = self.client.get("/post/collected/")
        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert post_not_private.title in data

        data = self.client.get(
            f"/post/collect/{post_id}", follow_redirects=True
        ).get_data(as_text=True)
        assert "Already collected." in data

        data = self.client.get(
            f"/post/uncollect/{post_id}", follow_redirects=True
        ).get_data(as_text=True)
        assert "Post uncollected." in data
        assert not self.admin.is_collecting(post_not_private)

        private_post = Post.query.filter(
            Post.author != self.admin, Post.private
        ).first()
        while private_post is None:  # same as the while loop above
            fakes.posts(5)
            private_post = Post.query.filter(
                Post.author != self.admin, Post.private
            ).first()
        post_id = private_post.id
        data = self.client.get(
            f"/post/collect/{post_id}", follow_redirects=True
        ).get_data(as_text=True)
        assert (
            "The author has set this post to invisible. So you cannot collect this post."
            in data
        )
        assert not self.admin.is_collecting(private_post)

        title = self.generate_post()["post"]["title"]
        post_id = Post.query.filter_by(title=title).first().id
        data = self.client.get(
            f"/post/collect/{post_id}", follow_redirects=True
        ).get_data(as_text=True)
        assert "You cannot collect your own post." in data
        assert not self.admin.is_collecting(Post.query.get(post_id))

    def test_view_post(self):
        post = Post.query.filter(~Post.private).first()
        while post is None:
            fakes.posts(5)
            post = Post.query.filter(~Post.private).first()
        data = self.get_response_and_data_of_post(post.id)[1]

        assert post.content in data

        post_private = Post.query.filter(Post.private).first()
        while post_private is None:
            fakes.posts(5)
            post_private = Post.query.filter(Post.private).first()
        data = self.get_response_and_data_of_post(post_private.id)[1]
        assert "The author has set this post to invisible." in data

        self.login()

        post_not_private = Post.query.filter(
            Post.author != self.admin, ~Post.private
        ).first()
        while post_not_private is None:  # ensure the post exists
            fakes.posts(5)
            post_not_private = Post.query.filter(
                Post.author != self.admin, ~Post.private
            ).first()
        data = self.get_response_and_data_of_post(post_not_private.id)[1]
        assert post_not_private.content in data

        self.logout()

        self.register("john", "john", "123456", "john@example.com")
        self.login("john", "123456")
        data = self.get_response_and_data_of_post(post_private.id)[1]
        assert "The author has set this post to invisible." in data

    def test_edit_post(self):
        self.login()
        post_data = self.generate_post()
        title = post_data["post"]["title"]
        post_id = Post.query.filter_by(title=title).first().id
        response = self.client.get(f"/post/edit/{post_id}/")
        response_data = response.get_data(as_text=True)
        # test if the old content exists in the edit page.
        assert post_data["text"] in response_data
        data = dict(title="new title", content="new content", private=True)
        response = self.client.post(
            f"/post/edit/{post_id}/", data=data, follow_redirects=True
        )
        assert response.status_code == 200
        post = Post.query.get(post_id)
        assert post is not None
        assert post.title == data["title"]
        assert post.private

    def test_delete_post(self):
        self.login()
        title = self.generate_post()["post"]["title"]
        post = Post.query.filter_by(title=title).first()
        response = self.client.post(f"/post/delete/{post.id}/", follow_redirects=True)
        assert response.status_code == 200
        assert Post.query.filter_by(title=title).first() is None

    def test_get_urls(self):
        """Test if the user can GET the urls withour displaying a 500 page."""
        self.login()
        title = self.generate_post()["post"]["title"]
        post = Post.query.filter_by(title=title).first()
        response = self.client.get(f"/post/{post.id}/")
        assert response.status_code == 200
        response = self.client.get("/write/")
        assert response.status_code == 200
        response = self.client.get(f"/post/edit/{post.id}/")
        assert response.status_code == 200
        response = self.client.get("/post/manage/")
        assert response.status_code == 200

    def test_comments(self):
        self.login()
        title = self.generate_post()["post"]["title"]
        post = Post.query.filter_by(title=title).first()
        data = {"body": "comment content"}
        response = self.client.post(
            f"/post/{post.id}/", data=data, follow_redirects=True
        )
        assert response.status_code == 200
        response = self.client.get(f"/post/{post.id}/")
        assert data["body"] in response.get_data(as_text=True)
        comment = Comment.query.filter_by(body=data["body"]).first()

        # test replying comments
        response2 = self.client.get(
            f"/reply/comment/{comment.id}/", follow_redirects=True
        )

        assert post.title in response2.get_data(as_text=True)

        reply = {"body": "reply"}
        response = self.client.post(
            f"/post/{post.id}/?reply={comment.id}", data=reply, follow_redirects=True
        )
        assert response.status_code == 200
        assert len(comment.replies) == 1

        # test deleting comments
        response = self.client.post(
            f"/comment/delete/{comment.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert Comment.query.get(comment.id) is None

    def test_comment_posts_of_deleted_users(self):
        self.register()
        self.login("test", "password")
        title = self.generate_post(username="test", password="password")["post"][
            "title"
        ]
        self.logout()
        post = Post.query.filter_by(title=title).first()
        user = User.query.filter_by(username="test").first()
        user.delete()
        self.login()

        data = {"body": "comment content"}
        response = self.client.post(
            f"/post/{post.id}/", data=data, follow_redirects=True
        )
        assert response.status_code == 200

    def test_picks(self):
        self.login()
        post = Post.query.filter(and_(~Post.picked, ~Post.private)).first()
        response = self.client.post(f"/post/pick/{post.id}/", follow_redirects=True)
        assert response.status_code == 200
        assert post.picked

        response = self.client.get("/post/picks/")
        assert post.title in response.get_data(as_text=True)

        response = self.client.post(f"/post/unpick/{post.id}/", follow_redirects=True)
        assert response.status_code == 200

        response = self.client.get("/post/picks/")
        assert post.title not in response.get_data(as_text=True)

    def test_publish_experience(self):
        """test if the user receives 5 exp when publishing a post"""
        self.login()
        self.generate_post()
        assert self.admin.experience == 5

    def test_coin_experience(self):
        """test if the user and the author both receive 10exp when 'inserting' a coin."""
        self.register()
        self.login("test", "password")
        title = self.generate_post()["title"]
        p = Post.query.filter_by(title=title).first()
        self.logout()
        self.login()
        self.client.post(f"/post/coin/{p.id}/", data={"coins": 2})
        u_test = User.query.filter_by(username="test").first()
        response = self.client.get(f"/user/{u_test.id}/")
        assert "1" in response.get_data(as_text=True)
        assert u_test.experience == 25
        assert self.admin.experience == 20

    def test_no_enough_coins(self):
        """test if the app will return a 400 response when there isn't enough coins."""
        self.register()
        self.login("test", "password")
        u = User.query.filter_by(username="test").first()
        u.coins = 1
        db.session.commit()
        title = self.generate_post()["title"]
        p = Post.query.filter_by(title=title).first()
        response = self.client.post(f"/post/coin/{p.id}/", data={"coins": 2})
        assert response.status_code == 400

    def test_pick_experience(self):
        """test if picking a post will increase the author's experience"""
        self.register()
        self.login()
        title = self.generate_post()["title"]
        p = Post.query.filter_by(title=title).first()
        self.client.post(f"/post/pick/{p.id}/")
        assert self.admin.experience == 25
        # test if picking a post twice will increase the author's experience twice
        self.client.post(f"/post/pick/{p.id}/")
        assert self.admin.experience == 25


class ColumnTestCase(Testing):
    def setUp(self):
        super().setUp()
        self.register()
        self.login("test", "password")

    def test_create_column(self):
        self.generate_post(login=False)
        response = self.client.get("/column/create/")
        assert response.status_code == 200

        user = User.query.filter_by(username="test").first()
        column = dict(
            name="test",
            posts=[post.id for post in Post.query.filter_by(author=user).all()],
        )
        response = self.client.post(
            "/column/create/", data=column, follow_redirects=True
        )
        assert response.status_code == 200
        res_data = response.get_data(as_text=True)
        assert "Your column was successfully created." in res_data

    def test_view_column(self):
        col_name = self.generate_column()["column_name"]
        column = Column.query.filter_by(name=col_name).first()
        response = self.client.get(f"/column/{column.id}/", follow_redirects=True)
        assert response.status_code == 200
        assert col_name in response.get_data(as_text=True)
        response = self.client.get("/column/all/")
        assert response.status_code == 200
        assert col_name in response.get_data(as_text=True)
        self.logout()

    def test_request_post_to_column(self):
        notification_count = Notification.query.count()
        col_name = self.generate_column()["column_name"]
        self.logout()
        self.login()
        post = Post.query.filter_by(title=self.generate_post()["title"]).first()
        column = Column.query.filter_by(name=col_name).first()
        response = self.client.post(
            f"/column/{column.id}/request/{post.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert Notification.query.count() == notification_count + 1
        self.logout()
        self.login("test", "password")
        response = self.client.post(
            f"/column/{column.id}/approve/{post.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert post in column.posts

    def test_request_post_to_column(self):
        notification_count = Notification.query.count()
        col_name = self.generate_column()["column_name"]
        self.logout()
        self.login()
        post = Post.query.filter_by(title=self.generate_post()["title"]).first()
        column = Column.query.filter_by(name=col_name).first()
        response = self.client.post(
            f"/column/{column.id}/request/{post.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert Notification.query.count() == notification_count + 1
        self.logout()
        self.login("test", "password")
        response = self.client.get(
            f"/column/{column.id}/approve/{post.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert post in column.posts

    def test_transpost_post_to_column(self):
        post = Post.query.filter_by(title=self.generate_post()["title"]).first()
        notification_count = Notification.query.count()
        self.logout()

        self.login()
        col_name = self.generate_column()["column_name"]
        column = Column.query.filter_by(name=col_name).first()
        response = self.client.post(
            f"/post/{post.id}/transpost/{column.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert Notification.query.count() == notification_count + 1
        self.logout()
        self.login("test", "password")
        response = self.client.get(
            f"/post/{post.id}/approve/{column.id}/", follow_redirects=True
        )
        assert response.status_code == 200
        assert post in column.posts
