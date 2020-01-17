from flask import Flask, request, render_template, redirect, url_for, make_response, abort, flash, jsonify
import redis
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies
import os
import hashlib

GET = "GET"
POST = "POST"
SECRET_KEY = "FLASK_SECRET"
SESSION_ID = "my-session-id"
ACCESS_TOKEN = "access-token"
TOKEN_EXPIRES_IN_SECONDS = 300

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis", port=6379, decode_responses=True)

app.config['JWT_SECRET_KEY'] = os.environ.get(SECRET_KEY)
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
jwt = JWTManager(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/app", methods=[GET, POST])
def login():
    if (request.method == POST):
        if ((request.form["username"] != "") and (request.form["username"] != "")):
            username = request.form["username"].encode("utf-8")
            password = request.form["password"].encode("utf-8")
            name_hash = hashlib.sha512(username).hexdigest()
            password_hash = hashlib.sha512(password).hexdigest()
            if (db.hget(name_hash, "password_hash") == password_hash):
                response = make_response(render_template("index.html"))
                response = get_response_with_cookies(name_hash, response)
                return response
            else:
                flash("Błędne hasło.")

    return render_template("app.html")


@app.route("/app/<string:username>", methods=[GET])
def login_check(username):
    name_hash = hashlib.sha512(username.encode("utf-8")).hexdigest()
    firstname = db.hget(name_hash, "firstname")
    if (firstname is None):
        message = {"status": 404, "message": "Not Found " + request.url}
        resp = jsonify(message)
        resp.status_code = 404
    else:
        message = {"status": 200, "message": "OK"}
        resp = jsonify(message)
        resp.status_code = 200
    return resp


@app.route("/register", methods=[GET, POST])
def register():
    if (request.method == POST):
        fields_are_valid = True
        if (fields_are_valid):
            registration_dict = {}
            username = request.form["username"].encode("utf-8")
            name_hash = hashlib.sha512(username).hexdigest()
            password = request.form["password"].encode("utf-8")
            password_hash = hashlib.sha512(password).hexdigest()
            registration_dict["password_hash"] = password_hash
            for key in ["firstname", "lastname", "birthdate", "pesel", "sex"]:
                registration_dict[key] = request.form[key].encode("utf-8")
            db.hmset(name_hash, registration_dict)
            return render_template("app.html")

        flash("Błędnie poddane pola w formularzu.")
        return render_template("registration.html")

    return render_template("registration.html")


def get_response_with_cookies(name_hash, response):
    response.set_cookie(SESSION_ID, name_hash, max_age=TOKEN_EXPIRES_IN_SECONDS, secure=True, httponly=True)
    access_token = create_access_token(identity=name_hash)
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
    return response



@app.errorhandler(400)
def bad_reqest(error):
    return render_template("errors/400.html", error=error)


@app.errorhandler(401)
def page_unauthorized(error):
    return render_template("errors/401.html", error=error)


@app.errorhandler(403)
def page_forbidden(error):
    return render_template("errors/403.html", error=error)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html", error=error)
