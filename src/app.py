from flask import Flask, abort, url_for
from flask import flash, redirect, render_template, request, session
import utils
import secrets
import config
import users
import destinations
import comments
import math
import ratings_cache

app = Flask(__name__)
app.secret_key = config.secret_key
app.add_template_filter(utils.show_lines, name="show_lines")


@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    destination_count = destinations.destination_count()
    page_count = math.ceil(destination_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    destinations_list = destinations.get_destinations(page=page, page_size=page_size)
    return render_template(
        "index.html", destinations=destinations_list, page=page, page_count=page_count
    )


@app.route("/search-destination")
def search_destination():
    classes = destinations.get_all_classes()

    query_text = request.args.get("query", "")
    query_class = request.args.get("class", "")

    results = []
    if query_text:
        results = destinations.search_destinations_by_query(query_text)
    elif query_class:
        title, value = query_class.split(":", 1)
        results = destinations.search_destionations_by_class(title, value)

    return render_template(
        "search_destination.html",
        classes=classes,
        query=query_text,
        results=results,
    )


@app.route("/destination/<int:destination_id>")
def get_destination(destination_id):
    destination = destinations.get_destination(destination_id)
    classes = destinations.get_destination_classes(destination_id)
    comments_list = comments.get_comments(destination_id)

    if not destination:
        abort(404)
    return render_template(
        "show_destination.html",
        destination=destination,
        classes=classes,
        comments=comments_list,
    )


@app.route("/destination/add", methods=["GET", "POST"])
def add_destination():
    utils.require_login()
    all_classes = destinations.get_all_classes()

    if request.method == "GET":
        return render_template(
            "add_destination.html",
            classes=all_classes,
            destination=None,
            current_classes={},
        )

    if request.method == "POST":
        utils.check_csrf()

        name = request.form.get("name")
        if not name or len(name) < 5 or len(name) > 80:
            flash("Nimen pitää olla 5-80 merkkiä pitkä.", "error")
            return redirect(url_for("add_destination"))

        description = request.form.get("description")
        if not description or len(description) < 10 or len(description) > 500:
            flash("Kuvauksen pitää olla 10-500 merkkiä pitkä.", "error")
            return redirect(url_for("add_destination"))

        municipality = request.form.get("municipality")
        if not municipality:
            flash("Paikkakunta ei voi olla tyhjä.", "error")
            return redirect(url_for("add_destination"))

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                classes.append((class_title, class_value))

        try:
            destination_id = destinations.add_destination(
                name,
                description,
                municipality,
                session["user_id"],
                classes,
            )
            flash("Retkipaikka lisätty onnistuneesti.")
            return redirect(url_for("get_destination", destination_id=destination_id))
        except Exception:
            flash("Virhe retkipaikan lisäämisessä.", "error")
            return redirect(url_for("add_destination"))


@app.route("/destination/<int:destination_id>/edit", methods=["GET", "POST"])
def edit_destination(destination_id):
    utils.require_login()
    destination = destinations.get_destination(destination_id)

    if not destination or destination["user_id"] != session["user_id"]:
        abort(403)

    all_classes = destinations.get_all_classes()

    if request.method == "GET":
        current_classes = destinations.get_destination_classes(destination_id)

        return render_template(
            "edit_destination.html",
            classes=all_classes,
            destination=destination,
            current_classes=current_classes,
        )

    if request.method == "POST":
        utils.check_csrf()

        actions = request.form.get("action")
        if actions == "cancel":
            return redirect(url_for("get_destination", destination_id=destination_id))

        name = request.form.get("name")
        description = request.form.get("description")
        municipality = request.form.get("municipality")

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                classes.append((class_title, class_value))

        try:
            destinations.update_destination(
                destination_id,
                name,
                description,
                municipality,
                classes,
            )
            flash("Retkipaikka päivitetty.")
            return redirect(url_for("get_destination", destination_id=destination_id))
        except Exception:
            flash("Virhe retkipaikan päivityksessä.", "error")
            return redirect(url_for("edit_destination", destination_id=destination_id))


@app.route("/destination/<int:destination_id>/delete", methods=["GET", "POST"])
def delete_destination(destination_id):
    utils.require_login()
    destination = destinations.get_destination(destination_id)
    if not destination or destination["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_destination.html", destination=destination)

    if request.method == "POST":
        utils.check_csrf()

        action = request.form.get("action")
        if action == "cancel":
            return redirect(url_for("get_destination", destination_id=destination_id))

        try:
            destinations.delete_destination(destination_id)
            flash("Retkipaikka poistettu.")
            return redirect("/")
        except Exception:
            flash("Virhe retkipaikan poistamisessa.", "error")
            return redirect(url_for("get_destination", destination_id=destination_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if len(username) < 5 or len(username) > 20:
            flash("Käyttäjätunnuksen oltava 5-20 merkkiä pitkä.", "error")
            return render_template("register.html", filled={"username": username})

        if password1 != password2:
            flash("Salasanat eivät täsmää.", "error")
            return render_template("register.html", filled={"username": username})

        if len(password1) < 8 or len(password1) > 20:
            flash("Salasanan oltava 8-20 merkkiä pitkä.", "error")
            return render_template("register.html", filled={"username": username})

        try:
            users.add_user(username, password1)
            flash("Käyttäjätili luotu. Voit kirjautua sisään!")
            return redirect(url_for("login"))

        except users.UserError:
            flash("Rekisteröitymisessä tapahtui virhe.", "error")
            return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={})

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            flash("Kirjautuminen onnistui.")
            return redirect(url_for("index"))
        else:
            flash("Väärä tunnus tai salasana", "error")
            return render_template("login.html", filled={"username": username})


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect(url_for("index"))


@app.route("/destination/<int:destination_id>/comments", methods=["POST"])
def add_comment(destination_id):
    utils.require_login()
    utils.check_csrf()

    destination_id = request.form.get("destination_id")
    comment = request.form.get("comment")
    rating = request.form.get("rating")

    if not comment or len(comment) < 1 or len(comment) > 500:
        flash("Kommentin pitää olla 1-500 merkkiä pitkä.", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))

    if not rating or int(rating) < 1 or int(rating) > 5:
        flash("Arvion pitää olla välillä 1-5.", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))
    try:
        comments.add_comment(
            destination_id,
            session["user_id"],
            comment,
            int(rating),
        )
        ratings_cache.update_cache(destination_id)
        flash("Kommentti lisätty.")
    except Exception as e:
        print(e)
        flash("Virhe kommentin lisäämisessä.", "error")

    return redirect(url_for("get_destination", destination_id=destination_id))


@app.route(
    "/destination/<int:destination_id>/comments/<int:comment_id>/delete",
    methods=["GET", "POST"],
)
def delete_comment(destination_id, comment_id):
    utils.require_login()
    comment = comments.get_comment(comment_id)

    if not comment or comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_comment.html", comment=comment)

    if request.method == "POST":
        utils.check_csrf()

        action = request.form.get("action")
        if action == "cancel":
            return redirect(url_for("get_destination", destination_id=destination_id))

        try:
            comments.delete_comment(comment_id)
            ratings_cache.update_cache(destination_id)
            flash("Kommentti poistettu")
        except Exception:
            flash("Virhe kommentin poistamisessa", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))


@app.route("/profile")
def profile():
    utils.require_login()
    user_destinations = destinations.get_destinations(user_id=session["user_id"])
    comments_list = comments.get_comments_by_user(session["user_id"])
    return render_template(
        "profile.html", destinations=user_destinations, comments=comments_list
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if app.debug:
    import time
    from flask import g

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        elapsed_time = round(time.time() - g.start_time, 4)
        print("elapsed time:", elapsed_time, "s")
        return response
