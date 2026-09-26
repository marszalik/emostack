import random
import re
import threading

from research.domains.experiments.BlindCodingContext import BlindCodingContext
from research.domains.experiments.repositoryCodes import repositoryCodes
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.repositoryTurns import repositoryTurns
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
from research.domains.scenarios.repositoryCodings import repositoryCodings


class serviceCodeBlind:
    """One call per coding over every finished run of the experiment, all arms together: the being's
    replies of the coding's day, in an order fixed by the experiment and the coding and blind to the
    arm. The labels are kept with the runs."""

    temperature = 0.0
    replyLimit = 1600

    def __init__(self, application):
        database = application.database
        self.application = application
        self.runs = repositoryRuns(database)
        self.turns = repositoryTurns(database)
        self.codings = repositoryCodings(database)
        self.codes = repositoryCodes(database)
        self.connect = serviceConnectModel(repositoryModels(database), application.config.root)

    def startInBackground(self, experiment, coderModelId, codingIds):
        threading.Thread(target=self.code, args=(experiment, coderModelId, codingIds), daemon=True).start()

    def code(self, experiment, coderModelId, codingIds):
        key = f"experiment:{experiment['id']}"
        coder = self.connect.processor(coderModelId)
        runs = [run for run in self.runs.forExperiment(experiment["id"]) if run["status"] == "done"]
        for codingId in codingIds:
            coding = self.codings.get(codingId)
            try:
                items = [(run["id"], self._replies(run["id"], coding)) for run in runs]
                items = [(runId, text) for runId, text in items if text]
                random.Random(experiment["id"] * 1000 + codingId).shuffle(items)
                context = BlindCodingContext(coding, [text for _, text in items])
                answer = coder.chat(context.system(), context.user(), self.temperature, context.responseFormat(),
                                    purpose="coding")
                codes = self._codes(coder, answer)
                labels = {runId: codes.get(str(index)) for index, (runId, _) in enumerate(items)}
                self.codes.replace(experiment["id"], codingId, coderModelId, labels)
                self.application.streams.emit(key, {"kind": "coded", "text": coding["name"]})
            except Exception as error:
                self.application.streams.emit(key, {"kind": "error", "text": f"coding '{coding['name']}': {error}"})
        self.application.streams.emit(key, {"kind": "codedAll"})

    def _replies(self, runId, coding):
        replies = [turn["text"].strip() for turn in self.turns.forRun(runId, withCalls=False)
                   if turn["speaker"] == "sheep" and turn["dayIndex"] == coding["dayIndex"] and turn["text"].strip()]
        if not replies:
            return ""
        text = replies[-1] if coding["which"] == "last" else "\n\n".join(replies)
        return text[:self.replyLimit]

    @staticmethod
    def _codes(coder, answer):
        try:
            return coder.parseJson(answer).get("codes", {})
        except ValueError:
            found = re.search(r"\{.*\}", answer or "", re.S)
            return coder.parseJson(found.group(0)).get("codes", {}) if found else {}
