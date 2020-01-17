from flask import Flask, request, render_template, send_file, abort, redirect, url_for, make_response, Response
import redis
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies
import os, sys
from datetime import datetime

POST = "POST"
GET = "GET"
SECRET_KEY = "FLASK_SECRET"
SESSION_ID = "my-session-id"
TOKEN_EXPIRES_IN_SECONDS = 300

DIR_PATH = "files/"
FILE_COUNTER = "file_counter"
ORG_FILENAME = "org_filename"
NEW_FILENAME = "new_filename"
PATH_TO_FILE = "path_to_file"
DATE = "date"
ACCESS_TOKEN = "access-token"

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
    return render_template("index_files.html")


@app.route("/files-manager/", methods=[GET])
def show_files():
    name_hash = request.cookies.get(SESSION_ID)
    if (name_hash != None):
        files_values = db.hvals(name_hash + "_files")
        files_keys = db.hkeys(name_hash + "_files")
        files_dates = {}
        for key in files_keys:
            files_dates[key] = db.hget(key, DATE)
        files = dict(zip(files_keys, files_values))

        files_number = len(files_keys)

        response = make_response(render_template("notes_list.html", my_files=files, my_files_dates=files_dates,
                                                 my_files_number=files_number))
        response = get_response_with_cookies(name_hash, response)
        return response
    else:
        abort(403)


@app.route("/files-manager/files/", methods=[GET])
def add_files():
    name_hash = request.cookies.get(SESSION_ID)
    if (name_hash != None):
        response = make_response(render_template("add_note.html"))
        response = get_response_with_cookies(name_hash, response)
        return response
    else:
        abort(403)


@app.route("/files-manager/files/<string:file_hash>", methods=[GET])
@jwt_required
def download_file(file_hash):
    full_name = db.hget(file_hash, PATH_TO_FILE)
    org_filename = db.hget(file_hash, ORG_FILENAME)

    if (full_name is not None):
        try:
            return send_file(full_name, attachment_filename=org_filename, as_attachment=True)
        except Exception as e:
            print(e, file=sys.stderr)

    abort(404)


@app.route("/files-manager", methods=[POST])
def upload_file():
    f = request.files["file"]
    name_hash = request.cookies.get(SESSION_ID)
    if (name_hash == None):
        abort(403)

    save_file(f, name_hash)
    return redirect(url_for("show_files"))


def save_file(file_to_save, owner_name_hash):
    if (len(file_to_save.filename) > 0):
        filename_prefix = str(db.incr(FILE_COUNTER))
        new_filename = filename_prefix + file_to_save.filename
        path_to_file = DIR_PATH + new_filename
        file_to_save.save(path_to_file)
        date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

        db.hset(new_filename, ORG_FILENAME, file_to_save.filename)
        db.hset(new_filename, PATH_TO_FILE, path_to_file)
        db.hset(new_filename, DATE, date)
        db.hset(owner_name_hash + "_files", new_filename, file_to_save.filename)
    else:
        print("\n\t\t[WARN] Empty content of file\n", file=sys.stderr)


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
