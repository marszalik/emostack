import unittest

from emostack.laws.fadingLaw import fadingLaw
from emostack.laws.forgettingThreshold import forgettingThreshold
from emostack.laws.reconsolidationLaw import reconsolidationLaw


class testLaws(unittest.TestCase):

    def testNegativeFeelingsFadeMoreSlowly(self):
        law = fadingLaw()
        day = 86400
        self.assertGreater(law.felt(1.0, day, -0.5), law.felt(1.0, day, 0.5))
        self.assertAlmostEqual(law.felt(1.0, 1000 * day, 0.5), 0.3, places=3)

    def testForgettingThresholdRisesWithAge(self):
        threshold = forgettingThreshold([[1, 0.2], [7, 0.4], [10, 0.5], [30, 0.6], [180, 0.8]])
        self.assertEqual(threshold.at(0.5), 0.0)
        self.assertAlmostEqual(threshold.at(7), 0.4)
        self.assertLess(threshold.at(3), threshold.at(20))

    def testRecurrenceRestoresTowardWhatIsFeltNeverPast(self):
        law = reconsolidationLaw(0.6)
        self.assertAlmostEqual(law.restored(0.2, 0.7), 0.5)
        self.assertEqual(law.restored(0.8, 0.3), 0.8)
