"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import render_template, request
from flask.json import jsonify
from flask_wtf.csrf import CSRFError
from flask_babel import _


def register_error_handlers(app):
    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'bad request'})
            response.status_code = 400
            return response
        return render_template('errors/error.html',
                               error_message=_("400 Bad Request")), 400

    @app.errorhandler(403)
    def forbidden(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'forbidden'})
            response.status_code = 403
            return response
        return render_template('errors/error.html',
                               error_message=_("403 You do not have the permission to access this page")), 403

    @app.errorhandler(404)
    def page_not_found(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'not found'})
            response.status_code = 404
            return response
        # special easter egg :P
        return render_template('errors/404.html',
                               error_message=_("404 Not Found")), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'method not allowed'})
            response.status_code = 405
            return response
        return render_template('errors/error.html',
                               error_message=_("405 Method Not Allowed")), 405

    @app.errorhandler(413)
    def payload_to_large(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'payload to large'})
            response.status_code = 413
            return response
        return render_template('errors/error.html',
                               error_message=_("The file you uploaded was TOO"
                                               "large (larger than 1M)")), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        if (request.accept_mimetypes.accept_json and
                not request.accept_mimetypes.accept_html):
            response = jsonify({'error': 'internal server error'})
            response.status_code = 500
            return response
        return render_template('errors/error.html',
                               error_message=_("500 Internal Server Error")), 500
