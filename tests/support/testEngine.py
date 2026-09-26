import os
import tempfile

from emostack.core.config import config
from emostack.core.timeSource import timeSource
from emostack.runtime.engine import engine
from tests.support.scriptedProcessor import scriptedProcessor
from tests.support.wordEmbedder import wordEmbedder


class testEngine:
    """An engine over a fresh store, a scripted LLM model and a fixed clock."""

    start = 1790110000.0

    def __init__(self):
        self.folder = tempfile.mkdtemp()
        self.processor = scriptedProcessor()
        self.time = timeSource(fixed=self.start)
        self.engine = engine(config({"databasePath": os.path.join(self.folder, "test.db")}),
                             processor=self.processor, embedder=wordEmbedder(), time=self.time)
