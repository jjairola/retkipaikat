from flask import abort, session, request
import markupsafe


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
