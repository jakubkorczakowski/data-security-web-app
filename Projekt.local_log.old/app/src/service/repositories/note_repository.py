from flask import Flask
import redis
import json
from datetime import datetime

from ...service.entity.note import Note
from ...exception.exception import NoteAlreadyExistsException, EmptyNoteNameException

app = Flask(__name__)

NOTE_COUNTER = "note_counter"
NOTE_ID_PREFIX = "note_"

DIR_PATH = "notes/"
NOT_EXISTING_BIBLIOGRAPHY_ID = 0


class NoteRepository:

    def __init__(self):
        self.db = redis.Redis(host="redis", port=6379, decode_responses=True)
        if self.db.get(NOTE_COUNTER) is None:
            self.db.set(NOTE_COUNTER, 0)

    def save(self, note_to_save, username, allowed_users, title):
        app.logger.debug("Saving new note: {0}.".format(note_to_save))

        if (len(note_to_save) == 0):
            raise EmptyNoteNameException

        id = self.db.incr(NOTE_COUNTER)

        notename_prefix = NOTE_ID_PREFIX + str(id)
        date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

        note = Note(id, note_to_save, date, username, allowed_users, title)

        note_id = NOTE_ID_PREFIX + str(note.id)
        note_json = json.dumps(note.__dict__)

        self.db.set(note_id, note_json)

        app.logger.debug("Saved new note: (id: {0}).".format(note.id))
        return note.id

    def update(self, note, username):
        app.logger.debug("Updating note: {0}.".format(note.id))

        note_id = NOTE_ID_PREFIX + str(note.id)
        note_json = json.dumps(note.__dict__)

        app.logger.debug(note_json)

        self.db.set(note_id, note_json)
        app.logger.debug("Updated note: {0}.".format(note.id))
        return note.id

    def find_by_id(self, note_id_to_find, username):
        n = int(self.db.get(NOTE_COUNTER))

        for i in range(1, n + 1):
            note_id = NOTE_ID_PREFIX + str(i)

            if not self.db.exists(note_id):
                continue

            note_json = self.db.get(note_id)
            note = Note.from_json(json.loads(note_json))

            if note.id == note_id_to_find and note.username == username:
                return note
        return None

    def del_note_by_id(self, note_id_to_del, username):
        n = int(self.db.get(NOTE_COUNTER))

        for i in range(1, n + 1):
            note_id = NOTE_ID_PREFIX + str(i)

            if not self.db.exists(note_id):
                continue

            note_json = self.db.get(note_id)
            note = Note.from_json(json.loads(note_json))

            if note.id == note_id_to_del and note.username == username:
                self.db.delete(note_id)
                return note.id

        return None

    def count_all(self):
        app.logger.debug("Starting counting all notes")
        n = int(self.db.get(NOTE_COUNTER))

        n_of_notes = 0

        for i in range(1, n + 1):
            note_id = NOTE_ID_PREFIX + str(i)

            if self.db.exists(note_id):
                n_of_notes += 1

        app.logger.debug("Counted all notes (n: {0})".format(n_of_notes))
        return n_of_notes

    def find_n_notes(self, start, limit, username):
        app.logger.debug("Finding n of notes (start: {0}, limit: {1}".format(start, limit))
        n = int(self.db.get(NOTE_COUNTER))

        notes = []
        counter = 1

        for i in range(1, n + 1):
            note_id = NOTE_ID_PREFIX + str(i)

            if not self.db.exists(note_id):
                continue

            if counter < start:
                counter += 1
                continue

            note_json = self.db.get(note_id)
            note = Note.from_json(json.loads(note_json))
            if note.username == username:
                notes.append(note)

            if len(notes) >= limit:
                break

        app.logger.debug("Found {0} notes.".format(len(notes)))
        return notes
