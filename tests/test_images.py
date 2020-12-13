from flog.main.views import upload
import os
from os.path import abspath, dirname, join
from flask import url_for
from flask.globals import current_app
from flog.models import Image
from .helpers import login


def test_image(client):
    login(client)
    filename = current_app.config['FLOG_ADMIN'] + '_test.png'
    uploaded_path = os.path.join(
        current_app.config['UPLOAD_DIRECTORY'],
        filename
    )
    if os.path.exists(uploaded_path):
        os.remove(uploaded_path)
    assert not os.path.exists(uploaded_path)
    os.chdir(dirname(abspath(__file__)))
    image_obj = open('test.png', 'rb')
    data = {'upload': image_obj}
    response = client.post(
        url_for('main.upload'),
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert os.path.exists(uploaded_path)
    image = Image.query.filter_by(filename=filename).first()
    assert image is not None
    assert image.path() == uploaded_path
    assert image.url() == url_for('main.uploaded_files', filename=filename)
    assert not image.private
    response = client.post(
        url_for(
            'main.toggle_image_visibility',
            id=image.id
        ), follow_redirects=True
    )
    assert response.status_code == 200
    assert image.private
    response = client.post(
        url_for(
            'main.delete_image',
            id=image.id
        ), follow_redirects=True
    )
    assert response.status_code == 200
    assert Image.query.filter_by(filename=filename).first() is None
    assert not os.path.exists(uploaded_path)
