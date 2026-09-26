from emostack.core.ProcessorError import ProcessorError
from emostack.processes.appraisal.Affect import Affect


class appraisal:
    """The second reading of the event, with the state withheld on purpose, that forms the record
    to be kept. Returns None when the answer cannot be read; the feeling of the reply call is then
    kept instead."""

    temperature = 0.4

    def __init__(self, processor):
        self.processor = processor

    def appraise(self, context):
        try:
            answer = self.processor.chatJson(context.system(), context.user(), self.temperature,
                                             context.responseFormat(), purpose="appraisal")
            felt = answer["emothought"]
            return Affect(str(felt["emo_summary"]).strip(), str(felt["conclusion"]).strip(),
                          float(felt["valence"]), float(felt["intensity"]))
        except (ProcessorError, KeyError, TypeError, ValueError):
            return None
