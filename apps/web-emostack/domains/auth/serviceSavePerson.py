class serviceSavePerson:
    def __init__(self, people):
        self.people = people

    def save(self, email, level):
        email = (email or "").strip().lower()
        level = int(level)
        if "@" not in email or level not in (1, 2, 3):
            raise ValueError("an email and a level 1, 2 or 3")
        self.people.save(email, level)
