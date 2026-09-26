from emostack.trigger.Channel import Channel


class Trigger:
    """What reaches the being from the world: an event addressed to it. It is never stored as
    such; what it leaves is an episode.

    A trigger is taken by whoever runs it through `enter(handler)`: each kind calls the handler
    method for itself, so no code asks which kind it is."""

    def __init__(self, person, at, channel=Channel.TEXT):
        self.person = person
        self.at = at
        self.channel = channel

    def enter(self, handler):
        raise NotImplementedError
