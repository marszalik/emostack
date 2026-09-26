class serviceDeleteModel:
    def __init__(self, repository):
        self.repository = repository

    def delete(self, modelId):
        self.repository.delete(modelId)
