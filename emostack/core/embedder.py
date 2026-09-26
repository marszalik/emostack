class embedder:
    """Turns a text into a vector. Vectors of different models cannot be compared, so every
    reader checks the length before comparing."""

    def embed(self, text):
        raise NotImplementedError
