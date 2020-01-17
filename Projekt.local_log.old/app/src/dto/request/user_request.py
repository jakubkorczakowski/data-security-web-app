class UserRequest:
    def __init__(self, reqest):
        self.firstname = reqest["firstname"]
        self.lastname = reqest["lastname"]
        self.username = reqest["username"]
        self.password = reqest["password"]

    def __str__(self):
        return "firstname: {0}, lastname: {1}, username: {2}, password: {3}" \
            .format(self.firstname, self.lastname, self.username, self.password)
