import itertools

from research.domains.experiments.serviceFisherTest import serviceFisherTest


class serviceCodingResults:
    """For each coding and coder: how many runs of each arm got each label, and for each pair of arms
    Fisher's exact p on the first label against the rest."""

    def __init__(self, runs, codes, codings, models):
        self.runs = runs
        self.codes = codes
        self.codings = codings
        self.models = models

    def results(self, experiment):
        armOf = {run["id"]: run["armLabel"] for run in self.runs.forExperiment(experiment["id"])}
        grouped = {}
        for code in self.codes.forExperiment(experiment["id"]):
            grouped.setdefault((code["codingId"], code["coderModelId"]), []).append(code)
        out = []
        for (codingId, coderModelId), codes in sorted(grouped.items()):
            coding = self.codings.get(codingId)
            if coding is None:
                continue
            counted = coding["labels"][0]
            arms = {}
            for code in codes:
                arm = armOf.get(code["runId"], "?")
                arms.setdefault(arm, {}).setdefault(code["label"] or "(none)", 0)
                arms[arm][code["label"] or "(none)"] += 1
            pairs = []
            for first, second in itertools.combinations(sorted(arms), 2):
                a = arms[first].get(counted, 0)
                c = arms[second].get(counted, 0)
                b = sum(arms[first].values()) - a
                d = sum(arms[second].values()) - c
                pairs.append({"a": first, "b": second, "countA": f"{a}/{a + b}", "countB": f"{c}/{c + d}",
                              "p": serviceFisherTest().pValue(a, b, c, d)})
            model = self.models.get(coderModelId)
            out.append({"coding": coding["name"], "coder": model["label"] if model else coderModelId,
                        "counted": counted, "arms": arms, "pairs": pairs})
        return out
