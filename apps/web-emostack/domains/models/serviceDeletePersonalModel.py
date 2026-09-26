class serviceDeletePersonalModel:
    def __init__(self, models):
        self.models = models

    def delete(self, email):
        self.models.delete(email)
