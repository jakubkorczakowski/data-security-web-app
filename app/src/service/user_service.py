from flask import Flask
from src.service.repositories.user_repository import UserRepository
from src.exception.exception import UserNotFoundByUsernameException
from src.exception.exception import UserPasswordIsInvalidException
import hashlib

app = Flask(__name__)

HASH_ITERATIONS = 100000


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()

    def add_user(self, user_req):
        app.logger.debug("Adding user...")
        user_username = self.user_repo.save(user_req)
        app.logger.debug("Added user (username: {0})".format(user_username))
        return user_username

    def get_user_by_username(self, user_username):
        app.logger.debug("Getting user by username: {0}.".format(user_username))
        user = self.user_repo.find_by_username(user_username)

        if user == None:
            raise UserNotFoundByUsernameException("Not found user by username: {0}".format(user_username))

        app.logger.debug("Got user by username: {0}".format(user_username))
        return user

    def del_user_by_username(self, user_username_to_del):
        app.logger.debug("Deleting user...")
        user_username = self.user_repo.del_user_by_username(user_username_to_del)

        if user_username == None:
            raise UserNotFoundByUsernameException("Not found user by username: {0}".format(user_username))

        app.logger.debug("Deleted user (username: {0})".format(user_username))
        return user_username

    def get_user_by_username_and_password(self, user_username_to_check, user_password_to_check):
        app.logger.debug("Checking user with username: {0} password.".format(user_username_to_check))
        user = self.get_user_by_username(user_username_to_check)
        salt = self.user_repo.find_salt_by_username(user_username_to_check)

        password_to_check = user_password_to_check.encode("utf-8")
        salt = bytes.fromhex(salt)
        password_to_check_hash = hashlib.pbkdf2_hmac('sha512', bytes(password_to_check), salt, HASH_ITERATIONS).hex()

        if password_to_check_hash != user.password_hash:
            raise UserPasswordIsInvalidException("User: {0} password is invalid.".format(user_username_to_check))

        app.logger.debug("Checked user with username: {0} password.".format(user_username_to_check))
        return user

    def update_user(self, username, new_password):
        app.logger.debug("Updating user...")
        user = self.get_user_by_username(username)

        if user is None:
            raise UserNotFoundByUsernameException("Not found user by username: {0}".format(username))

        updated_user_username = self.user_repo.update(user, new_password)
        app.logger.debug("Updated user by username: {0}".format(updated_user_username))
        return updated_user_username
