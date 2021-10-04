from flask_login import login_required, current_user
from datetime import datetime, timedelta
from flask import redirect, flash, url_for

from ..models import db, User, Belong, items
from . import shop_bp


@shop_bp.route('/')
@login_required
def shop_index():
    return 'welcome to shop!'

@shop_bp.route('/buy/<int:id>')
@login_required
def buy(id):
    try:
        if not Belong.query.filter_by(owner_id=current_user.id, goods_id=id).scalar():
            ownership = Belong(
                owner_id = current_user.id,
                goods_id = id,
                expires = items(id)['expires'] + datetime.utcnow()
            )
            current_user.coins -= items(id)['price']
            db.session.add(ownership)
            db.session.commit()
            return {
                "owner_id" : current_user.id,
                "goods_id" : id,
                "expires" : (items(id)['expires'] + datetime.utcnow()).__str__(),
                "coins": current_user.coins,
                "belongings": [str(i) for i in current_user.load_belongings()]
            }
        return {
            "status": "does exists!",
            "coins": current_user.coins,
            "belongings": [str(i) for i in current_user.load_belongings()],
        }
    except KeyError:
        return {
            "status": "goods do not exist!",
            "coins": current_user.coins,
            "belongings": [str(i) for i in current_user.load_belongings()],
        }

@shop_bp.route('/yours')
@login_required
def yours():
    return {
        "yours": [str(i) for i in current_user.load_belongings()]
    }

@shop_bp.route('/use/<int:id>')
@login_required
def use(id):
    if id not in [i.goods_id for i in current_user.load_belongings()]:
        flash("You haven't buy this yet!")
        return redirect(url_for('main.main'))
    else:
        current_user.avatar_style_id = id
        try:
            if current_user.load_avatar_style() is not None:
                db.session.commit()
                if current_user.avatar_style_id == id:
                    flash("Success! Check out at your avatar!")
                else:
                    flash("Bad id!")
        except:
            flash("Not so good!")
    return redirect(url_for('main.main'))

@shop_bp.route('/add')
def add():
    admin = User.query.filter_by(username='flog_admin').first_or_404()
    admin.coins += 1000
    db.session.commit()
    return str(admin.coins)

# note that moderator permission do not have access to users' belongings.