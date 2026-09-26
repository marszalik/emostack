import json
import os
import re

from emostack.core.localEmbedder import localEmbedder
from emostack.core.openAiCompatibleProcessor import openAiCompatibleProcessor


class serviceConnectModel:
    """A stored model → a processor or an embedder the engine can use. A key file may hold notes
    around the key: only the key token is taken."""

    keyPattern = re.compile(r"sk-[A-Za-z0-9_\-]+")

    def __init__(self, repository, root):
        self.repository = repository
        self.root = root

    def processor(self, modelId):
        model = self._model(modelId)
        return openAiCompatibleProcessor({
            "baseUrl": model["baseUrl"], "apiKey": self._key(model), "model": model["model"],
            "jsonMode": model["jsonMode"], "maxTokens": model["maxTokens"],
            "maxTokensParam": model["maxTokensParam"], "supportsTemperature": bool(model["supportsTemperature"]),
            "timeoutSeconds": model["timeoutSeconds"],
            "extraBody": json.loads(model["extraBody"]) if model["extraBody"].strip() else {}})

    def embedder(self, modelId):
        model = self._model(modelId)
        return localEmbedder({"baseUrl": model["baseUrl"], "apiKey": self._key(model), "model": model["model"],
                              "timeoutSeconds": model["timeoutSeconds"]})

    def _model(self, modelId):
        model = self.repository.get(int(modelId))
        if model is None:
            raise ValueError(f"no model {modelId}")
        return model

    def _key(self, model):
        if not model["apiKeyFile"]:
            return model["apiKey"]
        path = model["apiKeyFile"]
        if not os.path.isabs(path):
            path = os.path.join(self.root, path)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        found = self.keyPattern.search(text)
        return found.group(0) if found else text.strip()
