from emostack.core.promptTemplate import promptTemplate


class DispositionClassificationContext:
    """What placing a new rule sees: the rules the being holds and the new one."""

    def __init__(self, rule, dispositions):
        self.rule = rule
        self.dispositions = list(dispositions)
        self.template = promptTemplate.beside(__file__, "dispositionClassification.prompt")

    def system(self):
        return self.template.text("system")

    def user(self):
        rules = "\n".join(self.template.fill("rule", INDEX=index, RULE=disposition.rule)
                          for index, disposition in enumerate(self.dispositions))
        return self.template.fill("user", RULES=rules, NEW=self.rule)

    def responseFormat(self):
        return self.template.json("responseFormat")
