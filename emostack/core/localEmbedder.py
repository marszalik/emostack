import json
import urllib.error
import urllib.request

from emostack.core.embedder import embedder
from emostack.core.ProcessorError import ProcessorError


class localEmbedder(embedder):
    """An embedding model behind an OpenAI-compatible /embeddings endpoint, typically a local
    server."""

    def __init__(self, settings):
        self.baseUrl = settings["baseUrl"].rstrip("/")
        self.apiKey = settings.get("apiKey", "")
        self.model = settings["model"]
        self.timeoutSeconds = int(settings.get("timeoutSeconds", 240))

    def embed(self, text):
        body = {"model": self.model, "input": [text]}
        request = urllib.request.Request(
            self.baseUrl + "/embeddings",
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
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ProcessorError(f"HTTP {error.code} from /embeddings: {detail}") from error
        except urllib.error.URLError as error:
            raise ProcessorError(f"network error calling /embeddings: {error}") from error
        try:
            return data["data"][0]["embedding"]
        except (KeyError, IndexError) as error:
            raise ProcessorError(f"unexpected embeddings response: {data}") from error
