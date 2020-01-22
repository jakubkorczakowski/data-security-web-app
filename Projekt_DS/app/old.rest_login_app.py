from flask import Flask, request, send_file
from flask_restplus import Api, Resource, fields
from src.dto.request.user_request import UserRequest
from src.exception.exception import UserPasswordIsInvalidException, UserAlreadyExistsException, FileAlreadyExistsException
from src.service.user_service import UserService
from src.service.file_service import FileService
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity
from flask_cors import CORS
import os
import requests


app = Flask(__name__)
api_app = Api(app=app, version="0.1", title="Bib-Maker Login API",
              description="REST-full API for managing users of bibliography service")

user_namespace = api_app.namespace("user", description="User API")
hello_namespace = api_app.namespace("hello", description="Hello API")
file_namespace = api_app.namespace("file", description="File API")

START = "start"
LIMIT = "limit"

SECRET_KEY = "FLASK_SECRET"
SESSION_ID = "my-session-id"
ACCESS_TOKEN = "access-token"
TOKEN_EXPIRES_IN_SECONDS = 300

app.config['JWT_SECRET_KEY'] = os.environ.get(SECRET_KEY)
app.secret_key = os.environ.get(SECRET_KEY)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_TOKEN_LOCATION'] = ('headers', 'cookies')
app.config['JWT_COOKIE_SECURE'] = True
jwt = JWTManager(app)

CORS(app)

@hello_namespace.route("/")
class Hello(Resource):

    def __init__(self, args):
        super().__init__(args)

    def get(self):
        result = requests.get('https://web_files:81/hello', verify=False)

        return result.json()


@user_namespace.route("/")
class User(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.user_service = UserService()

    new_user_model = api_app.model("user model",
                                   {
                                       "firstname": fields.String(required=True, description="user firstname",
                                                                  help="Firstname cannot be blank"),
                                       "lastname": fields.String(required=True, description="user lastname",
                                                                 help="Lastname cannot be null"),
                                       "birthdate": fields.String(required=True, description="user birthdate",
                                                                  help="Birthdate cannot be null"),
                                       "pesel": fields.String(required=True, description="user pesel",
                                                              help="Pesel cannot be null"),
                                       "sex": fields.String(required=True, description="user sex",
                                                            help="Sex cannot be null"),
                                       "password": fields.String(required=True, description="user password",
                                                                 help="Password cannot be null"),
                                       "username": fields.String(required=True, description="user username",
                                                                 help="Username cannot be null")

                                   })

    @api_app.expect(new_user_model)
    def post(self):
        try:
            user_req = UserRequest(request)
            saved_user_id = self.user_service.add_user(user_req)

            result = {"message": "Added new user", "save_user_id": saved_user_id}

            return result

        except UserAlreadyExistsException as e:
            user_namespace.abort(409, e.__doc__, status="Could not save user. Already exists", statusCode=409)


@user_namespace.route("/<string:username>")
class UserUsername(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.user_service = UserService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"username": "Specify user username"})
    def get(self, username):
        try:
            user = self.user_service.get_user_by_username(username)
            resp = user.__dict__
            try:
                del resp['password_hash']
            except KeyError as e:
                pass

            return resp

        except Exception as e:
            user_namespace.abort(400, e.__doc__, status="Could not find user by username", statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"username": "Specify user username"})
    def delete(self, username):
        try:

            user_username = self.user_service.del_user_by_username(username)

            return {
                "message": "Removed user by username: {0}".format(user_username)
            }

        except Exception as e:
            user_namespace.abort(400, e.__doc__, status="Could not remove user by username", statusCode="400")


@user_namespace.route("/app/")
class UserLoginUsername(Resource):

    def __init__(self, args):
        super().__init__(args)
        self.user_service = UserService()

    check_user_password_model = api_app.model("user model for checking password",
                                              {
                                                  "username": fields.String(required=True, description="user username",
                                                                            help="Username cannot be null"),
                                                  "password": fields.String(required=True, description="user password",
                                                                            help="Password cannot be null")
                                              })

    @api_app.doc(responses={200: "OK", 403: "Forbidden"})
    @jwt_required
    def get(self):
        try:
            username = get_jwt_identity()
            user = self.user_service.get_user_by_username(username)
            access_token = create_access_token(identity=username)

            resp = {"access_token": access_token}

            return resp
        except Exception as e:
            user_namespace.abort(400, e.__doc__, status="Could not find user by username", statusCode="400")

    @api_app.expect(check_user_password_model)
    @api_app.doc(responses={200: "OK", 400: "Invalid argument", 403: "Forbidden"})
    def post(self):
        try:
            user = self.user_service.get_user_by_username_and_password(request.json["username"],
                                                                       request.json["password"])

            access_token = create_access_token(identity=request.json["username"])
            resp = {"access_token": access_token}

            return resp

        except UserPasswordIsInvalidException as e:
            user_namespace.abort(403, e.__doc__, status="User password is invalid", statusCode="403")
        except KeyError as e:
            user_namespace.abort(400, e.__doc__, status="Could not find user by username", statusCode="400")


@file_namespace.route("/download/<int:id>")
class FileDownloadID(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"file_id": "Specify file Id"})
    @jwt_required
    def get(self, id):
        try:
            username = get_jwt_identity()
            file = self.file_service.get_file_by_id(id, username)
            return send_file(file.path_to_file, attachment_filename=file.org_filename, as_attachment=True)

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not find file by id",
                                 statusCode="400")


@file_namespace.route("/<int:id>")
class File(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()
        self.bib_service = BibliographyService()

    update_file_model = api_app.model("Update file model",
                                      {
                                          "bibliography_id": fields.Integer(required=True,
                                                                            description="bibliography id",
                                                                            help="Bibliography id cannot be null")

                                      })

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"file_id": "Specify file Id"})
    @jwt_required
    def get(self, id):
        try:
            username = get_jwt_identity()
            file = self.file_service.get_file_by_id(id, username)
            return file.__dict__

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not find file by id",
                                 statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id to remove"})
    @jwt_required
    def delete(self, id):
        try:
            username = get_jwt_identity()
            file_id = self.file_service.del_file_by_id(id, username)

            return {
                "message": "Removed bibliography postion by id: {0}".format(file_id)
            }

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not remove bibliography postion by id",
                                 statusCode="400")

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id"})
    @api_app.expect(update_file_model)
    @jwt_required
    def post(self, id):
        try:
            username = get_jwt_identity()
            bib_id = request.json["bibliography_id"]

            if bib_id != NOT_EXISTING_BIBLIOGRAPHY_ID:
                bib = self.bib_service.get_bib_by_id(bib_id, username)

            updated_file_id = self.file_service.update_file(id, bib_id, username)

            result = {"message": "Updated file", "saved_file_id": updated_file_id}

            return result

        except KeyError as e:
            file_namespace.abort(400, e.__doc__, status="Could not update file by id",
                                 statusCode="400")

        except BibliographyNotFoundByIdException as e:
            file_namespace.abort(404, e.__doc__,
                                 status="Could not update new file. Bibliography (by id) does not exist.",
                                 statusCode="404")

        except Exception as e:
            file_namespace.abort(400, e.__doc__, status="Could not update file by id",
                                 statusCode="400")


@file_namespace.route("/list")
class FileList(Resource):
    def __init__(self, args):
        super().__init__(args)
        self.file_service = FileService()
        self.bib_service = BibliographyService()

    @api_app.doc(responses={200: "OK", 400: "Invalid argument"},
                 params={"id": "Specify file Id"})
    @jwt_required
    def post(self):
        try:
            file = request.files["file"]
            username = get_jwt_identity()
            saved_file_id = self.file_service.add_file(file, username)

            result = {"message": "Added new file", "saved_file_id": saved_file_id}

            return result

        except KeyError as e:
            file_namespace.abort(400, e.__doc__, status="Could not save new file",
                                 statusCode="400")

        except FileAlreadyExistsException as e:
            file_namespace.abort(409, e.__doc__,
                                 status="Could not save new file. Already exists",
                                 statusCode="409")

    @api_app.param(START, "The data will be returned from this position.")
    @api_app.param(LIMIT, "The max size of returned data.")
    @api_app.doc(responses={200: "OK"})
    @jwt_required
    def get(self):
        username = get_jwt_identity()

        start = self.parse_request_arg_or_zero(request, START, "0")
        start = max(1, start)
        all_user_files = self.file_service.get_all_files(username)
        default_limit = len(all_user_files)
        limit = self.parse_request_arg_or_zero(request, LIMIT, str(default_limit))

        paginated_files_response = self.file_service.get_paginated_files_response(start, limit, username)

        return paginated_files_response.get_json(request.base_url)

    def parse_request_arg_or_zero(self, request, param, default_value):
        val = request.args.get(param, default_value)
        val = int(val) if val.isdigit() else 0
        return val