import os

from emostack.core.database import database
from research.domains.core.config import config
from research.domains.core.streams import streams
from research.domains.core.templates import templates


class application:
    """What every domain of the panel shares: its settings, its database, its views and the live
    streams."""

    def __init__(self, root):
        self.config = config(root)
        self.database = database(self.config.databasePath)
        self.templates = templates(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.streams = streams()

    def page(self, name, **values):
        return self.templates.render(name, **values)
