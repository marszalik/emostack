import json
import urllib.error
import urllib.request

from emostack.core.processor import processor
from emostack.core.ProcessorError import ProcessorError


class openAiCompatibleProcessor(processor):
    """An LLM model behind an OpenAI-compatible chat completions endpoint.

    jsonMode says how the backend accepts a request for JSON:
      jsonObject  {"type": "json_object"}
      jsonSchema  the strict schema the caller supplies (a plain JSON request then sends nothing)
      none        nothing; the prompt and the tolerant parser carry it
    """

    def __init__(self, settings):
        super().__init__()
        self.baseUrl = settings["baseUrl"].rstrip("/")
        self.apiKey = settings["apiKey"]
        self.model = settings["model"]
        self.jsonMode = settings.get("jsonMode", "jsonObject")
        self.maxTokens = int(settings.get("maxTokens", 2048))
        self.maxTokensParam = settings.get("maxTokensParam", "max_tokens")
        self.supportsTemperature = bool(settings.get("supportsTemperature", True))
        self.timeoutSeconds = int(settings.get("timeoutSeconds", 240))
        self.extraBody = dict(settings.get("extraBody") or {})

    def _send(self, system, messages, temperature, responseFormat):
        body = {"model": self.model,
                "messages": ([{"role": "system", "content": system}] if system else []) + list(messages)}
        if self.supportsTemperature:
            body["temperature"] = temperature
        if self.maxTokens:
            body[self.maxTokensParam] = self.maxTokens
        requested = self._responseFormat(responseFormat)
        if requested:
            body["response_format"] = requested
        body.update(self.extraBody)
        data = self._post("/chat/completions", body)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as error:
            raise ProcessorError(f"unexpected chat response: {data}") from error

    def _responseFormat(self, responseFormat):
        if not responseFormat or self.jsonMode == "none":
            return None
        if self.jsonMode == "jsonObject":
            return {"type": "json_object"}
        if self.jsonMode == "jsonSchema" and responseFormat.get("type") == "json_schema":
            schema = dict(responseFormat.get("json_schema") or {})
            schema.setdefault("name", "response")
            schema["strict"] = True
            return {"type": "json_schema", "json_schema": schema}
        return None

    def _post(self, path, body):
        request = urllib.request.Request(
            self.baseUrl + path,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.apiKey}",
                "User-Agent": "EmoStack/3",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeoutSeconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ProcessorError(f"HTTP {error.code} from {path}: {detail}") from error
        except urllib.error.URLError as error:
            raise ProcessorError(f"network error calling {path}: {error}") from error
