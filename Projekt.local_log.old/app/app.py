from flask import Flask, request, send_file, render_template, abort, make_response, flash
from flask_restplus import Api, Resource, fields
from src.dto.request.user_request import UserRequest
from src.exception.exception import UserPasswordIsInvalidException, UserAlreadyExistsException, \
    NoteAlreadyExistsException
from src.service.user_service import UserService
from src.service.note_service import NoteService
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity
from flask_cors import CORS
import os
import requests

# TODO | Dodać wyświetlanie notatek udostępnionym użytkowikowi
# TODO | Dodać walidację notatki + walidację wszystkiego po stronie serwera
# TODO | Dodać salt (ewentualnie kilkukrotne hashowanie)
# TODO | Opóźnienie przy loginie
# TODO | Ukrycie REDISA
# TODO | Sprawdzić notatki Piotrka

app = Flask(__name__, static_url_path="")

START = "start"
LIMIT = "limit"

GET = "GET"
POST = "POST"

SECRET_KEY = "FLASK_SECRET"
SESSION_ID = "my-session-id"
ACCESS_TOKEN = "access-token"
ACCESS_TOKEN_COOKIE = "access_token_cookie"
TOKEN_EXPIRES_IN_SECONDS = 300

app.config['JWT_SECRET_KEY'] = os.environ.get(SECRET_KEY)
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)

user_service = UserService()
note_service = NoteService()


@jwt.unauthorized_loader
def my_unauthorized_loader_function(callback):
    return render_template("errors/403.html"), 403


@app.route('/')
def index():
    return render_template('index.html')


# ==================================== LOGIN ======================================

@app.route('/register', methods=[GET, POST])
def register():
    if request.method == POST:
        try:
            form_data = request.form.to_dict()
            user_req = UserRequest(form_data)
            saved_user_id = user_service.add_user(user_req)

            response = make_response(render_template('index.html'))

            return response

        except UserAlreadyExistsException as e:
            flash("Użytkownik już istnieje.")
            return render_template('registration.html')

    return render_template('registration.html')


@app.route('/login', methods=[GET, POST])
def login():
    if request.method == POST:
        try:
            user = user_service.get_user_by_username_and_password(request.form['username'],
                                                                  request.form['password'])

            access_token = create_access_token(identity=request.form['username'])
            resp = make_response(render_template('index.html'))
            set_access_cookies(resp, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
            return resp
        except UserPasswordIsInvalidException as e:
            flash('Błędne hasło')
            return render_template('login.html')
        except KeyError as e:
            flash('Nie ma takiego użytkownika')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout', methods=[GET])
@jwt_required
def logout():
    response = make_response(render_template('index.html'))
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    return response


@app.route('/login/refresh')
@jwt_required
def refresh_token():
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)

    resp = {"access_token": access_token}

    return resp


@app.route('/user/<string:username>', methods=[GET])
def check_if_user_exists(username):
    try:
        user_service.get_user_by_username(username)
        return {"message": "User with given username exists.", "status": "200"}
    except Exception as e:
        abort(400)

    abort(400)


# =================================== NOTATKI =========================================

@app.route('/notes/list')
@jwt_required
def show_notes():
    username = get_jwt_identity()

    start = parse_request_arg_or_zero(request, START, "0")
    start = max(1, start)
    all_user_notes = note_service.get_all_notes(username)
    default_limit = len(all_user_notes)
    limit = parse_request_arg_or_zero(request, LIMIT, str(default_limit))

    paginated_notes_response = note_service.get_paginated_notes_response(start, limit, username)

    resp_json = paginated_notes_response.get_json(request.base_url)

    response = make_response(render_template("notes_list.html", resp_json=resp_json))
    access_token = create_access_token(identity=username)
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)

    return response


def parse_request_arg_or_zero(request, param, default_value):
    val = request.args.get(param, default_value)
    val = int(val) if val.isdigit() else 0
    return val


@app.route("/notes/add", methods=[GET, POST])
@jwt_required
def add_note():
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)

    if (request.method == POST):
        try:
            title = request.form["title"]
            note = request.form['note']
            allowed_users_string = request.form['allowed_users']
            allowed_users = allowed_users_string.split(' ')
            if request.form.get('allow_all_users'):
                allowed_users.append('__all__')
            saved_note_id = note_service.add_note(note, username, allowed_users, title)
            return show_notes()
        except KeyError as e:
            app.logger.debug('ke')
            response = make_response(render_template("add_note.html"))
            set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
            return response
        except NoteAlreadyExistsException as e:
            app.logger.debug('faee')
            response = make_response(render_template("add_note.html"))
            set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
            return response

    response = make_response(render_template("add_note.html"))
    set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
    return response


@app.route("/notes/delete/<int:id>")
@jwt_required
def delete_note(id):
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)

    try:
        username = get_jwt_identity()
        note_id = note_service.del_note_by_id(id, username)
    except Exception as e:
        abort(404)

    return show_notes()


@app.route("/notes/<int:id>")
@jwt_required
def show_note(id):
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)

    try:
        username = get_jwt_identity()
        note = note_service.get_note_by_id(id, username)
        author = user_service.get_user_by_username(note.username)
        response = make_response(render_template("note_page.html", author=author, note=note))
        set_access_cookies(response, access_token, max_age=TOKEN_EXPIRES_IN_SECONDS)
        return response
    except Exception as e:
        abort(404)

    return show_notes()


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


