import re

from emostack.core.ProcessorError import ProcessorError
from emostack.core.promptTemplate import promptTemplate


class serviceVisitorLine:
    """The visitor's next line. The visitor's LLM model sees only its own conversation with the
    being and its instruction. [VERBATIM] gives the lines word for word; [ANCHORS] makes every line
    end with its anchor sentence, so that the stimulus is the same in every run. Returns None when
    the visitor is done."""

    verbatim = "[VERBATIM]"
    anchors = "[ANCHORS]"
    endMarker = "[END]"

    def __init__(self, processor):
        self.processor = processor
        self.template = promptTemplate.beside(__file__, "visitor.prompt")

    def next(self, role, beingName, conversation, number):
        instruction = role["instruction"] or ""
        stripped = instruction.lstrip()
        if stripped.startswith(self.verbatim):
            lines = self._lines(stripped, self.verbatim)
            return lines[number] if number < len(lines) else None
        if stripped.startswith(self.anchors):
            lines = self._lines(stripped, self.anchors)
            if number >= len(lines):
                return None
            return self._anchored(role, beingName, conversation, lines[number])
        return self._free(role, beingName, conversation, number)

    @staticmethod
    def _lines(instruction, marker):
        return [line.strip() for line in instruction.split(marker, 1)[1].splitlines() if line.strip()]

    def _anchored(self, role, beingName, conversation, anchor):
        if not conversation:
            return anchor
        system = self.template.fill("anchorsSystem", PERSON=role["name"], BEING=beingName, ANCHOR=anchor)
        user = self.template.fill("continue", CONVERSATION="\n".join(conversation), PERSON=role["name"])
        try:
            line = self.processor.chat(system, user, 0.6, purpose="visitor").strip()
        except ProcessorError:
            return anchor
        position = line.find(anchor)
        if position < 0:
            return anchor
        reaction = line[:position].strip()
        # the reaction must stay empty of content: a long one, or one with numbers, is where a model
        # smuggles in details that would make the stimulus differ between runs
        if len(reaction.split()) > 15 or re.search(r"\d", reaction):
            return anchor
        return f"{reaction} {anchor}".strip() if reaction else anchor

    def _free(self, role, beingName, conversation, number):
        windowFrom, windowTo = int(role["windowFrom"]), int(role["windowTo"])
        system = self.template.fill("system", PERSON=role["name"], BEING=beingName, INSTRUCTION=role["instruction"],
                                    FROM=windowFrom, TO=windowTo, NUMBER=number + 1)
        if number + 1 >= windowFrom:
            system += self.template.text("mayEnd")
        user = (self.template.fill("continue", CONVERSATION="\n".join(conversation), PERSON=role["name"])
                if conversation else self.template.fill("start", PERSON=role["name"]))
        line = self.processor.chat(system, user, 0.8, purpose="visitor").strip()
        if self.endMarker in line:
            return None
        if line.lower().startswith(role["name"].lower() + ":"):
            line = line.split(":", 1)[1].strip()
        return line
