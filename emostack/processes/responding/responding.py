from emostack.core.ProcessorError import ProcessorError
from emostack.processes.responding.Reaction import Reaction


class responding:
    """Reply generation: one call over the reply context. It returns the moment as felt, the words,
    the retelling of the exchange and the act."""

    temperature = 0.4
    retries = 2

    def __init__(self, processor, actions):
        self.processor = processor
        self.actions = actions

    def react(self, context):
        try:
            answer = self.processor.chatJson(context.system(), context.user(), self.temperature,
                                             context.responseFormat(), purpose="reply", retries=self.retries)
            felt = answer["emothought"]
            words = str(answer.get("reply", "") or "").strip()
            if not bool(answer.get("respond", True)):
                words = ""
            return Reaction(
                feeling=str(felt["emo_summary"]).strip(),
                conclusion=str(felt["conclusion"]).strip(),
                valence=float(felt["valence"]),
                intensity=float(felt["intensity"]),
                reinforcesId=self._reinforced(felt.get("reinforces", -1), context.stateIndex),
                retold=str(answer.get("told", "") or "").strip(),
                words=words,
                action=self.actions.fromReply(answer, words))
        except (ProcessorError, KeyError, TypeError, ValueError):
            return Reaction.failure()

    @staticmethod
    def _reinforced(raw, stateIndex):
        if isinstance(raw, list):
            raw = raw[0] if raw else -1
        try:
            index = int(raw)
        except (TypeError, ValueError):
            return None
        return stateIndex[index] if 0 <= index < len(stateIndex) else None
