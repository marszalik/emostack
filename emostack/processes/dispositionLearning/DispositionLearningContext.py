from emostack.core.promptTemplate import promptTemplate


class DispositionLearningContext:
    """What disposition learning sees: the context the being worked from in the conversation that
    closed (its state, the retold episodes it rests on, the conversation) and what it carries. Not
    its constructs as such."""

    def __init__(self, beingName, session, carries):
        self.beingName = beingName
        self.session = session
        self.carries = carries
        self.template = promptTemplate.beside(__file__, "dispositionLearning.prompt")

    def system(self):
        return self.template.fill("system", BEING=self.beingName)

    def user(self):
        if self.carries:
            return self.template.fill("userCarrying", CARRIES=self.carries, SESSION=self.session,
                                      BEING=self.beingName)
        return self.template.fill("user", SESSION=self.session, BEING=self.beingName)

    def responseFormat(self):
        return self.template.json("responseFormat")
