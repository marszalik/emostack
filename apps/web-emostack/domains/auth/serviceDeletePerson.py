class serviceDeletePerson:
    def __init__(self, people, config):
        self.people = people
        self.config = config

    def delete(self, email):
        email = (email or "").strip().lower()
        if email in {admin.strip().lower() for admin in self.config.adminEmails}:
            raise ValueError("an administrator named in the settings cannot be removed here")
        self.people.delete(email)
