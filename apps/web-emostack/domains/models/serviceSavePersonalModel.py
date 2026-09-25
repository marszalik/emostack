from domains.models.Provider import Provider
from domains.models.Purpose import Purpose


class serviceSavePersonalModel:
    """Checks and keeps a person's model. A key left empty keeps the one saved for the same
    provider. In the advanced settings a kind of call may go to another model; its key may be left
    empty when it is the same provider as the main one."""

    def __init__(self, models):
        self.models = models

    def build(self, email, form):
        saved = self.models.get(email) or {}
        main = self._model(form.get("provider"), form.get("model"), form.get("baseUrl"), form.get("apiKey"),
                           form.get("jsonMode"), saved if saved.get("provider") == form.get("provider") else {})
        routes = {}
        savedRoutes = saved.get("routes", {})
        for purpose in Purpose.all():
            provider = form.get(f"route.{purpose.name}.provider")
            if not provider:
                continue
            previous = savedRoutes.get(purpose.name, {})
            fallback = previous if previous.get("provider") == provider else (main if main["provider"] == provider else {})
            routes[purpose.name] = self._model(provider, form.get(f"route.{purpose.name}.model"),
                                               form.get(f"route.{purpose.name}.baseUrl"),
                                               form.get(f"route.{purpose.name}.apiKey"), None, fallback)
        main["routes"] = routes
        main["embedModel"] = (form.get("embedModel") or "").strip() or (
            saved.get("embedModel", "") if saved.get("provider") == main["provider"] else "")
        return main

    def save(self, email, form):
        model = self.build(email, form)
        self.models.save(email, model)
        return model

    @staticmethod
    def _model(providerName, model, baseUrl, apiKey, jsonMode, fallback):
        provider = Provider.named((providerName or "").strip().lower())
        model = (model or "").strip()
        if not model:
            raise ValueError("give the model name")
        address = (baseUrl or "").strip() if provider.name == "custom" else provider.baseUrl
        if not address.startswith(("http://", "https://")):
            raise ValueError("the endpoint address must start with http:// or https://")
        key = (apiKey or "").strip() or fallback.get("apiKey", "")
        if not key:
            raise ValueError("paste the API key")
        mode = jsonMode if jsonMode in ("jsonObject", "jsonSchema", "none") else provider.jsonMode
        return {"provider": provider.name, "baseUrl": address.rstrip("/"), "model": model, "apiKey": key,
                "jsonMode": mode}
