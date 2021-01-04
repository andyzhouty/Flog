"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
from urllib.parse import urlparse, urljoin
from flask import redirect, url_for, request


def lower_username(username: str) -> str:
    """Returns lowered username"""
    return username.strip().lower().replace(" ", "")


def is_safe_url(target):
    """Check if target url is safe"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="main.main", **kwargs):
    """Redirect back"""
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
