class Action:
    """What the being does: one act per step. The performer of a step (a turn or a reflection)
    runs it through `execute(performer)`; each kind calls the performer's method for itself.

    replyNames and reflectionNames are the words by which the LLM model names this kind of act
    in the answer of a reply call or of a reflection."""

    target = None
    replyNames = ()
    reflectionNames = ()

    def execute(self, performer):
        raise NotImplementedError
