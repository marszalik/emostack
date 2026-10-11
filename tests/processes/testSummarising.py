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

    def testAFoldedMemoryIsSummarisedAsRecalledInTheConversation(self):
        processor = scriptedProcessor()
        entries = [FocusEntry(record("Tom said: hello."), FocusEntry.THIS_CONVERSATION),
                   FocusEntry(record("Azor ran in the park."), FocusEntry.EVOKED_FROM_BEFORE)]
        self.assertEqual(summarising(processor).fold("Maya", "", entries, before=False), "We talked.")
        call = processor.callsFor("summarising")[0]
        self.assertIn("earlier in this conversation", call["system"])
        self.assertIn("- Tom said: hello.", call["user"])
        self.assertIn("- I recalled: Azor ran in the park.", call["user"])

    def testWhatWasBroughtInIsFoldedAsBeforeTheConversation(self):
        processor = scriptedProcessor()
        entries = [FocusEntry(record("Anna lost her dog."), FocusEntry.CARRIED_FROM_BEFORE)]
        summarising(processor).fold("Maya", "", entries, before=True)
        call = processor.callsFor("summarising")[0]
        self.assertIn("before this conversation", call["system"])
        self.assertIn("- Anna lost her dog.", call["user"])


if __name__ == "__main__":
    unittest.main()
