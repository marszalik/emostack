import unittest

from emostack.containers.FocusEntry import FocusEntry
from emostack.processes.summarising.summarising import summarising
from tests.support.scriptedProcessor import scriptedProcessor


class episode:
    def __init__(self, text, happenedAt=0.0):
        self.happenedAt = happenedAt
        self._text = text

    def text(self, rendering):
        return self._text


class record:
    def __init__(self, text):
        self.episodes = [episode(text)]


class testSummarising(unittest.TestCase):

    def testAFoldedMemoryIsSummarisedAsRecalledAndABroughtInFeelingAsFromBefore(self):
        processor = scriptedProcessor()
        entries = [FocusEntry(record("Anna lost her dog."), FocusEntry.CARRIED_FROM_BEFORE),
                   FocusEntry(record("Tom said: hello."), FocusEntry.THIS_CONVERSATION),
                   FocusEntry(record("Azor ran in the park."), FocusEntry.EVOKED_FROM_BEFORE)]
        self.assertEqual(summarising(processor).fold("Maya", "", entries), "We talked.")
        user = processor.callsFor("summarising")[0]["user"]
        self.assertIn("- from before this conversation: Anna lost her dog.", user)
        self.assertIn("- Tom said: hello.", user)
        self.assertIn("- I recalled: Azor ran in the park.", user)


if __name__ == "__main__":
    unittest.main()
