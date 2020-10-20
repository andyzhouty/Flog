"""
MIT License
Copyright (c) 2020 Andy Zhou
"""
import re
import requests
import markdown
from urllib.parse import urlparse, urljoin
from unidecode import unidecode
from flask import redirect, url_for, request


_punct_re = re.compile(r'[\t !"#$%&\]\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates ASCII slugs"""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).lower().split())
    return unidecode(delim.join(result))

def is_safe_url(target):
    """Check if target url is safe"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.main', **kwargs):
    """Redirect back"""
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def get_markdown(url: str) -> 'markdown_str':
    return requests.get(url).text

def convert_to_html(markdown_str: str) -> 'html_str':
    return markdown.markdown(markdown_str)
