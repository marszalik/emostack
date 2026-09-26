from emostack.core.promptTemplate import promptTemplate
from emostack.senses.EmptySense import EmptySense


class Senses:
    """The channels through which the present reaches the being, and its knowledge of them. They
    stand first in every context the being answers from: what it hears, what it does not
    perceive, and how much it holds."""

    def __init__(self, hearing, attentionAndMemory):
        self.hearing = hearing
        self.attentionAndMemory = attentionAndMemory
        self.emptySenses = [EmptySense(name) for name in EmptySense.all]

    @staticmethod
    def words():
        """The words of the senses, including the queries the engine's own searches are named by."""
        return promptTemplate.beside(__file__, "senses.prompt")

    def render(self):
        words = self.words()
        counts = self.attentionAndMemory
        if counts.stateWithheld:
            state = words.text("stateWithheld")
        elif counts.stateCount == 0:
            state = words.text("stateNothing")
        else:
            state = words.fill("stateEntries", COUNT=counts.stateCount)
        associations = (words.text("associationsNone") if counts.associationCount == 0
                        else words.fill("associationsSome", COUNT=counts.associationCount))
        memory = (words.text("memoryEmpty") if counts.memoryCount == 0
                  else words.fill("memoryHolds", COUNT=counts.memoryCount))
        searches = "".join(self._search(words, search) for search in counts.searches)
        return words.fill(
            "senses",
            HEARING=words.fill(self.hearing.carries, PERSON=self.hearing.person),
            EMPTY="\n".join(words.text(sense.name) for sense in self.emptySenses),
            STATE=state, ASSOCIATIONS=associations, MEMORY=memory, SEARCHES=searches)

    @staticmethod
    def _search(words, search):
        if search.found == 0 and search.ownThoughtsOnly > 0:
            result = words.text("searchOnlyThoughts")
        elif search.found == 0:
            result = words.text("searchNothing")
        else:
            result = words.fill("searchFound", COUNT=search.found)
        return words.fill("search", QUERY=str(search.query)[:80], RESULT=result)
