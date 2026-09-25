from emostack.core.promptTemplate import promptTemplate


class BlindCodingContext:
    """What a blind coder sees: the criterion, the labels, and the replies of every run in an order
    that says nothing of the arm."""

    def __init__(self, coding, replies):
        self.coding = coding
        self.replies = list(replies)
        self.template = promptTemplate.beside(__file__, "coding.prompt")

    def system(self):
        return self.template.fill("system", LABELS=", ".join(self.coding["labels"]))

    def user(self):
        listing = "\n\n".join(self.template.fill("reply", INDEX=index, TEXT=text)
                              for index, text in enumerate(self.replies))
        return self.template.fill("user", CRITERION=self.coding["criterion"], REPLIES=listing)

    def responseFormat(self):
        return self.template.json("responseFormat")
