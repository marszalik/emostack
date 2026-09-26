class repositoryModels:
    """The LLM models and embedders the panel can run with, and the panel's default choices."""

    schema = [
        """CREATE TABLE IF NOT EXISTS models (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             label TEXT NOT NULL,
             kind TEXT NOT NULL DEFAULT 'chat',
             baseUrl TEXT NOT NULL,
             model TEXT NOT NULL,
             apiKey TEXT NOT NULL DEFAULT '',
             apiKeyFile TEXT NOT NULL DEFAULT '',
             jsonMode TEXT NOT NULL DEFAULT 'jsonObject',
             maxTokens INTEGER NOT NULL DEFAULT 2048,
             maxTokensParam TEXT NOT NULL DEFAULT 'max_tokens',
             supportsTemperature INTEGER NOT NULL DEFAULT 1,
             timeoutSeconds INTEGER NOT NULL DEFAULT 240,
             extraBody TEXT NOT NULL DEFAULT ''
           )""",
        "CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '')",
    ]
    fields = ("label", "kind", "baseUrl", "model", "apiKey", "apiKeyFile", "jsonMode", "maxTokens",
              "maxTokensParam", "supportsTemperature", "timeoutSeconds", "extraBody")

    def __init__(self, database):
        self.database = database
        database.ensureSchema("models", self.schema)

    def all(self):
        return [dict(row) for row in self.database.read("SELECT * FROM models ORDER BY kind, label")]

    def get(self, modelId):
        row = self.database.readOne("SELECT * FROM models WHERE id = ?", (modelId,))
        return dict(row) if row else None

    def save(self, values, modelId=None):
        names = [name for name in self.fields if name in values]
        if modelId:
            self.database.write(f"UPDATE models SET {', '.join(f'{name} = ?' for name in names)} WHERE id = ?",
                                [values[name] for name in names] + [modelId])
            return modelId
        cursor = self.database.write(
            f"INSERT INTO models ({', '.join(names)}) VALUES ({', '.join('?' for _ in names)})",
            [values[name] for name in names])
        return cursor.lastrowid

    def delete(self, modelId):
        self.database.write("DELETE FROM models WHERE id = ?", (modelId,))

    def setting(self, name, default=""):
        row = self.database.readOne("SELECT value FROM settings WHERE name = ?", (name,))
        return row["value"] if row else default

    def setSetting(self, name, value):
        self.database.write("INSERT INTO settings (name, value) VALUES (?, ?) "
                            "ON CONFLICT(name) DO UPDATE SET value = excluded.value", (name, str(value)))
