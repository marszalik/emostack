import hashlib
import math
import re

from emostack.core.embedder import embedder


class wordEmbedder(embedder):
    """An embedder for tests: a bag of words hashed into a small vector, so that texts sharing
    words are near."""

    size = 64

    def embed(self, text):
        vector = [0.0] * self.size
        for word in re.findall(r"\w+", (text or "").lower()):
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % self.size] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]
