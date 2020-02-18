class NoteRequest:
    def __init__(self, request):
        self.note = request.form["note"]
        self.allowed_users = request.form["allowed_users"].split(' ')
        self.title = request.form["title"]

        if request.form.get('allow_all_users'):
            self.allowed_users.append('__all__')

    def __str__(self):
        return "note: {0}, allowed_users: {1}, title: {2}".format(self.note, self.allowed_users,
                                                                  self.title)
