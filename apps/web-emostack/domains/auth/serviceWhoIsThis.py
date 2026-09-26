from domains.auth.Person import Person
from domains.auth.repositoryPeople import repositoryPeople
from domains.auth.sessionCookie import sessionCookie


class serviceWhoIsThis:
    """The person behind a request, with their level; None when nobody signed in. How a person is
    known is a setting (`identity`):

      local   one person, the owner of this installation, an administrator; nobody signs in
      header  a reverse proxy signs people in and passes the email in `identityHeader`; it must
              overwrite that header on every request, so that a browser cannot set it
      cookie  a sign-in domain added to the application sets a signed cookie (see sessionCookie)
    """

    def __init__(self, application):
        self.application = application
        self.cookie = sessionCookie(application.config.secret("COOKIE_SECRET"))
        self.people = repositoryPeople(application.database)

    def person(self, request):
        identity = self.application.config.identity
        if identity == "local":
            email = self.application.config.localEmail
            return Person(email, "", "", Person.ADMINISTRATOR)
        if identity == "header":
            email = (request.headers.get(self.application.config.identityHeader) or "").strip().lower()
            return Person(email, "", "", self.levelOf(email)) if "@" in email else None
        data = self.cookie.read(request.cookies.get(sessionCookie.name, ""))
        if data is None:
            return None
        email = data["email"].strip().lower()
        return Person(email, data.get("name", ""), data.get("picture", ""), self.levelOf(email))

    def level(self, request):
        person = self.person(request)
        return person.level if person else int(self.application.config.defaultLevel)

    def levelOf(self, email):
        if email in {admin.strip().lower() for admin in self.application.config.adminEmails}:
            return Person.ADMINISTRATOR
        stored = self.people.level(email)
        return stored if stored is not None else int(self.application.config.defaultLevel)
