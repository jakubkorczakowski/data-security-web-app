import re
from src.exception.exception import InvalidFormDataException, LowPasswordEntropyException
import math


class Validator():

    def __init__(self):
        pass

    def validate_register_form_data(self, user_req, repeted_password):
        if (re.match('^[A-Z][a-z]{1,}$', user_req.firstname)) and \
                (re.match('^[A-Z][a-z]{1,}$', user_req.lastname)) and \
                (re.match('^.{8,40}$', user_req.password)) and \
                (re.match('^[a-z]{3,12}$', user_req.username)) and \
                (user_req.password == repeted_password):
            return True

        raise InvalidFormDataException('Wrong registration data.')

    def validate_login_form_data(self, username, password):
        if (re.match('^.{8,40}$', password)) and \
                (re.match('^[a-z]{3,12}$', username)):
            return True

        raise InvalidFormDataException('Wrong login data.')

    def validate_change_password_form_data(self, old_password, new_password, new_repeated_password):
        if (re.match('^.{8,40}$', old_password)) and \
                (re.match('^.{8,40}$', new_password)) and \
                (new_password == new_repeated_password):
            return True

        raise InvalidFormDataException('Wrong change password data.')

    def validate_note_form_data(self, allowed_users, title):
        title_pattern = '^[a-zA-Z0-9 _\\-:()!.?\'\",AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż]*$'
        title_regex = re.compile(title_pattern)
        allowed_users_pattern = '^[a-z]{3,12}( [a-z]{3,12}(?= ))*( [a-z]{3,12} {0,1})*$'
        users_regex = re.compile(allowed_users_pattern)

        if ((re.match(users_regex, allowed_users) or allowed_users == '')) and (re.match(title_regex, title)):
            return True

        raise InvalidFormDataException('Wrong note data.')

    def check_password_entropy(self, password):
        alfabet_len = 26

        unique_password = set(password)

        big_letters_added = False
        signs_added = False
        sec_signs_added = False
        numbers_added = False

        for c in unique_password:
            if big_letters_added is False and ord(c) in range(ord('A'), ord('Z')):
                alfabet_len += 26
                big_letters_added = True
            if signs_added is False and ord(c) in range(ord(' '), ord('/')):
                alfabet_len += ord('/') - ord(' ') + 1
                signs_added = True
            if sec_signs_added is False and ord(c) in range(ord(':'), ord('@')):
                alfabet_len += ord('@') - ord(':') + 1
                sec_signs_added = True
            if numbers_added is False and ord(c) in range(ord('0'), ord('9')):
                alfabet_len += ord('9') - ord('0') + 1
                numbers_added = True

        entropy = len(password) * math.log(alfabet_len, 2)

        if (entropy < 50):
            raise LowPasswordEntropyException

        return entropy



