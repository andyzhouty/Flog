from flask_login import login_required, current_user
from datetime import datetime
from flask import redirect, flash, url_for, render_template, request

from ..models import db, Belong, items
from . import shop_bp


@shop_bp.route("/")
@login_required
def shop_index():
    filter_ = "all"
    if request.args.get("filter") is not None:
        filter_ = request.args.get("filter")
        if filter_ == "yours":
            goods = {
                current_user.load_belongings_id()[i]: items(
                    current_user.load_belongings_id()[i]
                )
                for i in range(len(current_user.load_belongings()))
            }
        else:
            goods = {i + 1: items(i + 1) for i in range(items(0, "len") - 1)}
    else:
        goods = {i + 1: items(i + 1) for i in range(items(0, "len") - 1)}
    return render_template("shop/main.html", goods=goods, filter=filter_)


@shop_bp.route("/buy/<int:id>")
@login_required
def buy(id):
    try:
        if id == 0:
            raise KeyError(0)
        belong: Belong = Belong.query.filter_by(
            owner_id=current_user.id, goods_id=id
        ).first()
        if not belong or belong.load_expiration_delta().seconds > 0:
            if (
                items(id).exp <= current_user.experience
                and current_user.experience >= 200
            ):
                if items(id).price <= current_user.coins:
                    ownership = Belong(
                        owner_id=current_user.id,
                        goods_id=id,
                        expires=items(id).expires + datetime.utcnow(),
                    )
                    current_user.coins -= items(id).price
                    current_user.experience -= 200
                    db.session.add(ownership)
                    db.session.commit()
                    flash("Success! Use it and check out!")
                else:
                    flash("You don't have enough coins!")
            else:
                flash("Your experience is not enough!")
        else:
            flash("You have this already, and you don't have to get it a second time!")
    except KeyError:
        flash("Well... are you sure that this item exists?")
    return redirect(url_for("shop.shop_index"))


@shop_bp.route("/yours")
@login_required
def yours():
    return {"yours": [str(i) for i in current_user.load_belongings()]}


@shop_bp.route("/use/<int:id>")
@login_required
def use(id):
    if id not in [i.goods_id for i in current_user.load_belongings()]:
        flash("You haven't buy this yet!")
        return redirect(url_for("main.main"))
    else:
        current_user.avatar_style_id = id
        try:
            if current_user.load_avatar_style() is not None:
                db.session.commit()
                if current_user.avatar_style_id == id:
                    flash("Success! Now you can check out at your avatar!")
                else:
                    flash("Well... This is a bad ID.")
        except:
            flash("Failure. Please try again!")
    return redirect(url_for("shop.shop_index"))


# note that moderator permission do not have access to users' belongings.
# and also, only consoles have access to users' belongings, but it is not so easy to get them!
