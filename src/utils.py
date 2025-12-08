import re
import math
import secrets
from flask import abort, session, request
import markupsafe
import config

def is_username_valid_characters(username):
    return bool(re.match(r'^[A-Za-z0-9]+$', username))

def page_count(items):
    pages = math.ceil(items / config.PAGE_SIZE)
    pages = max(pages, 1)
    return pages, config.PAGE_SIZE

def generate_csrf_token():
    return secrets.token_hex(16)


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# template filter
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)
