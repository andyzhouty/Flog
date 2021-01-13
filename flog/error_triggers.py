from flask import abort, Flask


def trigger_error(err_code: int, testing: bool):
    if testing:
        abort(err_code)
    else:
        abort(404)


def register_error_triggers(app: Flask):
    testing = app.testing

    @app.route("/400")
    def trigger_bad_request():
        trigger_error(400, testing)

    @app.route("/403")
    def trigger_forbidden():
        trigger_error(403, testing)

    @app.route("/404")
    def trigger_not_found():
        trigger_error(404, testing)

    @app.route("/405")
    def trigger_method_not_allowed():
        trigger_error(405, testing)

    @app.route("/413")
    def trigger_payload_too_large():
        trigger_error(413, testing)

    @app.route("/500")
    def trigger_server_error():
        trigger_error(500, testing)
