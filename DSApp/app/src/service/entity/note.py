import json


class Note:
    def __init__(self, id, note, date, username, allowed_users, title):
        self.id = id
        self.note = note
        self.date = date
        self.username = username
        self.allowed_users = allowed_users
        self.title = title

    @classmethod
    def from_json(cls, data):
        return cls(**data)
