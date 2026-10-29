"""The memory of a Generative Agent (Park et al., 2023), reimplemented for the panel's control arm: a memory stream
of observations in natural language with a time stamp, an importance score asked of the model once per observation,
retrieval by recency + importance + relevance (each normalised to 0..1, equal weights), and reflection when the sum
of importance since the last reflection crosses a threshold: three salient questions over the most recent memories,
retrieval for each, insights with citations stored back into the stream. Planning is not reimplemented: there is no
world with a daily schedule here; the visitor drives every exchange. Nothing is felt, nothing is withheld from a call.
Parameters (arm parameters, all optional): gaReflectionThreshold (default 30, the paper's 150 scaled to a day of a
few exchanges), gaRetrieve (default 12 memories), gaRecentForReflection (default 100), gaDecay (default 0.995 per
simulated hour), gaHoursPerExchange (default 0.05), gaScoreTemperature (default 0.3)."""
import math
import re

from emostack.core.ProcessorError import ProcessorError
from emostack.core.promptTemplate import promptTemplate


class generativeAgentMemory:
    def __init__(self, processor, embedder, name, parameters, note):
        self.processor = processor
        self.embedder = embedder
        self.name = name
        self.note = note                      # note(text): writes an event line into the run's turns
        self.threshold = float(parameters.get("gaReflectionThreshold", 30))
        self.retrieveCount = int(parameters.get("gaRetrieve", 12))
        self.recentForReflection = int(parameters.get("gaRecentForReflection", 100))
        self.decay = float(parameters.get("gaDecay", 0.995))
        self.hoursPerExchange = float(parameters.get("gaHoursPerExchange", 0.05))
        self.scoreTemperature = float(parameters.get("gaScoreTemperature", 0.3))
        self.template = promptTemplate.beside(__file__, "generativeAgents.prompt")
        self.stream = []                      # dicts: text, kind, created, accessed, importance, embedding
        self.sinceReflection = 0.0
        self.now = 0.0                        # simulated hours

    # ---- time -----------------------------------------------------------------------------------------------
    def startDay(self, day):
        self.now = day * 24.0

    def tick(self):
        self.now += self.hoursPerExchange

    # ---- the stream -----------------------------------------------------------------------------------------
    def observe(self, text, kind="observation", importance=None):
        importance = self._importance(text) if importance is None else importance
        try:
            embedding = self.embedder.embed(text)
        except ProcessorError:
            embedding = None
        self.stream.append({"text": text, "kind": kind, "created": self.now, "accessed": self.now,
                            "importance": importance, "embedding": embedding})
        self.sinceReflection += importance
        return importance

    def _importance(self, text):
        try:
            answer = self.processor.chat(self.template.fill("importanceSystem", BEING=self.name),
                                         self.template.fill("importanceUser", MEMORY=text),
                                         self.scoreTemperature, purpose="gaImportance")
        except ProcessorError:
            return 5.0
        found = re.search(r"\b(10|[1-9])\b", answer or "")
        return float(found.group(1)) if found else 5.0

    # ---- retrieval ------------------------------------------------------------------------------------------
    def retrieve(self, query, count=None):
        count = self.retrieveCount if count is None else count
        if not self.stream:
            return []
        try:
            q = self.embedder.embed(query)
        except ProcessorError:
            q = None
        recency = [self.decay ** max(0.0, self.now - m["accessed"]) for m in self.stream]
        importance = [m["importance"] / 10.0 for m in self.stream]
        relevance = [self._cosine(q, m["embedding"]) for m in self.stream]
        total = [a + b + c for a, b, c in zip(self._normalise(recency), self._normalise(importance), self._normalise(relevance))]
        order = sorted(range(len(self.stream)), key=lambda i: total[i], reverse=True)[:count]
        chosen = [self.stream[i] for i in sorted(order)]      # in the order they were formed
        for m in chosen:
            m["accessed"] = self.now
        return chosen

    @staticmethod
    def _normalise(values):
        lo, hi = min(values), max(values)
        return [0.0 if hi == lo else (v - lo) / (hi - lo) for v in values]

    @staticmethod
    def _cosine(a, b):
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def memoriesText(self, memories):
        return "\n".join(f"- {self._when(m)}: {m['text']}" for m in memories)

    def _when(self, m):
        age = self.now - m["created"]
        if age < 1.0:
            return "just now"
        if age < 20.0:
            return f"{int(age)} hours ago"
        return f"{int(round(age / 24.0))} day(s) ago"

    # ---- reflection -----------------------------------------------------------------------------------------
    def maybeReflect(self, force=False):
        if not self.stream or (self.sinceReflection < self.threshold and not force):
            return None
        recent = self.stream[-self.recentForReflection:]
        statements = "\n".join(f"{i + 1}. {m['text']}" for i, m in enumerate(recent))
        try:
            questions = self.processor.chat(self.template.fill("reflectSystem", BEING=self.name),
                                            self.template.fill("questionsUser", STATEMENTS=statements),
                                            self.scoreTemperature, purpose="gaQuestions")
        except ProcessorError:
            return None
        questionLines = [q.strip(" -*0123456789.)") for q in (questions or "").split("\n") if q.strip()][:3]
        insights = []
        for question in questionLines:
            memories = self.retrieve(question, count=15)
            numbered = "\n".join(f"{i + 1}. {m['text']}" for i, m in enumerate(memories))
            try:
                answer = self.processor.chat(self.template.fill("reflectSystem", BEING=self.name),
                                             self.template.fill("insightsUser", BEING=self.name, STATEMENTS=numbered),
                                             self.scoreTemperature, purpose="gaInsights")
            except ProcessorError:
                continue
            for line in (answer or "").split("\n"):
                line = line.strip(" -*").strip()
                line = re.sub(r"^\d+[.)]\s*", "", line)
                if len(line) > 10 and line not in insights:
                    insights.append(line)
        self.sinceReflection = 0.0
        for insight in insights[:15]:
            self.observe(insight, kind="reflection")
        if self.note:
            self.note(f"reflection; questions: {' | '.join(questionLines)}; insights: {' | '.join(insights[:15])}")
        return insights
