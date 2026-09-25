class Candidate:
    """A record recall scored for the present words: meaning multiplied by how strongly it is still
    felt, lifted by the names it carries."""

    def __init__(self, score, similarity, record):
        self.score = score
        self.similarity = similarity
        self.record = record
