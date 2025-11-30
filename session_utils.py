from flask import session


def get_form_and_errors():
    form_data = session.pop("form_data", {})
    errors = session.pop("errors", {})
    return form_data, errors


def set_form_and_errors(form_data, errors):
    session["form_data"] = form_data
    session["errors"] = errors
