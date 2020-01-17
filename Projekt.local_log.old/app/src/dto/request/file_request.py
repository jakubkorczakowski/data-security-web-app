class FileRequest:
    def __init__(self, request):
        self.note = request.json["note"]
        self.date = request.json["date"]
        self.allowed_users = request.json["allowed_users"]
        self.title = request.json["title"]

    def __str__(self):
        return "note: {0}, date: {1}, allowed_users: {2}".format(self.note,  self.date, self.allowed_users)
