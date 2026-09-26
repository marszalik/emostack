class Purpose:
    """A kind of call the engine makes, which the advanced settings can give a model of its own."""

    def __init__(self, name, label):
        self.name = name
        self.label = label

    @classmethod
    def all(cls):
        return [
            cls("reply", "reply — what the being says"),
            cls("appraisal", "appraisal — the feeling that is kept as memory"),
            cls("associationFilter", "association filter — what comes to mind"),
            cls("introspection", "introspection — thinking in the quiet"),
            cls("summarising", "conversation summary"),
            cls("dispositionSelection", "disposition selection"),
            cls("dispositionLearning", "disposition learning"),
            cls("dispositionClassification", "disposition placement"),
            cls("consolidation", "sleep consolidation"),
        ]
