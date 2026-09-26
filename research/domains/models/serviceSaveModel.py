class serviceSaveModel:
    """Adds or changes a model. A key is better kept in a file outside the panel: then only the
    file's path is stored."""

    def __init__(self, repository):
        self.repository = repository

    def save(self, form, modelId=None):
        values = {
            "label": form.get("label", "").strip() or form.get("model", "").strip(),
            "kind": "embed" if form.get("kind") == "embed" else "chat",
            "baseUrl": form.get("baseUrl", "").strip(),
            "model": form.get("model", "").strip(),
            "apiKey": form.get("apiKey", "").strip(),
            "apiKeyFile": form.get("apiKeyFile", "").strip(),
            "jsonMode": form.get("jsonMode", "jsonObject"),
            "maxTokens": int(form.get("maxTokens") or 2048),
            "maxTokensParam": form.get("maxTokensParam", "max_tokens").strip() or "max_tokens",
            "supportsTemperature": 1 if form.get("supportsTemperature") else 0,
            "timeoutSeconds": int(form.get("timeoutSeconds") or 240),
            "extraBody": form.get("extraBody", "").strip(),
        }
        if modelId and not values["apiKey"]:
            values.pop("apiKey")
        if not values["baseUrl"] or not values["model"]:
            raise ValueError("a model needs a base URL and a model name")
        return self.repository.save(values, modelId)
