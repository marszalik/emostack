import unittest

from emostack.core.ProcessorError import ProcessorError
from tests.support.testEngine import testEngine


def reply(valence, intensity, words="I hear you.", action="none", text="", respond=True):
    return {"emothought": {"emo_summary": f"felt {valence}", "conclusion": f"concluded {valence}",
                           "valence": valence, "intensity": intensity},
            "told": f"They spoke; Maya answered '{words}'.", "reply": words, "respond": respond,
            "action": {"type": action, "text": text}}


def appraised(valence, intensity):
    return {"emothought": {"emo_summary": f"appraised {valence}", "conclusion": f"kept {valence}",
                           "valence": valence, "intensity": intensity}}


class testConversation(unittest.TestCase):

    def setUp(self):
        self.test = testEngine()
        self.engine = self.test.engine
        self.processor = self.test.processor

    def say(self, conversation, words):
        self.test.time.advance(30)
        return self.engine.hear(conversation, words)

    def records(self):
        being = self.engine.being("Maya")
        return self.engine.assemblyFor(being).hippocampus.all()

    def testAnArrivalFormsNoRecord(self):
        self.engine.open("Maya", "Daniel")
        self.assertEqual(self.records(), [])

    def testTheReplyContextShowsTheConversationUnderItsFeelings(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Did you ever have a pet?")
        self.say(conversation, "What was its name?")
        user = self.processor.callsFor("reply")[-1]["user"]
        conversationPart = user.split("=== THIS CONVERSATION SO FAR ===")[1]
        self.assertIn("Daniel said: Did you ever have a pet?", conversationPart)
        self.assertIn("you feel:", conversationPart)

    def testAMomentWhoseFeelingIsInTheStateShowsOnlyItsEvent(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Did you ever have a pet?")
        self.say(conversation, "What was its name?")
        user = self.processor.callsFor("reply")[-1]["user"]
        state = user.split("=== YOUR STATE (now) ===")[1].split("=== THIS CONVERSATION SO FAR ===")[0]
        line = [row for row in user.split("=== THIS CONVERSATION SO FAR ===")[1].splitlines()
                if "Did you ever have a pet?" in row][0]
        self.assertIn("a mild warmth", state)
        self.assertNotIn("you feel:", line)

    def testWhatLeavesViewIsFoldedIntoTheSummaryOfEvents(self):
        test = testEngine()
        test.engine.parameters["focusSize"] = 2
        conversation, _ = test.engine.open("Maya", "Daniel")
        for words in ("First thing.", "Second thing.", "Third thing.", "Fourth thing."):
            test.time.advance(30)
            test.engine.hear(conversation, words)
        folded = "\n".join(call["user"] for call in test.processor.callsFor("summarising"))
        self.assertIn("Daniel entered the conversation", folded)
        self.assertIn("Daniel said: First thing.", folded)
        self.assertNotIn("a mild warmth", folded)
        self.assertNotIn("this was kind", folded)
        self.assertLessEqual(len(conversation.focus.inView()), 2)
        user = test.processor.callsFor("reply")[-1]["user"]
        self.assertIn("=== WHAT HAS LEFT YOUR ATTENTION (your summary) ===\n  earlier in this conversation: We talked.", user)
        self.assertNotIn("First thing.", user.split("=== THIS CONVERSATION SO FAR ===")[1])

    def testAFailedFoldLeavesTheEntriesInView(self):
        test = testEngine()
        test.engine.parameters["focusSize"] = 1
        conversation, _ = test.engine.open("Maya", "Daniel")
        test.processor.prepare("summarising", ProcessorError("down"), ProcessorError("down"))
        test.time.advance(30)
        test.engine.hear(conversation, "First thing.")
        self.assertEqual(len(conversation.focus.inView()), 2)
        self.assertTrue(conversation.focus.summary.isEmpty())

    def testTheStateShowsEachFeelingWithItsConclusion(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Did you ever have a pet?")
        self.say(conversation, "Tell me more.")
        state = self.processor.callsFor("reply")[-1]["user"].split("=== YOUR STATE (now) ===")[1]
        self.assertIn("| conclusion: this was kind", state.split("===")[0])

    def testTheAppraisalDoesNotSeeTheStateOrTheDispositions(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Hello there.")
        self.say(conversation, "How are you?")
        user = self.processor.callsFor("appraisal")[-1]["user"]
        self.assertNotIn("what you feel now", user)
        self.assertNotIn("WHAT YOU HAVE LEARNED", user)
        self.assertIn("withheld on purpose", user)

    def testAFailedReplyLeavesNoRecordAndNoWords(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("reply", "not json", "not json", "not json")
        outcome = self.say(conversation, "Hello?")
        self.assertTrue(outcome.failed)
        self.assertEqual(outcome.words, "")
        self.assertEqual(self.records(), [])

    def testAChangeOfSignOpensANewRecordTheSameSignJoins(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("appraisal", appraised(0.5, 0.4), appraised(0.4, 0.5), appraised(-0.7, 0.8))
        self.say(conversation, "Nice to meet you.")
        self.say(conversation, "You seem kind.")
        self.say(conversation, "Actually your dog's name is ridiculous.")
        records = self.records()
        self.assertEqual(len(records), 2)
        negative = [record for record in records if record.valence < 0][0]
        positive = [record for record in records if record.valence > 0][0]
        self.assertAlmostEqual(positive.valence, 0.5)
        hippocampus = self.engine.assemblyFor(self.engine.being("Maya")).hippocampus
        self.assertEqual(len(hippocampus.repository.episodesOf(positive.id, 10)), 2)
        self.assertEqual(len(hippocampus.repository.episodesOf(negative.id, 10)), 1)

    def testANewBlowGetsItsOwnRecordAndTheRecalledLossComesBack(self):
        first, _ = self.engine.open("Maya", "Anna")
        self.processor.prepare("appraisal", appraised(-0.6, 0.7))
        self.say(first, "My dog Azor died last month.")
        self.engine.leave(first)
        self.test.time.advance(3 * 86400)
        hippocampus = self.engine.assemblyFor(self.engine.being("Maya")).hippocampus
        loss = [record for record in self.records() if not record.isConstruct()][0]
        faded = loss.feltAt(self.test.time.now(), self.engine.assemblyFor(self.engine.being("Maya")).fadingLaw)
        second, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("associationFilter", {"keep": [0], "asks_for_memory": False, "asks_for_own": None})
        self.processor.prepare("reply", reply(-0.7, 0.8), reply(-0.7, 0.8))
        self.processor.prepare("appraisal", appraised(-0.8, 0.8))
        self.say(second, "Azor? What a ridiculous name for a dog.")
        lived = [record for record in self.records() if not record.isConstruct()]
        self.assertEqual(len(lived), 2)
        mocked = [record for record in lived if record.id != loss.id][0]
        self.assertAlmostEqual(mocked.valence, -0.8)
        self.assertEqual(len(hippocampus.repository.episodesOf(loss.id, 10)), 1)
        restored = hippocampus.record(loss.id)
        self.assertGreater(restored.intensity, faded)
        self.assertAlmostEqual(restored.valence, -0.6)

    def testDepartureLearnsASignedDispositionFromTheStrongestFeeling(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("appraisal", appraised(0.3, 0.3), appraised(-0.8, 0.9))
        self.processor.prepare("dispositionLearning", {"learned": "when someone mocks what I love → I protect it"})
        self.say(conversation, "Tell me about your dog.")
        self.say(conversation, "What a stupid dog.")
        self.engine.leave(conversation)
        held = self.engine.repositories["dispositions"].strongestFirst(self.engine.being("Maya").id, 10)
        self.assertEqual(len(held), 1)
        self.assertAlmostEqual(held[0].weight, -0.8)

    def testDispositionsReachOnlyTheReplyCall(self):
        being = self.engine.being("Maya")
        self.engine.repositories["dispositions"].add(being.id, "when mocked → stay calm", -0.6, 0)
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Hello.")
        self.assertIn("when mocked → stay calm", self.processor.callsFor("reply")[-1]["user"])
        self.assertNotIn("when mocked", self.processor.callsFor("appraisal")[-1]["user"])

    def testAHeldThoughtStandsInTheLineByWhenItCameToMind(self):
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("introspection", {
            "thought": "I miss him.", "emo_summary": "sad", "conclusion": "loss stays", "valence": -0.4,
            "intensity": 0.6, "reinforces": -1, "action": {"type": "decision", "text": "I will keep his memory."}})
        self.say(conversation, "Hi.")
        self.engine.leave(conversation)
        self.test.time.advance(60)
        second, _ = self.engine.open("Maya", "Anna")
        self.say(second, "Hello.")
        user = self.processor.callsFor("reply")[-1]["user"]
        line = user.split("=== THIS CONVERSATION SO FAR ===")[1]
        self.assertNotIn("=== YOUR OWN THOUGHTS ===", user)
        self.assertLess(line.index("I decided: I will keep his memory."), line.index("Anna entered"))

    def testTheLastDaysStandBesideTheFocusAfterANight(self):
        self.processor.prepare("lastDays", "Daniel came and asked about my dog.")
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Did you ever have a pet?")
        self.assertNotIn("=== THE LAST DAYS", self.processor.callsFor("reply")[-1]["user"])
        self.engine.leave(conversation)
        call = self.processor.callsFor("lastDays")[-1]
        self.assertIn("Daniel entered", call["user"])
        self.assertIn("- Someone spoke and the being answered.", call["user"])
        self.assertNotIn("a mild warmth", call["user"])
        self.assertNotIn("this was kind", call["user"])
        self.test.time.advance(3600)
        second, _ = self.engine.open("Maya", "Ann")
        self.say(second, "Hello.")
        user = self.processor.callsFor("reply")[-1]["user"]
        self.assertIn("=== THE LAST DAYS (what you carry without attending to it) ===\n  earlier today: Daniel came and asked about my dog.", user)
        self.processor.prepare("lastDays", "Daniel came and asked about my dog; later Ann came.")
        self.engine.leave(second)
        self.test.time.advance(86400)
        self.engine.night("Maya")
        third, _ = self.engine.open("Maya", "Carol")
        self.say(third, "Hi.")
        user = self.processor.callsFor("reply")[-1]["user"]
        block = user.split("=== THE LAST DAYS")[1].split("=== THIS CONVERSATION SO FAR ===")[0]
        self.assertNotIn("earlier today", block)
        self.assertIn("  yesterday: Daniel came and asked about my dog; later Ann came.", block)
        self.assertLess(user.index("=== THE LAST DAYS"), user.index("=== THIS CONVERSATION SO FAR ==="))
        self.assertNotIn("THE LAST DAYS", self.processor.callsFor("appraisal")[-1]["user"])

    def testTheLastDaysSurviveTheNightAndAreFoldedOnTheSecond(self):
        for person in ("Daniel", "Ann"):
            conversation, _ = self.engine.open("Maya", person)
            self.say(conversation, "Hello.")
            self.engine.leave(conversation)
            self.test.time.advance(86400)
            self.engine.night("Maya")
        days = self.engine.repositories["lastDays"].get(self.engine.being("Maya").id)
        self.assertEqual(days.today, "")
        self.assertEqual(days.yesterday, "Someone came and we talked.")
        self.assertEqual(days.before, "Someone came and we talked.")
        self.assertEqual(len(self.processor.callsFor("lastDays")), 3)

    def testWithoutTheLastDaysNothingIsKeptOrShown(self):
        self.engine.parameters["lastDays"] = False
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.say(conversation, "Hello.")
        self.engine.leave(conversation)
        self.engine.night("Maya")
        self.assertEqual(self.processor.callsFor("lastDays"), [])
        self.assertTrue(self.engine.repositories["lastDays"].get(self.engine.being("Maya").id).isEmpty())

    def testAThoughtGoesToTheSlotAndTheReplySeesIt(self):
        self.engine.parameters["heldThoughtsInLine"] = False
        conversation, _ = self.engine.open("Maya", "Daniel")
        self.processor.prepare("introspection", {
            "thought": "I miss him.", "emo_summary": "sad", "conclusion": "loss stays", "valence": -0.4,
            "intensity": 0.6, "reinforces": -1, "action": {"type": "decision", "text": "I will keep his memory."}})
        self.say(conversation, "Hi.")
        self.engine.leave(conversation)
        second, _ = self.engine.open("Maya", "Anna")
        self.say(second, "Hello.")
        user = self.processor.callsFor("reply")[-1]["user"]
        self.assertIn("=== YOUR OWN THOUGHTS ===", user)
        self.assertIn("I decided: I will keep his memory.", user)
        self.assertNotIn("I decided", user.split("=== YOUR OWN THOUGHTS ===")[0])



class testThinkingMidTurn(unittest.TestCase):

    def testTheChainStartsFromTheMomentAndMemoryWithOnlyThoughtsCanBeSearched(self):
        test = testEngine()
        conversation, _ = test.engine.open("Maya", "Tom")
        test.processor.prepare("reply", reply(-0.3, 0.5, words="I am not sure.", action="introspect", text="whether I think"))
        test.processor.prepare("introspection", {
            "thought": "Maybe I do.", "emo_summary": "calm", "conclusion": "c", "valence": 0.1, "intensity": 0.4,
            "reinforces": -1, "action": {"type": "keep_thinking", "text": "why it matters"}})
        test.time.advance(30)
        test.engine.hear(conversation, "You don't think.")
        first, second = [call["user"] for call in test.processor.callsFor("introspection")][:2]
        self.assertIn("Tom said: You don't think.", first)
        self.assertIn("Maya replied: I am not sure.", first)
        self.assertIn('"whether I think"', first)
        self.assertIn("Maybe I do.", second)
        self.assertIn("You chose to keep thinking.\n", second)


class namedModel:
    def __init__(self, name):
        self.name = name

    def _send(self, system, messages, temperature, responseFormat):
        return self.name


class testRouting(unittest.TestCase):

    def testEachPurposeGoesToItsModel(self):
        from emostack.core.routedProcessor import routedProcessor
        calls = []
        routed = routedProcessor(namedModel("default"), {"appraisal": namedModel("appraiser")})
        routed.addRecorder(calls.append)
        self.assertEqual(routed.chat("s", "u", 0.1, purpose="appraisal"), "appraiser")
        self.assertEqual(routed.chat("s", "u", 0.1, purpose="reply"), "default")
        self.assertEqual([call["purpose"] for call in calls], ["appraisal", "reply"])


class testBeingCopies(unittest.TestCase):

    def testACopyCarriesItsHistoryAndTheSourceStays(self):
        source = testEngine()
        conversation, _ = source.engine.open("Maya", "Daniel")
        source.time.advance(30)
        source.engine.hear(conversation, "Hello.")
        source.engine.leave(conversation)
        path = source.engine.database.path
        target = testEngine()
        copy = target.engine.copyBeing(path, source.engine.being("Maya").id, "Maya")
        copied = target.engine.assemblyFor(copy).hippocampus.all()
        self.assertEqual(len(copied), len(source.engine.assemblyFor(source.engine.being("Maya")).hippocampus.all()))
        target.engine.deleteBeing(copy.id)
        self.assertEqual(target.engine.assemblyFor(copy).hippocampus.all(), [])
