import unittest

from emostack.construct.Belief import Belief
from emostack.construct.Decision import Decision
from emostack.containers.AccessibilitySlot import AccessibilitySlot
from emostack.emoThought.Strength import Strength


class memorySlotRepository:
    def __init__(self):
        self.places = []

    def held(self, beingId):
        return list(self.places)

    def replace(self, beingId, places):
        self.places = list(places)


class testAccessibilitySlot(unittest.TestCase):

    def construct(self, cls, name, intensity):
        return cls(id=name, beingId=1, text=name, feeling="", conclusion="", valence=0.1,
                   strength=Strength(intensity, 0), happenedAt=0)

    def slot(self):
        slot = AccessibilitySlot(1, None, memorySlotRepository(), size=3, days=7)
        slot.loaded = True
        return slot

    def testABeliefCannotTakeTheReservedPlace(self):
        slot = self.slot()
        slot.activate(self.construct(Decision, "decided", 0.6), 1)
        slot.activate(self.construct(Belief, "b1", 0.9), 2)
        slot.activate(self.construct(Belief, "b2", 0.9), 3)
        slot.activate(self.construct(Belief, "b3", 0.95), 4)
        self.assertEqual(len(slot.held()), 3)
        self.assertIn("decided", slot.ids())
        self.assertNotIn("b1", slot.ids())

    def testAWeakerBeliefDoesNotEnterAFullSlot(self):
        slot = self.slot()
        for index, name in enumerate(["b1", "b2", "b3"]):
            slot.activate(self.construct(Belief, name, 0.9), index)
        self.assertFalse(slot.activate(self.construct(Belief, "weak", 0.5), 10))
        self.assertEqual(slot.ids(), {"b1", "b2", "b3"})

    def testAnArrivingActTakesThePlaceOfTheOldestBelief(self):
        slot = self.slot()
        for index, name in enumerate(["b1", "b2", "b3"]):
            slot.activate(self.construct(Belief, name, 0.9), index)
        slot.activate(self.construct(Decision, "decided", 0.6), 10)
        self.assertEqual(slot.ids(), {"b2", "b3", "decided"})

    def testANewerActReplacesTheHeldOne(self):
        slot = self.slot()
        slot.activate(self.construct(Decision, "first", 0.6), 1)
        slot.activate(self.construct(Decision, "second", 0.6), 2)
        self.assertEqual(slot.ids(), {"second"})
