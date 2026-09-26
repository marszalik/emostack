class serviceDeleteCoding:
    def __init__(self, codings):
        self.codings = codings

    def delete(self, codingId):
        self.codings.delete(codingId)
