import math
import re

from emostack.processes.recall.Cluster import Cluster


class ruminationClusters:
    """Groups records that are the same feeling recurring: their feeling and conclusion share most
    words, their conclusions are the same, or their vectors are almost equal."""

    stopWords = {"się", "i", "że", "to", "jest", "w", "na", "z", "o", "a", "mnie", "ale", "czuję",
                 "jak", "co", "tym", "do", "po", "the", "feel"}

    def __init__(self, vectorThreshold=0.92, wordOverlap=0.6):
        self.vectorThreshold = vectorThreshold
        self.wordOverlap = wordOverlap

    def cluster(self, records):
        clusters = []
        for record in records:
            for cluster in clusters:
                if self._same(record, cluster.representative):
                    cluster.add(record)
                    break
            else:
                clusters.append(Cluster(record))
        return clusters

    def _same(self, a, b):
        if self._overlap(self._words(f"{a.feeling} {a.conclusion}"),
                         self._words(f"{b.feeling} {b.conclusion}")) >= self.wordOverlap:
            return True
        if self._normal(a.conclusion) and self._normal(a.conclusion) == self._normal(b.conclusion):
            return True
        if a.vector and b.vector and len(a.vector) == len(b.vector):
            return self._cosine(a.vector, b.vector) >= self.vectorThreshold
        return False

    @staticmethod
    def _normal(text):
        text = re.sub(r"[^\w\s]", " ", (text or "").lower())
        return re.sub(r"\s+", " ", text).strip()

    def _words(self, text):
        return {word for word in self._normal(text).split() if word and word not in self.stopWords}

    @staticmethod
    def _overlap(a, b):
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    @staticmethod
    def _cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        normA = math.sqrt(sum(x * x for x in a))
        normB = math.sqrt(sum(y * y for y in b))
        return dot / (normA * normB) if normA and normB else 0.0
