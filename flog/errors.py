"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import render_template, request, abort
from flask.json import jsonify
from flask_wtf.csrf import CSRFError
from flask_babel import _


def api_err_response(err_code: int, short_message: str, long_message: str = None):
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
        return response
    return None  # explicitly return None


def err_handler(
    err_code: int,
    short_message: str,
    long_message: str,
    error_description: str,
    template: str = "errors/error.html",
):
    json_response = api_err_response(err_code, short_message)
    if json_response is not None:
        return json_response
    return (
        render_template(
            template, error_message=long_message, error_description=error_description
        ),
        err_code,
    )


def register_error_handlers(app):  # noqa: C901
    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(e):
        return err_handler(
            400,
            "bad request",
            "400 Bad Request",
            "You have sent an invalid request. This can either be caused by a false CSRF-token or an invalid value of a form.",
        )

    @app.errorhandler(403)
    def forbidden(e):
        return err_handler(
            403,
            "forbidden",
            "403 Forbidden",
            "You do not have the permission to access this page. Maybe you are not signed in (viewing posts directly), or you tried to enter a page where you aren't allowed to enter.",
        )

    @app.errorhandler(404)
    def page_not_found(e):
        return err_handler(
            404,
            "not found",
            "404 Not Found",
            "The page you want is not here or deleted.",
            "errors/404.html",
        )

    @app.errorhandler(405)
    def method_not_allowed(e):
        return err_handler(
            405,
            "method not allowed",
            "405 Method Not Allowed",
            "Your request has a wrong method. Maybe you entered some page without a form submission.",
        )

    @app.errorhandler(413)
    def payload_to_large(e):
        return err_handler(
            413,
            "request entity too large",
            "413 Request Entity Too Large",
            "Things you upload is too large.",
        )

    @app.errorhandler(429)  # handle when IP is limited
    def too_many_requests(e):
        return err_handler(
            429,
            "too many requests",
            "429 Too Many Requests",
            "You see 429 because you entered a page too many times and triggered our self-protection program. Usually you can wait for a while, in some cases it takes a day.",
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        return err_handler(
            500,
            "internal server error",
            "500 Internal Server Error",
            "The server went wrong and returned 500. You can contact them to report this 500 error.",
        )
