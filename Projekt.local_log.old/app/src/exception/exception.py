class UserAlreadyExistsException(Exception):
    pass


class UserNotFoundByUsernameException(Exception):
    pass


class UserPasswordIsInvalidException(Exception):
    pass


class NoteAlreadyExistsException(Exception):
    pass


class NoteNotFoundByIdException(Exception):
    pass


class EmptyNoteNameException(Exception):
    pass


