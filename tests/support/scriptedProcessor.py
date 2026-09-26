import json

from emostack.core.processor import processor


class scriptedProcessor(processor):
    """An LLM model for tests: answers each purpose from a queue of prepared answers, or with a
    default, and keeps every call."""

    defaults = {
        "reply": {"emothought": {"emo_summary": "a quiet interest", "conclusion": "they are curious",
                                 "valence": 0.3, "intensity": 0.4, "reinforces": -1},
                  "told": "Someone spoke and the being answered.", "reply": "Hello.", "respond": True,
                  "action": {"type": "none", "text": ""}},
        "appraisal": {"emothought": {"emo_summary": "a mild warmth", "conclusion": "this was kind",
                                     "valence": 0.4, "intensity": 0.5}},
        "associationFilter": {"keep": [0], "reason": "", "asks_for_memory": False, "asks_for_own": None},
        "introspection": {"thought": "I keep thinking about it.", "emo_summary": "calm", "conclusion": "it matters",
                          "valence": 0.2, "intensity": 0.5, "reinforces": -1,
                          "action": {"type": "none", "text": ""}},
        "summarising": "We talked.",
        "dispositionSelection": {"matched": [0]},
        "dispositionLearning": {"learned": None},
        "dispositionClassification": {"same": -1, "contradicts": -1},
        "consolidation": {"groups": []},
        "visitor": "How are you today?",
        "control": "I am fine, thank you.",
        "judging": {"scores": []},
    }

    def __init__(self):
        super().__init__()
        self.queues = {}
        self.calls = []
        self.addRecorder(self.calls.append)

    def prepare(self, purpose, *answers):
        self.queues.setdefault(purpose, []).extend(answers)

    def callsFor(self, purpose):
        return [call for call in self.calls if call["purpose"] == purpose]

    def converse(self, system, messages, temperature, responseFormat=None, purpose=""):
        self._purpose = purpose
        return super().converse(system, messages, temperature, responseFormat, purpose)

    def _send(self, system, messages, temperature, responseFormat):
        queue = self.queues.get(self._purpose) or []
        answer = queue.pop(0) if queue else self.defaults[self._purpose]
        return answer if isinstance(answer, str) else json.dumps(answer)
