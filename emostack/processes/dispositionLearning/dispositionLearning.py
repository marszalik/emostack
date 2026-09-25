import re

from emostack.core.ProcessorError import ProcessorError
from emostack.processes.dispositionLearning.DispositionClassificationContext import DispositionClassificationContext
from emostack.processes.dispositionLearning.DispositionLearningContext import DispositionLearningContext


class dispositionLearning:
    """When a conversation closes: what did it teach the being about surviving such a meeting
    better? Usually nothing. A rule gets a signed strength from the strongest feeling of the
    conversation, negative when the lesson came from what hurt, and is placed against the rules the
    being holds: the same rule in other words is counted again and the stronger of the two keeps the
    text; a contradicting rule weakens the old one and is added; a rule about something else is
    added."""

    extractTemperature = 0.2
    classifyTemperature = 0.1
    smallest = 0.1

    def __init__(self, processor, repository, clock, base=100):
        self.processor = processor
        self.repository = repository
        self.clock = clock
        self.base = base

    def learn(self, being, session, carries, strength):
        """Returns the rule the being holds after this conversation, or None."""
        rule = self._extract(being, session, carries)
        if not rule:
            return None
        weight = max(-1.0, min(1.0, float(strength)))
        if abs(weight) < self.smallest:
            weight = self.smallest if weight >= 0 else -self.smallest
        now = self.clock.now()
        held = self.repository.strongestFirst(being.id, self.base)
        same, contradicted = self._place(rule, held)
        if same is not None:
            if being.temperament.pull(weight) > being.temperament.pull(same.weight):
                self.repository.rewrite(same, rule, weight, same.count + 1, now)
                return rule
            self.repository.recount(same, same.count + 1, now)
            return same.rule
        if contradicted is not None:
            self.repository.weaken(contradicted, abs(weight), now)
        self.repository.add(being.id, rule, weight, now)
        return rule

    def _extract(self, being, session, carries):
        if not (session or "").strip():
            return None
        context = DispositionLearningContext(being.name, session, carries)
        try:
            answer = self._json(self.processor.chat(context.system(), context.user(), self.extractTemperature,
                                                    context.responseFormat(), purpose="dispositionLearning"))
        except (ProcessorError, ValueError):
            return None
        rule = answer.get("learned")
        return rule.strip() if isinstance(rule, str) and rule.strip() else None

    def _place(self, rule, held):
        if not held:
            return None, None
        context = DispositionClassificationContext(rule, held)
        try:
            answer = self._json(self.processor.chat(context.system(), context.user(), self.classifyTemperature,
                                                    context.responseFormat(), purpose="dispositionClassification"))
            same = int(answer.get("same", -1))
            contradicted = int(answer.get("contradicts", -1))
        except (ProcessorError, ValueError, TypeError):
            return None, None
        pick = lambda index: held[index] if 0 <= index < len(held) else None
        return pick(same), pick(contradicted)

    def _json(self, answer):
        try:
            return self.processor.parseJson(answer)
        except ValueError:
            found = re.search(r"\{.*\}", answer or "", re.S)
            return self.processor.parseJson(found.group(0)) if found else {}
