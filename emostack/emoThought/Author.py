class Author:
    """Who produced a record: a person, by name, or the being itself."""

    PERSON = "person"
    SELF = "self"

    def __init__(self, kind, name=""):
        self.kind = kind
        self.name = name

    @classmethod
    def person(cls, name):
        return cls(cls.PERSON, name)

    @classmethod
    def itself(cls):
        return cls(cls.SELF, "")

    def isSelf(self):
        return self.kind == self.SELF

    def isPerson(self, name=None):
        return self.kind == self.PERSON and (name is None or self.name == name)

    def __eq__(self, other):
        return isinstance(other, Author) and self.kind == other.kind and self.name == other.name

    def __hash__(self):
        return hash((self.kind, self.name))
