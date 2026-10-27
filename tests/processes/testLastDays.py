import unittest

from emostack.containers.Focus import Focus
from emostack.containers.LastDays import LastDays
from emostack.core.ProcessorError import ProcessorError
from emostack.processes.lastDays.lastDays import lastDays
from tests.support.scriptedProcessor import scriptedProcessor


class episode:
    def __init__(self, text, happenedAt=0.0):
        self.happenedAt = happenedAt
        self._text = text

    def text(self, rendering):
        return self._text


class record:
    def __init__(self, recordId, *texts):
        self.id = recordId
        self.episodes = [episode(text, index) for index, text in enumerate(texts)]


class being:
    id = 7
    name = "Maya"


class memoryRepository:
    def __init__(self):
        self.rows = {}

    def get(self, beingId):
        return self.rows.get(beingId, LastDays())

    def save(self, beingId, days):
        self.rows[beingId] = LastDays(days.today, days.yesterday, days.before)


def conversation(*texts):
    focus = Focus(size=2)
    for at, text in enumerate(texts):
        focus.pushMoment(record(f"m{at}", text), at)
    focus.fold(focus.overflow())
    return focus


class testLastDays(unittest.TestCase):

    def testTheConversationThatEndedIsFoldedIntoToday(self):
        processor = scriptedProcessor()
        processor.prepare("lastDays", "Jan came and counted to three; I said each number back.")
        repository = memoryRepository()
        layer = lastDays(processor, repository, being())
        layer.conversationEnded(conversation("Jan entered.", "Jan said 'One.' and Maya replied 'One.'",
                                             "Jan said 'Two.' and Maya replied 'Two.'"))
        call = processor.callsFor("lastDays")[0]
        self.assertIn("A conversation has just ended", call["system"])
        self.assertIn("(nothing yet)", call["user"])
        self.assertIn("- Jan entered.", call["user"])
        self.assertIn("- Jan said 'Two.' and Maya replied 'Two.'", call["user"])
        self.assertEqual(repository.get(7).today, "Jan came and counted to three; I said each number back.")

    def testASecondConversationOfTheDayGrowsTheAccountOfToday(self):
        processor = scriptedProcessor()
        repository = memoryRepository()
        repository.save(7, LastDays(today="Jan came and counted."))
        lastDays(processor, repository, being()).conversationEnded(conversation("Ann entered."))
        self.assertIn("My account of today so far:\nJan came and counted.", processor.callsFor("lastDays")[0]["user"])

    def testTheNightTurnsTheDaysAndFoldsYesterdayIntoTheDaysBefore(self):
        processor = scriptedProcessor()
        processor.prepare("lastDays", "Jan counted from one to ten over two days and I repeated each number.")
        repository = memoryRepository()
        repository.save(7, LastDays(today="Jan counted six to ten.", yesterday="Jan counted one to five.",
                                    before=""))
        lastDays(processor, repository, being()).night()
        call = processor.callsFor("lastDays")[0]
        self.assertIn("over the last days", call["system"])
        self.assertIn("And then, the day after that:\nJan counted one to five.", call["user"])
        days = repository.get(7)
        self.assertEqual(days.today, "")
        self.assertEqual(days.yesterday, "Jan counted six to ten.")
        self.assertEqual(days.before, "Jan counted from one to ten over two days and I repeated each number.")

    def testTheFirstNightNeedsNoFold(self):
        processor = scriptedProcessor()
        repository = memoryRepository()
        repository.save(7, LastDays(today="Jan counted one to five."))
        lastDays(processor, repository, being()).night()
        self.assertEqual(processor.callsFor("lastDays"), [])
        self.assertEqual(repository.get(7).yesterday, "Jan counted one to five.")
        self.assertEqual(repository.get(7).before, "")

    def testAFailedCallLeavesTheAccountAsItWas(self):
        processor = scriptedProcessor()
        processor.prepare("lastDays", ProcessorError("down"), ProcessorError("down"))
        repository = memoryRepository()
        repository.save(7, LastDays(today="Jan counted.", yesterday="Ann came.", before="Tom came."))
        layer = lastDays(processor, repository, being())
        layer.conversationEnded(conversation("Carol entered."))
        self.assertEqual(repository.get(7).today, "Jan counted.")
        layer.night()
        days = repository.get(7)
        self.assertEqual(days.yesterday, "Jan counted.")
        self.assertEqual(days.before, "Tom came.\nAnn came.")

    def testSwitchedOffItKeepsNothingAndShowsNothing(self):
        processor = scriptedProcessor()
        repository = memoryRepository()
        layer = lastDays(processor, repository, being(), enabled=False)
        layer.conversationEnded(conversation("Jan entered."))
        layer.night()
        self.assertIsNone(layer.current())
        self.assertEqual(processor.calls, [])
        self.assertEqual(repository.rows, {})


if __name__ == "__main__":
    unittest.main()
