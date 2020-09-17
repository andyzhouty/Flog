from flask import url_for, flash, redirect, request, render_template, abort
from flask.globals import current_app
from flask_login import login_user, logout_user, login_required
from flask_login.utils import current_user
from . import auth_bp
from .forms import DeleteAccountForm, LoginForm, RegisterationForm
from ..models import User, db
from ..emails import send_email


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.main'))
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    name=form.name.data,
                    username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        try:
            if not current_app.config['TESTING']:
                token = user.generate_confirmation_token()
                send_email([user.email], 'Confirm your account', 'auth/email/confirm', user=user, token=token)
                flash("A confirmation email has been sent to you by email! You can now login!", "info")
                return redirect(url_for('auth.login'))
            else:
                flash('You can now login!', "success")
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
        user_by_username = User.query.filter_by(username=form.username_or_email.data).first()
        user_by_email = User.query.filter_by(email=form.username_or_email.data.lower()).first()
        user = user_by_username if user_by_username is not None else user_by_email
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
        flash('You have confirmed your account. Thanks !', "success")
    else:
        flash('The confirmation link is invalid or has expired', "warning")
    return redirect(url_for('main.main'))


@auth_bp.route('/confirm/')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email([current_user.email], 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email', 'info')
    return redirect(url_for('main.main'))


@auth_bp.route('/delete-account/', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.delete()
            flash('Your account has been deleted', 'info')
        else:
            flash('Your password is invalid!', 'warning')
        return redirect(url_for('main.main'))
    return render_template('auth/delete_account.html', form=form)
