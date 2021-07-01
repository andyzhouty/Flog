import os
from flask import (
    current_app,
    request,
    send_from_directory,
    abort,
    render_template,
    flash,
)
from flask_login import login_required, current_user
from flask_ckeditor import upload_fail, upload_success
from flask_babel import _

from ..utils import get_image_path_and_url, redirect_back
from ..models import db, Image
from . import image_bp


@image_bp.route("/<path:filename>")
def uploaded_files(filename: str):
    image = Image.query.filter_by(filename=filename).first_or_404()
    if image.private:
        abort(403)
    image_directory = current_app.config["UPLOAD_DIRECTORY"]
    return send_from_directory(directory=image_directory, path=filename)


@image_bp.route("/upload/", methods=["POST"])
@login_required
def upload():
    image_obj = request.files.get("upload")
    if image_obj is None:
        flash(_("No image uploaded!"))
        return redirect_back()
    response = get_image_path_and_url(image_obj, current_user)
    if response.get("error") is not None:
        return upload_fail(message=response["error"])
    image_url = response["image_url"]
    filename = response["filename"]
    return upload_success(url=image_url, filename=filename)


@image_bp.route("/manage/")
@login_required
def manage():
    page = request.args.get("page", 1, int)
    if not current_user.is_administrator():
        pagination = (
            Image.query.with_parent(current_user)
            .order_by(Image.timestamp.desc())
            .paginate(page, per_page=current_app.config["IMAGES_PER_PAGE"])
        )
    else:
        pagination = Image.query.order_by(Image.timestamp.desc()).paginate(
            page, per_page=current_app.config["IMAGES_PER_PAGE"]
        )
    images = pagination.items
    return render_template("image/manage.html", pagination=pagination, images=images)


@image_bp.route("/toggle/<int:id>/", methods=["POST"])
@login_required
def toggle_visibility(id: int):
    image = Image.query.get(id)
    if image.author != current_user and not current_user.is_administrator():
        abort(403)
    image.private = not image.private
    db.session.commit()
    flash(_("Image {filename} visibility toggled".format(filename=image.filename)))
    return redirect_back()


@image_bp.route("/delete/<int:id>/", methods=["POST"])
@login_required
def delete(id: int):
    image = Image.query.get(id)
    if image.author != current_user and not current_user.is_administrator():
        abort(403)
    filename = image.filename
    try:
        os.remove(image.path())
    except FileNotFoundError:
        pass
    finally:
        db.session.delete(image)
        db.session.commit()
        flash(_("Image {filename} deleted".format(filename=filename)))
        return redirect_back()
