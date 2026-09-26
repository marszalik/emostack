import threading

from research.domains.judging.repositoryJudges import repositoryJudges
from research.domains.judging.repositoryScores import repositoryScores
from research.domains.judging.serviceJudgeRuns import serviceJudgeRuns
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.repositoryTurns import repositoryTurns
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
from research.domains.scenarios.repositoryCriteria import repositoryCriteria


class serviceJudgeExperiment:
    """Every chosen judge over every repeat of the experiment: the finished runs of one repeat go
    to the judge together, as blind series in the order of the arms."""

    def __init__(self, application):
        database = application.database
        self.application = application
        self.runs = repositoryRuns(database)
        self.judges = repositoryJudges(database)
        self.judgeRuns = serviceJudgeRuns(
            repositoryScores(database), repositoryTurns(database), repositoryCriteria(database),
            serviceConnectModel(repositoryModels(database), application.config.root), application.streams)

    def startInBackground(self, experiment, judgeIds):
        judges = [self.judges.get(judgeId) for judgeId in judgeIds if self.judges.get(judgeId)]
        if not judges:
            raise ValueError("choose at least one judge")
        byRepeat = {}
        for run in self.runs.forExperiment(experiment["id"]):
            if run["status"] == "done":
                byRepeat.setdefault(run["iteration"], []).append(run["id"])
        if not byRepeat:
            raise ValueError("no finished runs yet")
        threading.Thread(target=self._judge, args=(experiment, judges, byRepeat), daemon=True).start()

    def _judge(self, experiment, judges, byRepeat):
        key = f"experiment:{experiment['id']}"
        for repeat in sorted(byRepeat):
            for judge in judges:
                try:
                    self.judgeRuns.judge(judge, byRepeat[repeat], experiment["scenarioId"], key)
                except Exception as error:
                    self.application.streams.emit(key, {"kind": "error", "text": f"repeat {repeat + 1}, {judge['name']}: {error}"})
        self.application.streams.emit(key, {"kind": "judgedAll"})
