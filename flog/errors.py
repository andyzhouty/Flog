"""
MIT License
Copyright(c) 2020 Andy Zhou
"""
from flask import render_template, request
from flask.json import jsonify
from flask_wtf.csrf import CSRFError
from flask_babel import _


def api_error_handler(
        err_code: int,
        short_message: str,
        long_message: str = None,
        headers: dict = None
):
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
        or request.blueprint == "api_v1"
        or request.blueprint == "api_v2"
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


def register_error_handlers(app):
    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(e):
        json_response = api_error_handler(400, "bad request")
        if json_response is not None:
            return json_response
        return (
            render_template("errors/error.html", error_message=_("400 Bad Request")),
            400,
        )

    @app.errorhandler(403)
    def forbidden(e):
        json_response = api_error_handler(403, "forbidden")
        if json_response is not None:
            return json_response
        return (
            render_template(
                "errors/error.html",
                error_message=_(
                    "403 You do not have the permission to access this page"
                ),
            ),
            403,
        )

    @app.errorhandler(404)
    def page_not_found(e):
        json_response = api_error_handler(404, "not found")
        if json_response is not None:
            return json_response
        # special easter egg :P
        return render_template("errors/404.html", error_message=_("404 Not Found")), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        json_response = api_error_handler(405, "method not allowed")
        if json_response is not None:
            return json_response
        return (
            render_template(
                "errors/error.html", error_message=_("405 Method Not Allowed")
            ),
            405,
        )

    @app.errorhandler(413)
    def payload_to_large(e):
        json_response = api_error_handler(413, "image file too large")
        if json_response is not None:
            return json_response
        return (
            render_template(
                "errors/error.html",
                error_message=_("The file you uploaded was larger than the 1M limit"),
            ),
            413,
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        json_response = api_error_handler(500, "internal server error")
        if json_response is not None:
            return json_response
        return (
            render_template(
                "errors/error.html", error_message=_("500 Internal Server Error")
            ),
            500,
        )
