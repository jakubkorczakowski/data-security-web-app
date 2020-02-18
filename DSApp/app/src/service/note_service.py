from flask import Flask
from src.service.repositories.note_repository import NoteRepository
from src.exception.exception import NoteNotFoundByIdException
from src.dto.response.paginated_notes_response import PaginatedNotesResponse

app = Flask(__name__)


class NoteService:

    def __init__(self):
        self.note_repo = NoteRepository()

    def add_note(self, username, note_req):

        app.logger.debug("Adding note...")
        note_id = self.note_repo.save(username, note_req)
        app.logger.debug("Added note (id: {0})".format(note_id))
        return note_id

    def update_note(self, note_id, bib_id, username):
        app.logger.debug("Updating note...")
        note = self.note_repo.find_by_id(note_id, username)

        if note is None:
            raise NoteNotFoundByIdException("Not found note by id: {0}".format(note_id, username))

        note.bib_id = bib_id

        updated_note_id = self.note_repo.update(note, username)
        app.logger.debug("Updated note by id: {0}".format(updated_note_id))
        return updated_note_id

    def get_note_by_id(self, note_id, username):
        app.logger.debug("Getting note by id: {0}.".format(note_id))
        note = self.note_repo.find_by_id(note_id, username)

        if note is None:
            raise NoteNotFoundByIdException("Not found note by id: {0}".format(note_id))

        app.logger.debug("Got note by id: {0}".format(note_id))
        return note

    def del_note_by_id(self, note_id_to_del, username):
        app.logger.debug("Deleting bib...")
        note_id = self.note_repo.del_note_by_id(note_id_to_del, username)

        if note_id is None:
            raise NoteNotFoundByIdException("Not found note by id: {0}".format(note_id))

        app.logger.debug("Added note (id: {0})".format(note_id))
        return note_id

    def get_paginated_notes_response(self, start, limit, username):
        app.logger.debug("Getting paginated notes (start: {0}, limit: {1})".format(start, limit))
        n_of_notes = len(self.get_all_notes(username))

        notes = self.note_repo.find_n_notes(start, limit, username)

        notes_response = PaginatedNotesResponse(notes, start, limit, n_of_notes)

        app.logger.debug(
            "Got paginated notes (start: {0}, limit: {1}, count: {2}, current_size: {3})".format(start, limit,
                                                                                                 n_of_notes,
                                                                                                 len(notes)))
        return notes_response

    def get_all_notes(self, username):
        app.logger.debug("Getting all notes")
        n_of_notes = self.note_repo.count_all()
        start = 1
        limit = n_of_notes + 1

        notes = self.note_repo.find_n_notes(start, limit, username)

        return notes
