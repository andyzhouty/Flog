from flask import url_for, flash, redirect, request, render_template, abort
from flask_login import login_user, logout_user, login_required
from flask_login.utils import current_user
from . import auth_bp
from .forms import LoginForm, RegisterationForm
from ..models import User, db
from ..emails import send_email


@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    name=form.name.data,
                    username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        try:
            token = user.generate_confirmation_token()
            send_email([user.email], 'Confirm your account', 'auth/email/confirm', user=user, token=token)
            flash("A confirmation email has been sent to you by email!")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.delete(user)
            db.session.commit()
            print(e)
            abort(500)
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.main'))
    form = LoginForm()
    if form.validate_on_submit():
        user_by_name = User.query.filter_by(name=form.name_or_email.data).first()
        user_by_email = User.query.filter_by(email=form.name_or_email.data.lower()).first()
        user = user_by_name if user_by_name is not None else user_by_email
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or next.startswith('/'):
                next = url_for('main.main')
            return redirect(next)
        flash('Invalid username or password!', "danger")
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', "info")
    return redirect(url_for('main.main'))


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.main'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks !')
    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.main'))
