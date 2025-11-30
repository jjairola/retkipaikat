from flask import Flask, abort
from flask import flash, redirect, render_template, request, session
import secrets
import config
import users
import destinations
import validator
import session_utils

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


@app.route("/")
def index():
    destinations_list = destinations.get_destinations()
    print(destinations_list)
    return render_template("index.html", destinations=destinations_list)

@app.route("/find-destination")
def find_destination():
    classes = destinations.get_all_classes()

    print(dict(classes))

    query_text = request.args.get("query", "")
    query_class = request.args.get("class", "")

    results = []
    if query_text:
        results = destinations.search_destinations_by_query(query_text)
    elif query_class:
        title, value = query_class.split(":", 1)
        results = destinations.get_destinations_by_class(title, value)

    return render_template(
        "find_destination.html",
        classes=classes,
        query=query_text,
        results=results,
    )

@app.route("/destination/<int:destination_id>")
def destination_page(destination_id):
    destination = destinations.get_destination(destination_id)
    classes = destinations.get_destination_classes(destination_id)
    comments = destinations.get_comments(destination_id)

    print(dict(classes))

    if not destination:
        abort(404)
    return render_template("show_destination.html", destination=destination, classes=classes, comments=comments)


@app.route("/add-destination", methods=["GET", "POST"])
def add_destination():
    require_login()
    all_classes = destinations.get_all_classes()
    schema = {
        "name": {"required": True, "translation": "Nimi", "min": 10, "max": 50},
        "description": {"required": True, "translation": "Kuvaus", "max": 1000},
        "municipality": {
            "required": True,
            "translation": "Kunta",
        },
        "classes": {
            "require": {
                "required_types": ["Tyyppi", "Vaikeusaste"],
                "all_classes": all_classes,
            }
        },
    }

    if request.method == "GET":
        form_data, errors = session_utils.get_form_and_errors()

        return render_template(
            "add_destination.html",
            classes=all_classes,
            form_data=form_data,
            errors=errors,
            schema=validator.schema_to_input(schema),
        )

    if request.method == "POST":
        check_csrf()

        print("Adding destination with data:", request.form )

        validated, errors = validator.validator(request.form, schema)
        if errors:
            print("errors")
            print(errors)
            flash("Lomakkeen tiedot eivät kelpaa", "error")
            session_utils.set_form_and_errors(validated, errors)
            return redirect("/add-destination")

        print("validated")
        print(validated)

        try:
            destinations.add_destination(
                validated["name"],
                validated["description"],
                validated["municipality"],
                session["user_id"],
                validated["classes"],
            )
            flash("Retkipaikka lisätty onnistuneesti.")
            return redirect("/")
        except Exception as e:
            print(e)
            flash("Virhe retkipaikan lisäämisessä.", "error")
            return redirect("/add-destination")


@app.route("/destination/<int:destination_id>/edit", methods=["GET", "POST"])
def edit_destination(destination_id):
    require_login()
    destination = destinations.get_destination(destination_id)

    if not destination or destination["user_id"] != session["user_id"]:
        abort(403)

    all_classes = destinations.get_all_classes()
    schema = {
        "name": {"required": True, "translation": "Nimi", "min": 10, "max": 50},
        "description": {"required": True, "translation": "Kuvaus", "max": 1000},
        "municipality": {
            "required": True,
            "translation": "Kunta",
        },
        "classes": {
            "require": {
                "required_types": ["Tyyppi", "Vaikeusaste"],
                "all_classes": all_classes,
            }
        },
    }

    if request.method == "GET":
        current_classes = destinations.get_destination_classes(destination_id)

        return render_template(
            "edit_destination.html",
            classes=all_classes,
            form_data=destination,
            schema=validator.schema_to_input(schema),
            current_classes=current_classes,
        )

    if request.method == "POST":
        check_csrf()
        validated, errors = validator.validator(request.form, schema)

        print("error")
        print(errors)
        print("validated")
        print(validated)

        if errors:
            flash("Lomakkeen tiedot eivät kelpaa", "error")
            session_utils.set_form_and_errors(validated, errors)
            return redirect(f"/destination/{destination_id}/edit")

        try:
            destinations.update_destination(
                destination_id,
                validated["name"],
                validated["description"],
                validated["municipality"],
                validated["classes"],
            )
            flash("Retkipaikka päivitetty.")
            return redirect(f"/destination/{destination_id}")
        except Exception as e:
            #flash("Virhe retkipaikan päivityksessä.", "error")
            flash(e)
            return redirect(f"/destination/{destination_id}/edit")


@app.route("/destination/<int:destination_id>/delete", methods=["GET", "POST"])
def delete_destination(destination_id):
    require_login()
    destination = destinations.get_destination_by_id(destination_id)
    if not destination or destination["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_destination.html", destination=destination)

    if request.method == "POST":
        try:
            destinations.delete_destination(destination_id)
            flash("Retkipaikka poistettu.")
            return redirect("/")
        except Exception:
            flash("Virhe retkipaikan poistamisessa.", "error")
            return redirect(f"/destination/{destination_id}")


@app.route("/register", methods=["GET", "POST"])
def register():
    schema = {
        "username": {
            "required": True,
            "translation": "Käyttäjätunnus",
            "min": 5,
            "max": 20,
            "word_count": 1,
        },
        "password1": {"required": True, "translation": "Salasana", "min": 8, "max": 20},
        "password2": {
            "required": True,
            "translation": "Vahvista salasana",
            "min": 8,
            "max": 20,
            "equals": "password1",
        },
    }
    if request.method == "GET":
        form_data, errors = session_utils.get_form_and_errors()
        return render_template(
            "register.html",
            form_data=form_data,
            errors=errors,
            schema=validator.schema_to_input(schema),
        )

    if request.method == "POST":
        validated, errors = validator.validator(request.form, schema)
        if errors:
            flash("Lomakkeen tiedot eivät kelpaa", "error")
            session_utils.set_form_and_errors(validated, errors)
            return redirect("/register")

        try:
            users.create_user(validated["username"], validated["password1"])
            flash("Käyttäjätili luotu. Voit kirjautua sisään!")
            return redirect("/login")

        except users.UserError:
            flash("Rekisteröitymisessä tapahtui virhe.", "error")
            return redirect("/register")


@app.route("/login", methods=["GET", "POST"])
def login():
    schema = {
        "username": {
            "required": True,
            "translation": "Käyttäjätunnus",
            "min": 5,
            "max": 20,
            "word_count": 1,
        },
        "password": {
            "required": True,
            "translation": "Salasana",
            "min": 8,
            "max": 20,
        },
    }

    if request.method == "GET":
        form_data, errors = session_utils.get_form_and_errors()
        return render_template(
            "login.html",
            form_data=form_data,
            errors=errors,
            schema=validator.schema_to_input(schema),
        )

    if request.method == "POST":
        validated, errors = validator.validator(request.form, schema)
        if errors:
            flash("Lomakkeen tiedot eivät kelpaa", "error")
            session_utils.set_form_and_errors(validated, errors)
            return redirect("/login")

        user_id = users.check_login(validated["username"], validated["password"])
        if user_id:
            session["user_id"] = user_id
            session["username"] = validated["username"]
            session["csrf_token"] = secrets.token_hex(16)
            flash("Kirjautuminen onnistui.")
            return redirect("/profile")
        else:
            flash("Väärä tunnus tai salasana", "error")
            return redirect("/login")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")


@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    destination_id = request.form.get("destination_id")
    comment = request.form.get("comment")

    schema = {
        "comment": {"required": True, "translation": "Kommentti", "max": 1000},
        "destination_id": {"required": True}
    }

    validated, errors = validator.validator(request.form, schema)
    if errors:
        flash("Virhe kommentissa", "error")
        return redirect(f"/destination/{destination_id}")

    try:
        destinations.add_comment(int(validated["destination_id"]), session["user_id"], validated["comment"], 0)
        flash("Kommentti lisätty.")
    except Exception as e:
        print(e)
        flash("Virhe kommentin lisäämisessä.", "error")

    return redirect(f"/destination/{destination_id}")


@app.route("/profile")
def profile():
    require_login()
    user_destinations = destinations.get_destinations_by_user(session["user_id"])
    comments = destinations.get_comments_by_user(session["user_id"])
    return render_template("profile.html", destinations=user_destinations, comments=comments)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
