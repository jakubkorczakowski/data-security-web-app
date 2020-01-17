import json


class User:
    def __init__(self, firstname, lastname, username, password_hash):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def from_json(cls, data):
        return cls(**data)
