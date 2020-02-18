from flask import Flask
import redis
import json
import hashlib
import os

from ...service.entity.user import User
from ...exception.exception import UserAlreadyExistsException

app = Flask(__name__)

USER_COUNTER = "user_counter"
USER_USERNAME_PREFIX = "user_"
SALT_USER_PREFIX = "salt_"
FLASK_SECRET = "FLASK_SECRET"

HASH_ITERATIONS = 100000
SALT_SIZE = 32


class UserRepository:

    def __init__(self):
        self.db = redis.Redis(host="redis", port=6379, decode_responses=True, password=os.environ.get(FLASK_SECRET))
        if self.db.get(USER_COUNTER) is None:
            self.db.set(USER_COUNTER, 0)

    def save(self, user_req):
        app.logger.debug("Saving new user: {0}.".format(user_req))
        user = self.find_by_username(user_req.username)

        if user != None:
            raise UserAlreadyExistsException(
                "user (username: \"{0}\") already exists".format(user_req.username))

        self.db.incr(USER_COUNTER)

        password = user_req.password.encode("utf-8")
        salt = os.urandom(SALT_SIZE)
        password_hash = hashlib.pbkdf2_hmac('sha512', bytes(password), salt, HASH_ITERATIONS).hex()

        user = User(user_req.firstname, user_req.lastname, user_req.username, password_hash)

        user_username = USER_USERNAME_PREFIX + str(user.username)
        user_salt_username = SALT_USER_PREFIX + str(user.username)
        user_json = json.dumps(user.__dict__)
        self.db.set(user_username, user_json)
        self.db.set(user_salt_username, salt.hex())

        app.logger.debug("Saved new user: (username: {0}).".format(user.username))
        return user.username

    def update(self, user, new_password):
        app.logger.debug("Updating note: {0}.".format(user.username))

        password = new_password.encode("utf-8")
        salt = os.urandom(SALT_SIZE)
        password_hash = hashlib.pbkdf2_hmac('sha512', bytes(password), salt, HASH_ITERATIONS).hex()
        user.password_hash = password_hash

        user_json = json.dumps(user.__dict__)
        app.logger.debug(user_json)

        user_username = USER_USERNAME_PREFIX + str(user.username)
        user_salt_username = SALT_USER_PREFIX + str(user.username)
        self.db.set(user_username, user_json)
        self.db.set(user_salt_username, salt.hex())
        app.logger.debug("Updated user: {0}.".format(user.username))
        return user.username

    def find_by_username(self, user_username_to_find):

        user_username = USER_USERNAME_PREFIX + user_username_to_find

        if not self.db.exists(user_username):
            return None

        user_json = self.db.get(user_username)
        user = User.from_json(json.loads(user_json))

        if user.username == user_username_to_find:
            return user

        return None

    def del_user_by_username(self, user_username_to_find):

        user_username = USER_USERNAME_PREFIX + user_username_to_find

        if not self.db.exists(user_username):
            return None

        user_json = self.db.get(user_username)
        user = User.from_json(json.loads(user_json))

        if user.username == user_username_to_find:
            self.db.delete(user_username)
            return user.username

        return None

    def find_salt_by_username(self, user_username_to_find):

        user_username = SALT_USER_PREFIX + user_username_to_find

        if not self.db.exists(user_username):
            return None

        salt = self.db.get(user_username)

        return salt
