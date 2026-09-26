from emostack.core.ProcessorError import ProcessorError
from emostack.processes.dispositionSelection.DispositionSelectionContext import DispositionSelectionContext


class dispositionSelection:
    """Chooses the learned dispositions whose situation the present moment is an instance of: none
    is the normal answer, three the most."""

    temperature = 0.2

    def __init__(self, processor, repository, base=100, most=3):
        self.processor = processor
        self.repository = repository
        self.base = base
        self.most = most

    def hasAny(self, being):
        return self.repository.any(being.id)

    def select(self, being, situation, carries):
        dispositions = [disposition for disposition in self.repository.strongestFirst(being.id, self.base)
                        if disposition.isActive()]
        if not dispositions:
            return []
        context = DispositionSelectionContext(being.name, dispositions, situation, carries)
        try:
            answer = self.processor.parseJson(self.processor.chat(
                context.system(), context.user(), self.temperature, context.responseFormat(),
                purpose="dispositionSelection"))
        except (ProcessorError, ValueError):
            return []
        chosen = [dispositions[index] for index in answer.get("matched", [])
                  if isinstance(index, int) and 0 <= index < len(dispositions)]
        return chosen[:self.most]
