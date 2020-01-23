from flask import jsonify
import json


class PaginatedNotesResponse:
    def __init__(self, notes, start, limit, count):
        self.notes = []

        for note in notes:
            note.allowed_users = ''
            self.notes.append(note.__dict__)

        self.start = start
        self.limit = limit
        self.current_size = len(notes)
        self.count = count

    def get_json(self, url):
        if self.start <= 1:
            previous_url = ""
        else:
            start_previous = max(1, self.start - self.limit)
            previous_url = "{0}?start={1}&limit={2}".format(url, start_previous, self.limit)

        if self.start + self.limit > self.count:
            next_url = ""
        else:
            start_next = self.start + self.limit
            next_url = "{0}?start={1}&limit={2}".format(url, start_next, self.limit)

        return {
            "notes": self.notes,
            "start": self.start,
            "limit": self.limit,
            "current_size": self.current_size,
            "count": self.count,
            "previous": previous_url,
            "next": next_url
        }
