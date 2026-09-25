from emostack.core.promptTemplate import promptTemplate


class DispositionSelectionContext:
    """What disposition selection sees: the dispositions, what the being carries, and the present
    situation. Not the state, not the constructs."""

    def __init__(self, beingName, dispositions, situation, carries):
        self.beingName = beingName
        self.dispositions = list(dispositions)
        self.situation = situation
        self.carries = carries
        self.template = promptTemplate.beside(__file__, "dispositionSelection.prompt")

    def system(self):
        return self.template.fill("system", BEING=self.beingName)

    def user(self):
        rules = "\n".join(self.template.fill("rule", INDEX=index, RULE=disposition.rule)
                          for index, disposition in enumerate(self.dispositions))
        if self.carries:
            return self.template.fill("userCarrying", BEING=self.beingName, CARRIES=self.carries, RULES=rules,
                                      INPUT=self.situation.text)
        return self.template.fill("user", RULES=rules, INPUT=self.situation.text)

    def responseFormat(self):
        return self.template.json("responseFormat")
