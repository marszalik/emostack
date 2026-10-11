import unittest

from emostack.containers.Focus import Focus


class record:
    def __init__(self, recordId):
        self.id = recordId


class testFocus(unittest.TestCase):

    def testOnlyTheLastEntriesAreInViewAndTheOldestLeaveFirst(self):
        focus = Focus(size=2)
        for at, recordId in enumerate(("a", "b", "c")):
            focus.pushMoment(record(recordId), at)
        self.assertEqual([entry.record.id for entry in focus.overflow()], ["a"])
        focus.fold(focus.overflow(), "a happened")
        self.assertEqual([entry.record.id for entry in focus.inView()], ["b", "c"])
        self.assertEqual(focus.summary.text, "a happened")

    def testAMemoryStandsAfterTheMomentThatEvokedIt(self):
        focus = Focus(size=8)
        focus.pushCarried(record("before"), 0)
        focus.pushMoment(record("m1"), 1)
        focus.pushEvoked(record("memory"), 1)
        focus.pushMoment(record("m2"), 2)
        self.assertEqual([entry.record.id for entry in focus.line()], ["before", "m1", "memory", "m2"])

    def testAHeldThoughtIsPlacedByTimeAndDoesNotCountToTheLimit(self):
        focus = Focus(size=1)
        focus.pushMoment(record("m1"), 5)
        line = focus.line(held=[(record("belief"), 3)])
        self.assertEqual([entry.record.id for entry in line], ["belief", "m1"])
        self.assertEqual(focus.overflow(), [])

    def testAFeelingBroughtInEntersOnceAndAFoldedMemoryCanComeBack(self):
        focus = Focus(size=1)
        focus.pushCarried(record("before"), 0)
        focus.pushEvoked(record("memory"), 1)
        focus.fold(focus.overflow(), "")
        focus.pushCarried(record("before"), 2)
        self.assertEqual([entry.record.id for entry in focus.inView()], ["memory"])
        focus.pushMoment(record("m1"), 3)
        focus.fold(focus.overflow(), "")
        focus.pushEvoked(record("memory"), 4)
        self.assertEqual([entry.record.id for entry in focus.inView()], ["m1", "memory"])


if __name__ == "__main__":
    unittest.main()
