class Person:
    """Who is making a request, and what they may do: 0 nothing, 1 talk to their own beings,
    2 also see the being's inner life, 3 administer."""

    GUEST = 1
    FRIEND = 2
    ADMINISTRATOR = 3

    def __init__(self, email, name="", picture="", level=0):
        self.email = email
        self.name = name
        self.picture = picture
        self.level = level

    def isAdministrator(self):
        return self.level >= self.ADMINISTRATOR

    def toDict(self):
        return {"email": self.email, "name": self.name, "picture": self.picture}
