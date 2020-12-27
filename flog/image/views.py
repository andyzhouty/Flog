import os
from os.path import join, exists

from flask import (current_app, request, send_from_directory, abort,
                   render_template, make_response, flash)
from flask_login import login_required, current_user
from flask_ckeditor import upload_fail, upload_success
from flask_babel import _

from ..utils import redirect_back
from ..models import db, Image
from . import image_bp


@image_bp.route('/<path:filename>')
def uploaded_files(filename: str):
    image = Image.query.filter_by(filename=filename).first_or_404()
    if image.private:
        abort(403)
    image_directory = current_app.config['UPLOAD_DIRECTORY']
    return send_from_directory(image_directory, filename=filename)


@image_bp.route('/upload/', methods=['POST'])
@login_required
def upload():
    fileobj = request.files.get('upload')
    filename = fileobj.filename
    # add the current user's username to the filename of the image
    filename = current_user.username + '_' + filename
    # find the position of the last dot in the filename
    last_dot_in_filename = filename.rfind('.')
    # get the filename(without extension) and the extension
    filename_without_ext = filename[:last_dot_in_filename]
    extension = filename[last_dot_in_filename+1:]
    if extension not in ['jpg', 'gif', 'png', 'jpeg', 'jpg']:
        return upload_fail(message='Images only!')
    # get the absolute image path for the new image
    image_path = join(current_app.config['UPLOAD_DIRECTORY'], filename)
    current_app.logger.info(image_path)
    # deal with duplicated filenames
    while exists(image_path):
        filename_without_ext += '_'  # add underscores after the existed filename
        image_path = join(
            current_app.config['UPLOAD_DIRECTORY'],
            filename_without_ext + '.' + extension
        )
    # get final filename
    filename = filename_without_ext + '.' + extension
    current_app.logger.info(f'Upload file {filename} saved.')
    fileobj.save(image_path)
    # commit the image to the db
    image = Image(filename=filename, author=current_user)
    db.session.add(image)
    db.session.commit()
    url = image.url()
    current_app.logger.info(f'Upload file url: {url}')
    return upload_success(url=url, filename=filename)


@image_bp.route('/manage/')
@login_required
def manage_images():
    page = request.args.get('page', 1, int)
    if not current_user.is_administrator():
        pagination = current_user.images.order_by(Image.timestamp.desc()).paginate(
            page, per_page=current_app.config['IMAGES_PER_PAGE']
        )
    else:
        pagination = Image.query.order_by(Image.timestamp.desc()).paginate(
            page, per_page=current_app.config['IMAGES_PER_PAGE']
        )
    images = pagination.items
    return render_template('image/manage_images.html', pagination=pagination, images=images)


@image_bp.route('/toggle/<int:id>/', methods=['POST'])
@login_required
def toggle_image_visibility(id: int):
    image = Image.query.get(id)
    if image.author != current_user and not current_user.is_administrator():
        abort(403)
    image.private = not image.private
    db.session.commit()
    flash(_("Image {filename} visibility toggled".format(filename=image.filename)))
    return make_response(redirect_back())


@image_bp.route('/delete/<int:id>/', methods=['POST'])
@login_required
def delete_image(id: int):
    image = Image.query.get(id)
    if image.author != current_user and not current_user.is_administrator():
        abort(403)
    filename = image.filename
    os.remove(image.path())
    db.session.delete(image)
    db.session.commit()
    flash(_("Image {filename} deleted".format(filename=filename)))
    return make_response(redirect_back())

