from flask import render_template
from . import user_bp
from ..models import User


@user_bp.route('/<username>/')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile.html', user=user)
