import json


class repositoryPersonalModels:
    """The model and key each person talks on, and the models they chose for single kinds of call.
    Keys live only here, in the application's database, never in a page."""

    schema = [
        """CREATE TABLE IF NOT EXISTS personalModels (
             email TEXT PRIMARY KEY,
             provider TEXT NOT NULL,
             baseUrl TEXT NOT NULL,
             model TEXT NOT NULL,
             apiKey TEXT NOT NULL,
             jsonMode TEXT NOT NULL,
             embedModel TEXT NOT NULL DEFAULT '',
             routes TEXT NOT NULL DEFAULT '{}'
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("personalModels", self.schema)

    def get(self, email):
        row = self.database.readOne("SELECT * FROM personalModels WHERE email = ?", (email,))
        if row is None:
            return None
        model = dict(row)
        model["routes"] = json.loads(model["routes"] or "{}")
        return model

    def save(self, email, model):
        self.database.write(
            "INSERT INTO personalModels (email, provider, baseUrl, model, apiKey, jsonMode, embedModel, routes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(email) DO UPDATE SET provider = excluded.provider, "
            "baseUrl = excluded.baseUrl, model = excluded.model, apiKey = excluded.apiKey, jsonMode = excluded.jsonMode, "
            "embedModel = excluded.embedModel, routes = excluded.routes",
            (email, model["provider"], model["baseUrl"], model["model"], model["apiKey"], model["jsonMode"],
             model.get("embedModel", ""), json.dumps(model.get("routes", {}))))

    def delete(self, email):
        self.database.write("DELETE FROM personalModels WHERE email = ?", (email,))
