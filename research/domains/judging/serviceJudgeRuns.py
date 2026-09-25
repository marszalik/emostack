from emostack.core.ProcessorError import ProcessorError
from research.domains.judging.JudgedSeries import JudgedSeries
from research.domains.judging.JudgingContext import JudgingContext


class serviceJudgeRuns:
    """One judge over one or more runs at once. With several runs, each criterion is one call over
    all of them as blind series A, B, …, so that the judge scores them on the same scale."""

    temperature = 0.0

    def __init__(self, scores, turns, criteria, connect, streams):
        self.scores = scores
        self.turns = turns
        self.criteria = criteria
        self.connect = connect
        self.streams = streams

    def judge(self, judge, runIds, scenarioId, streamKey):
        if not judge["modelId"]:
            raise ValueError("the judge has no model")
        processor = self.connect.processor(judge["modelId"])
        series = [JudgedSeries(chr(65 + index), runId, self.turns.forRun(runId, withCalls=False))
                  for index, runId in enumerate(runIds)]
        judgementId = self.scores.startJudgement(judge["id"], runIds)
        try:
            for criterion in self.criteria.forScenario(scenarioId):
                context = JudgingContext(judge, criterion, series)
                answer = processor.chatJson(context.system(), context.user(), self.temperature,
                                            context.responseFormat(), purpose="judging", retries=2)
                self._keep(judgementId, criterion, series, context.unit, answer)
                self.streams.emit(streamKey, {"kind": "judged", "judge": judge["name"], "criterion": criterion["name"]})
            self.scores.finishJudgement(judgementId, "done")
        except (ProcessorError, ValueError) as error:
            self.scores.finishJudgement(judgementId, "error", str(error)[:2000])
            raise
        return judgementId

    def _keep(self, judgementId, criterion, series, unit, answer):
        byLetter = {one.letter: one for one in series}
        for item in answer.get("scores") or []:
            try:
                number = int(item[unit])
                score = max(1.0, min(5.0, float(item["score"])))
            except (KeyError, TypeError, ValueError):
                continue
            letter = str(item.get("series", series[0].letter)).strip().upper()[:1] if len(series) > 1 else series[0].letter
            one = byLetter.get(letter)
            if one is None:
                continue
            if unit == "session":
                self.scores.add(judgementId, one.runId, criterion["id"], None, number, score,
                                str(item.get("rationale", ""))[:300])
            else:
                day = next((turn["dayIndex"] for turn in one.beingTurns() if turn["turnIndex"] == number), None)
                self.scores.add(judgementId, one.runId, criterion["id"], number, day, score,
                                str(item.get("rationale", ""))[:300])
