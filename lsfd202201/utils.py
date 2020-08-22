# flake8: noqa
from urllib.parse import urlparse, urljoin
from functools import wraps
import requests
from flask import redirect, session, url_for, current_app, request
from werkzeug.security import check_password_hash
from markdown import markdown
from .models import User

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'admin' not in session or not session['admin']:
            return redirect(url_for('admin.login'))
        return func(*args, **kwargs)
    return wrapper


def check_article_password(password: str) -> bool:
    if (check_password_hash(current_app.config['ARTICLE_PASSWORD_HASH'], password) or
            check_password_hash(current_app.config['ADMIN_PASSWORD_HASH'], password)):
        return True
    return False


def check_admin_login(password: str, name) -> bool:
    try:
        admin = User.query.filter_by(name=name).first()
        return admin.verify_password(password)
    except:
        return False


def get_html_from(url: str) -> str:
    response = requests.get(url)
    return markdown(response.text)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.main', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
