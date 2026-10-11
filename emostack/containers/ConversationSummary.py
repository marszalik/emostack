class ConversationSummary:
    """The part of the focus that has left view, in the being\x27s own voice, without the feelings or the
    conclusions: what it brought in from before this conversation, and what happened earlier in it,
    each folded on its own."""

    def __init__(self):
        self.before = ""
        self.during = ""

    def isEmpty(self):
        return not (self.before.strip() or self.during.strip())
