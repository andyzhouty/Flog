"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import render_template, request
from flask.json import jsonify
from flask_wtf.csrf import CSRFError
from flask_babel import _


def api_err_response(
    err_code: int, short_message: str, long_message: str = None, headers: dict = None
):
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
        or request.blueprint == "api_v1"
        or request.blueprint == "api_v2"
        or request.blueprint == "api_v3"
    ):
        response = {"error": short_message}
        if long_message:
            response["message"] = long_message
        response = jsonify(response)
        response.status_code = err_code
        if headers:
            for key, value in headers:
                response.headers[key] = value
        return response
    return None  # explicitly return None


def err_handler(
    err_code: int,
    short_message: str,
    long_message: str,
    template: str = "errors/error.html",
):
    json_response = api_err_response(err_code, short_message)
    if json_response is not None:
        return json_response
    return render_template(template, error_message=long_message), err_code


def register_error_handlers(app):  # noqa: C901
    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(e):
        return err_handler(400, "bad request", _("Bad Request"))

    @app.errorhandler(403)
    def forbidden(e):
        return err_handler(
            403,
            "forbidden",
            _("403 You do not have the permission to access this page"),
        )

    @app.errorhandler(404)
    def page_not_found(e):
        return err_handler(404, "not found", _("404 Not Found"), "errors/404.html")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return err_handler(405, "method not allowed", _("405 Method Not Allowed"))

    @app.errorhandler(413)
    def payload_to_large(e):
        return err_handler(
            413,
            "image file too large",
            _("413 The file you uploaded was larger than the 1M limit"),
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        return err_handler(500, "internal server error", _("500 Internal Server Error"))
