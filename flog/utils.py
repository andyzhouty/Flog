"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from os.path import join, exists
from urllib.parse import urlparse, urljoin
from bleach import clean
from flask import current_app, request, redirect, url_for
from werkzeug.utils import secure_filename
from .models import db, Image


def lower_username(username: str) -> str:
    """Returns lowered username"""
    return username.strip().lower().replace(" ", "")


def is_safe_url(target):
    """Check if target url is safe"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="main.main", **kwargs):
    """Redirect back"""
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def get_image_path_and_url(image_obj, current_user) -> dict:
    filename = image_obj.filename
    # add the current user's username to the filename of the image
    filename = current_user.username + "_" + filename
    # find the position of the last dot in the filename
    last_dot_in_filename = filename.rfind(".")
    # get the filename(without extension) and the extension
    filename_without_ext = filename[:last_dot_in_filename]
    extension = filename[last_dot_in_filename + 1 :]  # noqa
    if extension not in ["jpg", "gif", "png", "jpeg", "jpg"]:
        return dict(error="Images only!")
    # get the absolute image path for the new image
    image_path = join(current_app.config["UPLOAD_DIRECTORY"], filename)
    # deal with duplicated filenames
    while exists(image_path):
        filename_without_ext += "_"  # add underscores after the existed filename
        image_path = join(
            current_app.config["UPLOAD_DIRECTORY"],
            filename_without_ext + "." + extension,
        )
    # get final filename
    filename = filename_without_ext + "." + extension
    filename = secure_filename(filename)
    current_app.logger.info(f"Upload file {filename} saved.")
    image_obj.save(image_path)
    # commit the image to the db
    image = Image(filename=filename, author=current_user)
    db.session.add(image)
    db.session.commit()
    url = image.url()
    current_app.logger.info(f"Upload file url: {url}")
    return {"image_url": url, "filename": image.filename, "image_id": image.id}


def clean_html(content: str) -> str:
    return clean(
        content,
        tags=current_app.config["FLOG_ALLOWED_TAGS"],
        attributes=current_app.config["FLOG_ALLOWED_HTML_ATTRIBUTES"],
        strip_comments=True,
    )
