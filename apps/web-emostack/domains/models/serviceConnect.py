from emostack.core.localEmbedder import localEmbedder
from emostack.core.openAiCompatibleProcessor import openAiCompatibleProcessor
from emostack.core.routedProcessor import routedProcessor
from domains.models.Provider import Provider
from domains.models.repositoryPersonalModels import repositoryPersonalModels


class serviceConnect:
    """The LLM model and the embedder a person's beings run on: an administrator's on the server's
    own settings, everyone else's on their own key. One store keeps vectors of one embedder: a change
    of provider makes older memories unsearchable, so the embedder follows the main provider only."""

    reasoningPrefixes = ("gpt-5", "o1", "o3", "o4")

    def __init__(self, application):
        self.config = application.config
        self.models = repositoryPersonalModels(application.database)

    def hasModel(self, person):
        return person.isAdministrator() or self.models.get(person.email) is not None

    def processor(self, person):
        if person.isAdministrator() and self.models.get(person.email) is None:
            return openAiCompatibleProcessor(self.config.serverProcessor)
        saved = self.models.get(person.email)
        if saved is None:
            raise ValueError("set your model first")
        routes = {purpose: self._processor(model) for purpose, model in saved["routes"].items()}
        return routedProcessor(self._processor(saved), routes)

    def embedder(self, person):
        saved = self.models.get(person.email)
        if saved is None or not Provider.named(saved["provider"]).hasEmbeddings():
            return localEmbedder(self.config.serverEmbedder)
        provider = Provider.named(saved["provider"])
        return localEmbedder({"baseUrl": saved["baseUrl"], "apiKey": saved["apiKey"],
                              "model": saved.get("embedModel") or provider.embedModel})

    def processorFor(self, model):
        return self._processor(model)

    def _processor(self, model):
        reasoning = model["model"].startswith(self.reasoningPrefixes)
        return openAiCompatibleProcessor({
            "baseUrl": model["baseUrl"], "apiKey": model["apiKey"], "model": model["model"],
            "jsonMode": model["jsonMode"], "maxTokens": 4096, "timeoutSeconds": 120,
            "maxTokensParam": "max_completion_tokens" if reasoning else "max_tokens",
            "supportsTemperature": not reasoning})
