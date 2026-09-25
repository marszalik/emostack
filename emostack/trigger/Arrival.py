from emostack.trigger.Trigger import Trigger


class Arrival(Trigger):
    """Someone enters. The being is told who is here and may greet; no record is formed."""

    def enter(self, handler):
        return handler.onArrival(self)
