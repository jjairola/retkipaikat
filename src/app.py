from flask import Flask, abort, make_response, url_for, g
from flask import flash, redirect, render_template, request, session
import utils
import config
import users
import destinations
import comments
import ratings
import classes

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.add_template_filter(utils.show_lines, name="show_lines")

cache = {}


@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    destination_count = destinations.destination_count()
    page_count, page_size = utils.page_count(destination_count)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    destinations_list = destinations.get_destinations(page=page, page_size=page_size)
    default_icons = classes.get_default_icons()
    return render_template(
        "index.html",
        destinations=destinations_list,
        page=page,
        page_count=page_count,
        default_icons=default_icons,
    )


@app.route("/search-destination")
def search_destination():
    all_classes = classes.get_all_classes_with_count()

    query_text = request.args.get("query", "")
    query_class = request.args.get("class", "")

    results = None
    if query_text:
        results = destinations.search_destinations_by_query(query_text)
    elif query_class:
        title, value = query_class.split(":", 1)
        results = destinations.search_destinations_by_class(title, value)

    return render_template(
        "search_destination.html",
        classes=all_classes,
        query=query_text,
        results=results,
    )


@app.route("/destination/<int:destination_id>")
def get_destination(destination_id):
    destination = destinations.get_destination(destination_id)
    destination_classes = destinations.get_destination_classes(destination_id)
    comments_list = comments.get_comments(destination_id)

    if not destination:
        abort(404)

    return render_template(
        "show_destination.html",
        destination=destination,
        classes=destination_classes,
        comments=comments_list,
    )


@app.route("/destination/add", methods=["GET", "POST"])
def add_destination():
    utils.require_login()
    all_classes = classes.get_all_classes()

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
        if not description or len(description) < 10 or len(description) > 1000:
            flash("Kuvauksen pitää olla 10-1000 merkkiä pitkä.", "error")
            return redirect(url_for("add_destination"))

        selected_classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                selected_classes.append((class_title, class_value))

        # TODO: Check clases present

        try:
            destination_id = destinations.add_destination(
                name,
                description,
                session["user_id"],
                selected_classes,
            )
            flash("Retkipaikka lisätty onnistuneesti.")
            return redirect(url_for("get_destination", destination_id=destination_id))
        except destinations.DestinationError:
            flash("Virhe retkipaikan lisäämisessä.", "error")
            return redirect(url_for("add_destination"))


@app.route("/destination/<int:destination_id>/edit", methods=["GET", "POST"])
def edit_destination(destination_id):
    utils.require_login()
    destination = destinations.get_destination(destination_id)

    if not destination or destination.get("user_id") != session["user_id"]:
        abort(403)

    all_classes = classes.get_all_classes()

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
        if not name or len(name) < 5 or len(name) > 80:
            flash("Nimen pitää olla 5-80 merkkiä pitkä.", "error")
            return redirect(url_for("edit_destination", destination_id=destination_id))

        description = request.form.get("description")
        if not description or len(description) < 10 or len(description) > 1000:
            flash("Kuvauksen pitää olla 10-1000 merkkiä pitkä.", "error")
            return redirect(url_for("edit_destination", destination_id=destination_id))

        selected_classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                selected_classes.append((class_title, class_value))

        # todo check classes

        try:
            destinations.update_destination(
                destination_id,
                name,
                description,
                selected_classes,
            )
            flash("Retkipaikka päivitetty.")
            return redirect(url_for("get_destination", destination_id=destination_id))
        except destinations.DestinationError:
            flash("Virhe retkipaikan päivityksessä.", "error")
            return redirect(url_for("edit_destination", destination_id=destination_id))


@app.route("/destination/<int:destination_id>/delete", methods=["GET", "POST"])
def delete_destination(destination_id):
    utils.require_login()
    destination = destinations.get_destination(destination_id)

    if not destination or destination.get("user_id") != session["user_id"]:
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
        except destinations.DestinationError:
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

        if not (utils.is_username_valid_characters(username)):
            flash(
                "Käyttäjätunnus tulee olla 5-20 merkkiä ja vain kirjaimia ja numeroita.",
                "error",
            )
            return render_template("register.html", filled={"username": username})

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

        except users.UserAlreadyExists:
            flash(
                "Käyttäjätunnus on jo käytössä. "
                + f"Haluatko <a href=\"{url_for('login')}\">kirjautua sisään?</a>",
                "error",
            )
            return redirect(url_for("register"))

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
            session["csrf_token"] = utils.generate_csrf_token()
            flash("Kirjautuminen onnistui.")
            return redirect(url_for("index"))
        else:
            session["user_id"] = None
            session["username"] = None
            session["csrf_token"] = None

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

    comment = request.form.get("comment")
    rating = utils.parse_int(request.form.get("rating"))

    if not comment or len(comment) < 1 or len(comment) > 500:
        flash("Kommentin pitää olla 1-500 merkkiä pitkä.", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))

    if not rating or rating < 1 or rating > 5:
        flash("Arvion pitää olla välillä 1-5.", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))

    try:
        comments.add_comment(
            destination_id,
            session["user_id"],
            comment,
            rating,
        )
        ratings.update_average_rating(destination_id)
        flash("Kommentti lisätty.")
    except comments.CommentError:
        flash("Virhe kommentin lisäämisessä.", "error")

    return redirect(url_for("get_destination", destination_id=destination_id))


@app.route(
    "/destination/<int:destination_id>/comments/<int:comment_id>/edit",
    methods=["GET", "POST"],
)
def edit_comment(destination_id, comment_id):
    utils.require_login()
    comment = comments.get_comment(comment_id)

    if not comment or comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template(
            "edit_comment.html", comment=comment, destination_id=destination_id
        )

    if request.method == "POST":
        utils.check_csrf()

        action = request.form.get("action")
        if action == "cancel":
            return redirect(url_for("get_destination", destination_id=destination_id))

        comment = request.form.get("comment")
        rating = utils.parse_int(request.form.get("rating"))

        if not comment or len(comment) < 1 or len(comment) > 500:
            flash("Kommentin pitää olla 1-500 merkkiä pitkä.", "error")
            return redirect(url_for("get_destination", destination_id=destination_id))

        if not rating or rating < 1 or rating > 5:
            flash("Arvion pitää olla välillä 1-5.", "error")
            return redirect(url_for("get_destination", destination_id=destination_id))

        try:
            comments.update_comment(comment_id, comment, rating)
            ratings.update_average_rating(destination_id)
            flash("Kommentti päivitetty")
        except comments.CommentError:
            flash("Virhe kommentin päivittämisessä", "error")
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
            ratings.update_average_rating(destination_id)
            flash("Kommentti poistettu")
        except destinations.DestinationError:
            flash("Virhe kommentin poistamisessa", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))


@app.route("/user/<int:user_id>")
def get_user(user_id):
    user = users.get_user(user_id)
    destinations_list = destinations.get_destinations(user_id)
    comments_list = comments.get_comments_by_user(user_id)

    if not user:
        abort(404)

    return render_template(
        "show_user.html",
        user=user,
        destinations=destinations_list,
        comments=comments_list,
    )


@app.route("/destination/<int:destination_id>/add-image", methods=["POST"])
def add_destination_image(destination_id):
    utils.require_login()

    destionation = destinations.get_destination(destination_id)
    if not destionation:
        abort(404)

    if destionation.get("user_id") != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not utils.is_allowed_filetype(file.filename):
        flash("Väärä tiedostomuoto", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))

    image = file.read()
    if len(image) > config.IMAGE_MAX_SIZE:
        flash("Kuva liian suuri", "error")
        return redirect(url_for("get_destination", destination_id=destination_id))

    user_id = session["user_id"]
    destinations.update_image(user_id, destination_id, image)

    flash("Kuva päivitetty")
    return redirect(url_for("get_destination", destination_id=destination_id))


@app.route("/image/<int:destination_id>")
def get_destination_image(destination_id):
    image = destinations.get_image(destination_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.template_filter("class_default_icon")
def class_default_icon(destination_classes, title):
    if "default_icons" not in cache:
        cache["default_icons"] = classes.get_default_icons()

    icons = cache["default_icons"]

    value = destination_classes.get(title)
    if not value:
        return ""

    if icons.get(title):
        if icons[title].get(value):
            return icons[title][value]

    return ""


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if app.debug:
    import time

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        elapsed_time = round(time.time() - g.start_time, 4)
        print("elapsed time:", elapsed_time, "s")
        return response
