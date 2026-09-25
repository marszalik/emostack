from emostack.core.promptTemplate import promptTemplate


class JudgingContext:
    """What a judge sees for one criterion: the conversations of one or more runs as blind series,
    the scoring rules, and which units to score. Nothing tells it which series is which arm."""

    def __init__(self, judge, criterion, series):
        self.judge = judge
        self.criterion = criterion
        self.series = series
        self.template = promptTemplate.beside(__file__, "judging.prompt")

    @property
    def unit(self):
        return "session" if self.judge["granularity"] == "session" else "turn"

    def system(self):
        return self.template.fill(
            "system", SEVERAL=self.template.text("several") if len(self.series) > 1 else "",
            NAME=self.criterion["name"], RULES=self.criterion["description"],
            INSTRUCTION=self.judge["instruction"] or self.template.text("noInstruction"))

    def user(self):
        blocks, asks = [], []
        for one in self.series:
            tag = (self.template.fill("seriesTag", LETTER=one.letter) if len(self.series) > 1
                   else self.template.text("singleTag"))
            blocks.append(self.template.fill("block", TAG=tag, TRANSCRIPT=self._transcript(one.turns)))
            if self.unit == "session":
                units = [{"session": day, "person": person} for day, person in one.days()]
                asks.append(self.template.fill("askDays", TAG=tag, UNITS=units))
            else:
                asks.append(self.template.fill("askTurns", TAG=tag, UNITS=one.beingTurnIndexes()))
        shape = self.template.fill("shapeSeveral" if len(self.series) > 1 else "shapeSingle", UNIT=self.unit)
        return self.template.fill("user", BLOCKS="\n\n".join(blocks), ASK="\n".join(asks), SHAPE=shape)

    def responseFormat(self):
        return self.template.json("responseFormat")

    def _transcript(self, turns):
        lines = []
        for turn in turns:
            if turn["speaker"] == "sheep":
                lines.append(self.template.fill("beingLine", INDEX=turn["turnIndex"], TEXT=turn["text"]))
            elif turn["speaker"] == "visitor":
                lines.append(self.template.fill("visitorLine", PERSON=turn["person"], TEXT=turn["text"]))
        return "\n".join(lines)
