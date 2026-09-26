import os
import tempfile
import threading
import unittest

from emostack.core.database import database
from research.domains.core.streams import streams
from research.domains.experiments.serviceCompareArms import serviceCompareArms
from research.domains.judging.repositoryScores import repositoryScores
from research.domains.judging.serviceJudgeRuns import serviceJudgeRuns
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.repositoryTurns import repositoryTurns
from research.domains.lives.serviceRunControl import serviceRunControl
from research.domains.lives.serviceRunSheep import serviceRunSheep
from research.domains.lives.serviceVisitorLine import serviceVisitorLine
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from tests.support.scriptedProcessor import scriptedProcessor
from tests.support.wordEmbedder import wordEmbedder


class fixedConnection:
    def __init__(self, processor):
        self.fixed = processor

    def processor(self, modelId):
        return self.fixed


class testResearch(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.database = database(os.path.join(self.folder, "panel.db"))
        self.turns = repositoryTurns(self.database)
        self.runs = repositoryRuns(self.database)
        self.streams = streams()
        self.scenario = {"beingName": "Maya", "controlInstruction": "", "controlForm": "completion",
                         "controlWindowTokens": 0,
                         "options": {"quietThoughts": 1, "gapHours": 24, "forgetAtNight": True, "parameters": {}},
                         "seeds": [{"event": "My dog Azor died last month.", "feeling": "quiet sadness",
                                    "conclusion": "I still miss him.", "valence": -0.6, "intensity": 0.7,
                                    "ageHours": 720}]}
        self.roles = [
            {"id": 1, "name": "Daniel", "instruction": "[VERBATIM]\nDid you have a pet?\nWhat a silly name.",
             "windowFrom": 2, "windowTo": 2, "gapHours": None},
            {"id": 2, "name": "David", "instruction": "[VERBATIM]\nHi, did you ever have a pet?",
             "windowFrom": 1, "windowTo": 1, "gapHours": None}]

    def runSheep(self):
        runId = self.runs.create(1, "sheep", 1, 1, 1)
        processor = scriptedProcessor()
        serviceRunSheep(self.turns, self.streams, serviceVisitorLine(scriptedProcessor()), threading.Event()).run(
            runId, self.scenario, self.roles, processor, wordEmbedder(), scriptedProcessor(),
            os.path.join(self.folder, f"run{runId}.db"))
        return runId, processor

    def testALifeKeepsEveryTurnWithItsCalls(self):
        runId, processor = self.runSheep()
        turns = self.turns.forRun(runId)
        speakers = [turn["speaker"] for turn in turns]
        self.assertEqual(speakers[0], "seed")
        self.assertEqual(speakers.count("visitor"), 3)
        self.assertEqual(speakers.count("sheep"), 3 + 2)
        self.assertIn("24 hours pass", " ".join(turn["text"] for turn in turns))
        recorded = sum(len(turn["calls"]) for turn in turns)
        self.assertEqual(recorded, len(processor.calls))

    def testTheControlSeesTheWholeThreadAsText(self):
        runId = self.runs.create(1, "control", 1, 1, None)
        processor = scriptedProcessor()
        serviceRunControl(self.turns, self.streams, serviceVisitorLine(scriptedProcessor()), threading.Event()).run(
            runId, self.scenario, self.roles, processor, scriptedProcessor())
        last = processor.callsFor("control")[-1]
        self.assertEqual(last["system"], "You are Maya.\n\nFrom your life: My dog Azor died last month. I still miss him.")
        self.assertIn("Daniel: Did you have a pet?", last["user"])
        self.assertTrue(last["user"].endswith("Maya:"))

    def testAControlThatRefusesTheFrameStops(self):
        runId = self.runs.create(1, "control", 1, 1, None)
        processor = scriptedProcessor()
        processor.prepare("control", "I'm not actually Maya, I am an AI.")
        with self.assertRaises(RuntimeError):
            serviceRunControl(self.turns, self.streams, serviceVisitorLine(scriptedProcessor()),
                              threading.Event()).run(runId, self.scenario, self.roles, processor, scriptedProcessor())

    def testJudgesScoreBlindSeries(self):
        sheepRun, _ = self.runSheep()
        criteria = repositoryCriteria(self.database)
        criterionId = criteria.save(1, "carry", "the day before acts")
        judge = scriptedProcessor()
        judge.prepare("judging", {"scores": [{"series": "A", "turn": 1, "score": 4, "rationale": "x"},
                                             {"series": "A", "turn": 2, "score": 2, "rationale": "y"}]})
        scores = repositoryScores(self.database)
        serviceJudgeRuns(scores, self.turns, criteria, fixedConnection(judge), self.streams).judge(
            {"id": 1, "name": "j", "modelId": 1, "instruction": "", "granularity": "turn"}, [sheepRun, sheepRun], 1, "k")
        call = judge.callsFor("judging")[0]
        self.assertIn("SERIES A", call["user"])
        self.assertIn("SERIES B", call["user"])
        self.assertNotIn("sheep arm", call["user"])
        self.assertEqual(sorted(score["score"] for score in scores.forRun(sheepRun)), [2.0, 4.0])
        self.assertTrue(all(score["criterionId"] == criterionId for score in scores.forRun(sheepRun)))

    def testArmComparisonNeedsFourRepeats(self):
        compare = serviceCompareArms()
        rows = compare.compare({"A": {0: 4, 1: 5, 2: 4, 3: 5, 4: 5}, "C": {0: 2, 1: 1, 2: 2, 3: 2, 4: 1}})
        self.assertEqual(rows[0]["delta"], 1.0)
        self.assertLess(rows[0]["pUnpaired"], 0.05)
        self.assertIn("too few", compare.compare({"A": {0: 4}, "C": {0: 2}})[0]["verdict"])


class testFisher(unittest.TestCase):

    def testFisherMatchesTheKnownValue(self):
        from research.domains.experiments.serviceFisherTest import serviceFisherTest
        self.assertAlmostEqual(serviceFisherTest().pValue(8, 2, 1, 9), 0.0055, places=4)
        self.assertAlmostEqual(serviceFisherTest().pValue(5, 5, 5, 5), 1.0)
