import json
import os


class config:
    """Settings of the web application. A secret comes from the environment, never from a file in
    the repository: COOKIE_SECRET, when people are known by a signed cookie.

    identity              how a person is known: local (one person, no sign-in), header (a reverse
                          proxy signs people in) or cookie (a sign-in domain added to the application)
    localEmail            the owner's email in the local identity
    identityHeader        the header a reverse proxy passes the email in
    signInPath            where the sign-in page is, when there is one
    signOutUrl            where signing out happens, when a proxy or a sign-in domain handles it

    dataFolder            where the application keeps its database and every person's store
    publicBaseUrl         the address people reach the application at
    adminEmails           people who administer it; they talk on the server's own model
    requireLoginLevel     the level a person needs to see anything (0 switches the gate off)
    defaultLevel          the level of a signed-in person nobody has given a role to
    requireUserModel      everyone but an administrator talks on their own key
    serverProcessor       the administrators' LLM model (settings as in the engine's config)
    serverEmbedder        the embedder used for providers without one (Anthropic)
    maxBeingsPerPerson, maxConversationsPerPerson, maxWords
    """

    defaults = {
        "dataFolder": "data/web",
        "identity": "local",
        "localEmail": "owner@localhost",
        "identityHeader": "X-Auth-Email",
        "signInPath": "",
        "signOutUrl": "",
        "publicBaseUrl": "",
        "adminEmails": [],
        "requireLoginLevel": 1,
        "defaultLevel": 0,
        "requireUserModel": False,
        "serverProcessor": {},
        "serverEmbedder": {},
        "maxBeingsPerPerson": 5,
        "maxConversationsPerPerson": 3,
        "maxWords": 4000,
    }

    def __init__(self, path=None, root=None):
        values = dict(self.defaults)
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                values.update(json.load(f))
        self.values = values
        folder = values["dataFolder"]
        self.dataFolder = folder if os.path.isabs(folder) else os.path.join(root or os.getcwd(), folder)
        os.makedirs(self.dataFolder, exist_ok=True)

    def __getattr__(self, name):
        values = self.__dict__.get("values", {})
        if name in values:
            return values[name]
        raise AttributeError(name)

    def secret(self, name):
        return os.environ.get(name, "")
