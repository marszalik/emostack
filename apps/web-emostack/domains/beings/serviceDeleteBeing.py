class serviceDeleteBeing:
    def __init__(self, engine):
        self.engine = engine

    def delete(self, beingId):
        if self.engine.beings.get(beingId) is None:
            raise ValueError("no such being")
        self.engine.deleteBeing(beingId)
