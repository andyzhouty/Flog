from flask import render_template
from . import ajax_bp
from ..models import User


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('ajax/profile_popup.html', user=user)

