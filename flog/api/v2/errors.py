from . import api_v2
from flog.errors import api_err_response


def bad_request(message):
    return api_err_response(400, "bad request", message)


def unauthorized(message):
    return api_err_response(401, "unauthorized", message)


def forbidden(message):
    return api_err_response(403, "forbidden", message)


def invalid_token():
    response = unauthorized("invalid token")
    response.headers["WWW-Authenticate"] = "Bearer"
    return response


class ValidationError(ValueError):
    pass


@api_v2.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
