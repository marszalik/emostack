import re

from domains.beings.serviceEngineFor import serviceEngineFor
from domains.conversations.LiveConversation import LiveConversation
from domains.models.serviceConnect import serviceConnect


class serviceOpenConversation:
    """Opens a conversation of a person with one of their beings. It needs a model; a person holds
    only a few conversations at once, and the oldest is closed to make room."""

    namePattern = re.compile(r"^[A-Za-zŁÓŚĄĘĆŻŹŃłóśąęćżźń0-9 _-]{1,24}$")

    def __init__(self, application, leave):
        self.application = application
        self.leave = leave

    def open(self, person, beingId, name):
        name = (name or "").strip()
        if not self.namePattern.match(name):
            raise ValueError("a name: letters, digits, spaces, up to 24 characters")
        if self.application.config.requireUserModel and not serviceConnect(self.application).hasModel(person):
            raise PermissionError("set your model first")
        engine = serviceEngineFor(self.application).engine(person)
        being = engine.beings.get(beingId)
        if being is None:
            engine.close()
            raise ValueError("no such being")
        mine = sorted((live for live in self.application.conversations.values() if live.owner == person.email),
                      key=lambda live: live.lastActivity)
        for live in mine[:max(0, len(mine) - self.application.config.maxConversationsPerPerson + 1)]:
            self.leave.leave(live)
        live = LiveConversation(person.email, person.level, being.id, being.name, name, engine)
        self.application.conversations[live.id] = live
        return live
