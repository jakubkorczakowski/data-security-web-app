class UserRequest:
    def __init__(self, request):
        self.firstname = request.form["firstname"]
        self.lastname = request.form["lastname"]
        self.username = request.form["username"]
        self.password = request.form["password"]

    def __str__(self):
        return "firstname: {0}, lastname: {1}, username: {2}, password: {3}" \
            .format(self.firstname, self.lastname, self.username, self.password)
