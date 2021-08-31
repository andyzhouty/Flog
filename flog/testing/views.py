"""
MIT License
Copyright(c) 2021 Andy Zhou
"""
from flask import abort
from . import testing_bp
from flog.utils import redirect_back


@testing_bp.route("/400")
def trigger_bad_request():
    abort(400)


@testing_bp.route("/403")
def trigger_forbidden():
    abort(403)


@testing_bp.route("/404")
def trigger_not_found():
    abort(404)


@testing_bp.route("/405")
def trigger_method_not_allowed():
    abort(405)


@testing_bp.route("/413")
def trigger_payload_too_large():
    abort(413)


@testing_bp.route("/429")
def trigger_too_many_requests():
    abort(429)


@testing_bp.route("/500")
def trigger_server_error():
    abort(500)


@testing_bp.route("/redirect")
def trigger_redirect_back():
    return redirect_back("main.main", next="example.com")
