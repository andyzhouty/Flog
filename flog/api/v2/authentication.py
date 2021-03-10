from flog.api.v2.errors import bad_request, invalid_token
from functools import wraps
from flask import g, request
from flog.models import User


def get_token():
    if "Authorization" in request.headers:
        try:
            token_type, token = request.headers["Authorization"].split(None, 1)
        except ValueError:  # Header authorization is empty or token is empty
            token_type = None
            token = None
    else:
        token_type = None
        token = None
    return token_type, token


def validate_token(token):
    user = User.verify_auth_token_api(token)
    if user is None:
        return False
    g.current_user = user
    return True


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_type, token = get_token()

        if request.method != "OPTIONS":
            if token_type is None or token is None or token_type.lower() != "bearer":
                return bad_request(
                    "The token type must be bearer and the token must not be none."
                )
            if not validate_token(token):
                return invalid_token()
        return f(*args, **kwargs)

    return decorated
