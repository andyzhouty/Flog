from flask import jsonify
from . import api_v2


def bad_request(message):
    response = jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({"error": "unauthorized", "message": message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


def invalid_token():
    response = jsonify(
        {
            "error": "invalid_token",
            "message": "Either the token was expired or invalid.",
        }
    )
    response.status_code = 401
    response.headers["WWW-Authenticate"] = "Bearer"
    return response


def token_missing():
    response = unauthorized("Token missing")
    response.headers["WWW-Authenticate"] = "Bearer"
    return response


class ValidationError(ValueError):
    pass


@api_v2.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
