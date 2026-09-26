from emostack.trigger.Trigger import Trigger


class Departure(Trigger):
    """Someone leaves. No record is formed; the conversation closes for the processes that run on
    a whole conversation: introspection in the quiet and disposition learning."""

    def enter(self, handler):
        return handler.onDeparture(self)
