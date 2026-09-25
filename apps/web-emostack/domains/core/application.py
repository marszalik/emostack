import os

from emostack.core.database import database
from domains.core.config import config
from domains.core.streams import streams
from domains.core.templates import templates


class application:
    """What every domain of the web application shares: its settings, its own database (people,
    roles, their models), the views, the live streams, and the conversations in progress."""

    def __init__(self, root, configPath):
        self.root = root
        self.config = config(configPath, root)
        self.database = database(os.path.join(self.config.dataFolder, "web.db"))
        self.templates = templates(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.streams = streams()
        self.conversations = {}

    def page(self, name, **values):
        values.setdefault("user", None)
        values.setdefault("level", 0)
        values.setdefault("section", "")
        values.setdefault("signInPath", self.config.signInPath)
        values.setdefault("signOutUrl", self.config.signOutUrl or ("/auth/logout" if self.config.identity == "cookie" else ""))
        values.setdefault("identity", self.config.identity)
        return self.templates.render(name, **values)
