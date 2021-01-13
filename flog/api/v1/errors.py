from . import api_v1
from flog.errors import api_error_handler


def bad_request(message):
    return api_error_handler(400, "bad request", message)


def unauthorized(message):
    return api_error_handler(401, "unauthorized", message)


def forbidden(message):
    return api_error_handler(403, "forbidden", message)


class ValidationError(ValueError):
    pass


@api_v1.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
