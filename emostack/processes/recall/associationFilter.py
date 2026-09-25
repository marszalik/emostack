from emostack.core.ProcessorError import ProcessorError
from emostack.processes.recall.AssociationFilterContext import AssociationFilterContext
from emostack.processes.recall.FilterVerdict import FilterVerdict


class associationFilter:
    """One small LLM call: of the recall candidates, which would actually come to a person's mind
    on hearing these words."""

    temperature = 0.2
    fallbackKeep = 3

    def __init__(self, processor, feelingWords, keepAtMost=4):
        self.processor = processor
        self.feelingWords = feelingWords
        self.keepAtMost = keepAtMost

    def choose(self, words, candidates, keepAtMost=None):
        """candidates: records. Returns a FilterVerdict."""
        keepAtMost = self.keepAtMost if keepAtMost is None else int(keepAtMost)
        if keepAtMost <= 0 or not candidates:
            return FilterVerdict([])
        context = AssociationFilterContext(words, candidates, keepAtMost, self.feelingWords)
        try:
            answer = self.processor.parseJson(self.processor.chat(
                context.system(), context.user(), self.temperature, context.responseFormat(),
                purpose="associationFilter"))
        except (ProcessorError, ValueError):
            return FilterVerdict(candidates[:self.fallbackKeep])
        kept = [candidates[index] for index in answer.get("keep", [])
                if isinstance(index, int) and 0 <= index < len(candidates)]
        return FilterVerdict(kept, answer.get("asks_for_memory", False), answer.get("asks_for_own"))
