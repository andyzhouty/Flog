from ..models import User, db

for user in User.query.all():
    user.ping_update_ai()
