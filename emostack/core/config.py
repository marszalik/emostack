import json


class config:
    """Settings of one engine: where the store is, which LLM model and embedder to use, and the
    parameters of the model. Every parameter has the value of the measured configuration; a JSON
    file overrides any of them."""

    defaults = {
        "databasePath": "data/emostack.db",
        "processor": {
            "baseUrl": "",
            "apiKey": "",
            "model": "",
            "jsonMode": "jsonObject",
            "maxTokens": 2048,
            "maxTokensParam": "max_tokens",
            "supportsTemperature": True,
            "timeoutSeconds": 240,
            "extraBody": {},
        },
        "embedder": {
            "baseUrl": "",
            "apiKey": "",
            "model": "",
            "timeoutSeconds": 240,
        },
        "parameters": {
            "recentCount": 5,
            "recallCandidates": 10,
            "filterKeep": 4,
            "nameBonus": 0.5,
            "strengthPassesFilter": 0.5,
            "fadeFloor": 0.3,
            "fadeTauDays": 3.0,
            "fadeNegativeSlowdown": 1.5,
            "stateMassBudget": 5.0,
            "episodesPerFeeling": 5,
            "focusCap": 100,
            "summaryEveryTurns": 3,
            "summaryThreadCap": 40,
            "strengthClosing": 0.6,
            "introspectionEntries": 8,
            "reflectionMaxSteps": 3,
            "turnActionHops": 1,
            "slotSize": 3,
            "slotDays": 7.0,
            "dispositionsMax": 3,
            "dispositionsBase": 100,
            "arrivalAssociations": 6,
            "quietThoughts": 1,
            "constructDuplicate": 0.90,
            "constructReinforcement": 0.1,
            "silenceSeconds": 600,
            "sleepAfterSeconds": 7200,
            "consolidateAfterSleepSeconds": 600,
            "anchorMinimum": 0.4,
            "forgettingCurve": [[1, 0.2], [7, 0.4], [10, 0.5], [30, 0.6], [180, 0.8]],
            "presenceStaleSeconds": 1800,
        },
        "temperament": {
            "valenceBias": 0.0,
            "intensityAmplification": 1.0,
            "avoidanceWeight": 2.0,
        },
    }

    def __init__(self, values=None):
        self.values = self._merge(self.defaults, values or {})

    @classmethod
    def fromFile(cls, path):
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def section(self, name):
        return self.values[name]

    def parameter(self, name):
        return self.values["parameters"][name]

    @property
    def databasePath(self):
        return self.values["databasePath"]

    def _merge(self, base, override):
        merged = {}
        for key, value in base.items():
            if isinstance(value, dict):
                merged[key] = self._merge(value, override.get(key, {}) or {})
            else:
                merged[key] = override.get(key, value)
        for key, value in override.items():
            if key not in merged:
                merged[key] = value
        return merged
