from flask import render_template
from flask_wtf.csrf import CSRFError
from flask_babel import _


def register_error_handlers(app):
    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(e):
        return render_template('errors/error.html',
                               error_message=_("400 Bad Request")), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/error.html',
                               error_message=_("403 You do not have the permission to access this page")), 403

    @app.errorhandler(404)
    def page_not_found(e):
        # special easter egg :P
        return render_template('errors/404.html',
                               error_message=_("404 Not Found")), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('errors/error.html',
                               error_message=_("405 Method Not Allowed")), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/error.html',
                               error_message=_("500 Internal Server Error")), 500
