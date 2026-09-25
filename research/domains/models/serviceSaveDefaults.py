class serviceSaveDefaults:
    """The models an experiment uses when none is picked: the being's, the visitors', the
    embedder, and the judges ticked by default."""

    names = ("defaultSheepModel", "defaultVisitorModel", "defaultEmbedModel")

    def __init__(self, repository):
        self.repository = repository

    def save(self, form):
        for name in self.names:
            self.repository.setSetting(name, form.get(name, ""))

    def defaults(self):
        return {name: self.repository.setting(name) for name in self.names}
