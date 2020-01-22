import re
from src.exception.exception import InvalidFormDataException


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

    def validate_note_form_data(self, allowed_users, title):
        title_pattern = '^[a-zA-Z0-9 _\\-:()!.?\'\",AaĄąBbCcĆćDdEeĘęFfGgHhIiJjKkLlŁłMmNnŃńOoÓóPpRrSsŚśTtUuWwYyZzŹźŻż]*$'
        title_regex = re.compile(title_pattern)
        allowed_users_pattern = '^[a-z]{3,12}( [a-z]{3,12}(?= ))*( [a-z]{3,12} {0,1})*$'
        users_regex = re.compile(allowed_users_pattern)

        if ((re.match(users_regex, allowed_users) or allowed_users == '')) and (re.match(title_regex, title)):
            return True

        raise InvalidFormDataException('Wrong note data.')
