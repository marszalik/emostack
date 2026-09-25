class Provider:
    """A provider of LLM models behind an OpenAI-compatible endpoint, and where its embeddings are.
    A provider without embeddings (Anthropic) has the being's memory vectors made by the server's
    own small embedder."""

    def __init__(self, name, label, baseUrl, jsonMode, models, keyHint, embedModel=None):
        self.name = name
        self.label = label
        self.baseUrl = baseUrl
        self.jsonMode = jsonMode
        self.models = models
        self.keyHint = keyHint
        self.embedModel = embedModel

    def hasEmbeddings(self):
        return self.embedModel is not None

    @classmethod
    def all(cls):
        return [
            cls("anthropic", "Anthropic (Claude)", "https://api.anthropic.com/v1", "jsonSchema",
                ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-sonnet-5", "claude-opus-5"], "sk-ant-…"),
            cls("openai", "OpenAI", "https://api.openai.com/v1", "jsonObject",
                ["gpt-4o-mini", "gpt-4o", "gpt-5"], "sk-…", "text-embedding-3-small"),
            cls("google", "Google (Gemini)", "https://generativelanguage.googleapis.com/v1beta/openai", "jsonObject",
                ["gemini-2.5-flash", "gemini-2.5-pro"], "AIza…", "gemini-embedding-001"),
            cls("custom", "other (an OpenAI-compatible endpoint)", "", "jsonObject", [], "API key",
                "text-embedding-3-small"),
        ]

    @classmethod
    def named(cls, name):
        found = next((provider for provider in cls.all() if provider.name == name), None)
        if found is None:
            raise ValueError("choose a provider")
        return found

    def toDict(self):
        return {"name": self.name, "label": self.label, "baseUrl": self.baseUrl, "jsonMode": self.jsonMode,
                "models": self.models, "keyHint": self.keyHint, "embeddings": self.hasEmbeddings()}
