from flask import Flask, abort
from flask import flash, redirect, render_template, request, session
import secrets
import config
import users
import destinations
import validator
import session as session_utils

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    destinations_list = destinations.get_destinations()
    return render_template("index.html", destinations=destinations_list)


@app.route("/add-destination", methods=["GET", "POST"])
def add_destination():
    require_login()

    if request.method == "GET":
        classifications = destinations.get_all_classifications()
        return render_template("add_destination.html", classifications=classifications)

    if request.method == "POST":
        schema = {
            "name": {"is_required": True, "translation": "Nimi"},
            "description": {"is_required": True, "translation": "Kuvaus"},
            "municipality": {"is_required": True, "translation": "Kunta"},
        }
        errors = validator.validator(request.form, schema)
        if errors:
            for error in errors.values():
                flash(error, ", ".join(errors.values()))
            return redirect("/add-destination")

        name = request.form["name"]
        description = request.form["description"]
        municipality = request.form["municipality"]
        classification_ids = request.form.getlist("classifications")

        if not name or not description or not municipality:
            flash("Kaikki kentät ovat pakollisia.", "error")
            return redirect("/add-destination")

        try:
            destinations.add_destination(
                name, description, municipality, session["user_id"], classification_ids
            )
            flash("Retkipaikka lisätty onnistuneesti.")
            return redirect("/")
        except Exception as e:
            flash("Virhe retkipaikan lisäämisessä.", "error")
            return redirect("/add-destination")


@app.route("/find-destination")
def find_destination():
    classifications = destinations.get_all_classifications()
    query = request.args.get("query", "")
    classification_id = request.args.get("classification")

    results = []
    if query:
        results = destinations.search_destinations_by_query(query)
    elif classification_id:
        results = destinations.get_destinations_by_classification(classification_id)

    return render_template(
        "find_destination.html",
        classifications=classifications,
        query=query,
        results=results,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        form_data, errors = session_utils.get_form_and_errors()
        return render_template("register.html", form_data=form_data, errors=errors)

    if request.method == "POST":
        schema = {
            "username": {"is_required": True, "translation": "Käyttäjätunnus"},
            "password1": {"is_required": True, "translation": "Salasana"},
            "password2": {"is_required": True, "translation": "Vahvista salasana"},
        }
        validated, errors = validator.validator(request.form, schema)
        if errors:
            flash("Lomakkeen tiedot eivät kelpaa", "error")
            session_utils.set_form_and_errors(validated, errors)
            return redirect("/register")

        try:
            users.create_user(validated["username"], validated["password1"])
            flash("Käyttäjätili luotu. Voit kirjautua sisään!")
        except users.UserError:
            flash("Rekisteröityinen ei kelpaava.", "error")
            return redirect("/register")

        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            flash("Kirjautuminen onnistui.")
            return redirect("/")
        else:
            flash("Väärä tunnus tai salasana", "error")
            return redirect("/login")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")


@app.route("/destination/<int:destination_id>")
def destination_page(destination_id):
    destination = destinations.get_destination_by_id(destination_id)
    if not destination:
        abort(404)
    return render_template("destination.html", destination=destination)


@app.route("/destination/<int:destination_id>/edit", methods=["GET", "POST"])
def edit_destination(destination_id):
    require_login()
    destination = destinations.get_destination_by_id(destination_id)
    if not destination or destination["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        classifications = destinations.get_all_classifications()
        current_classifications = destinations.get_destination_classifications_ids(
            destination_id
        )
        return render_template(
            "edit_destination.html",
            destination=destination,
            classifications=classifications,
            current_classifications=current_classifications,
        )

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        municipality = request.form["municipality"]
        classifications_selected = request.form.getlist("classifications")

        if not name or not description or not municipality:
            flash("Kaikki kentät ovat pakollisia.", "error")
            return redirect(f"/destination/{destination_id}/edit")

        try:
            destinations.update_destination(
                destination_id,
                name,
                description,
                municipality,
                classifications_selected,
            )
            flash("Retkipaikka päivitetty.")
            return redirect(f"/destination/{destination_id}")
        except Exception as e:
            flash("Virhe retkipaikan päivityksessä.", "error")
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
        except Exception as e:
            flash("Virhe retkipaikan poistamisessa.", "error")
            return redirect(f"/destination/{destination_id}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
