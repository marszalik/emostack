from emostack.core.ProcessorError import ProcessorError
from emostack.processes.introspection.ReflectionStep import ReflectionStep


class introspection:
    """One moment of thinking: over the introspection context, one honest first-person thought with
    no direction given, and what, if anything, follows from it. The temperament bends its feeling
    as it bends every other."""

    temperature = 0.5

    def __init__(self, processor, actions):
        self.processor = processor
        self.actions = actions

    def reflect(self, context, temperament):
        try:
            answer = self.processor.chatJson(context.system(), context.user(), self.temperature,
                                             context.responseFormat(), purpose="introspection")
            thought = str(answer["thought"]).strip()
            feeling = str(answer["emo_summary"]).strip()
            conclusion = str(answer["conclusion"]).strip()
            valence, intensity = temperament.apply(float(answer["valence"]), float(answer["intensity"]))
        except (ProcessorError, KeyError, TypeError, ValueError):
            return None
        reinforcesId = None
        try:
            index = int(answer.get("reinforces", -1))
            if 0 <= index < len(context.entries):
                reinforcesId = context.entries[index].id
        except (TypeError, ValueError):
            pass
        if reinforcesId is not None and valence < 0:
            # a thought that only circles a painful feeling again carries no new conclusion
            conclusion = ""
        return ReflectionStep(thought, feeling, conclusion, valence, intensity, reinforcesId,
                              self.actions.fromReflection(answer))
