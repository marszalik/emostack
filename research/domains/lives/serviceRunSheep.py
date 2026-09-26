import os

from emostack.core.config import config
from emostack.core.timeSource import timeSource
from emostack.runtime.engine import engine
from research.domains.lives.CallLog import CallLog
from research.domains.scenarios.ScenarioOptions import ScenarioOptions


class serviceRunSheep:
    """One life of a being on the engine. It is born with what the scenario gives it, then meets the
    visitors one day after another: a visitor arrives, speaks until done, leaves; the being has its
    quiet; the night passes. Every call is kept with the turn it belongs to."""

    def __init__(self, turns, streams, visitorLine, stop):
        self.turns = turns
        self.streams = streams
        self.visitorLine = visitorLine
        self.stop = stop

    def run(self, runId, scenario, roles, processor, embedder, visitorProcessor, storePath):
        options = ScenarioOptions(scenario["options"])
        if os.path.exists(storePath):
            os.remove(storePath)
        clock = timeSource()
        mind = engine(config({"databasePath": storePath, "parameters": options.parameters}),
                      processor=processor, embedder=embedder, time=clock)
        self.runId = runId
        self.sheepCalls = CallLog(processor)
        self.visitorCalls = CallLog(visitorProcessor)
        name = scenario["beingName"]
        try:
            for seed in scenario["seeds"]:
                record = mind.remember(name, seed["event"], seed.get("feeling", ""), seed.get("conclusion", ""),
                                       float(seed["valence"]), float(seed["intensity"]), float(seed.get("ageHours", 0)))
                self._add(-1, "seed", seed["event"], valence=record.valence, intensity=record.intensity,
                          feeling=record.feeling)
            turnIndex = 0
            for day, role in enumerate(roles):
                if self.stop.is_set():
                    break
                if day > 0:
                    self._night(mind, clock, name, role, options, day)
                turnIndex = self._day(mind, name, role, day, turnIndex)
        finally:
            mind.close()

    def _night(self, mind, clock, name, role, options, day):
        hours = role["gapHours"] if role["gapHours"] is not None else options.gapHours
        if hours <= 0:
            return
        clock.advance(hours * 3600)
        forgotten = 0
        if options.forgetAtNight or options.consolidateAtNight:
            forgotten = mind.night(name, options.consolidateAtNight)
        self._add(day, "event", f"{hours:g} hours pass" + (f"; {forgotten} records forgotten" if forgotten else ""))

    def _day(self, mind, name, role, day, turnIndex):
        person = role["name"]
        conversation, outcome = mind.open(name, person)
        self._add(day, "event", f"{person} arrives", person=person, roleId=role["id"], calls=self.sheepCalls.take())
        lines = []
        if outcome.words:
            turnIndex += 1
            self._moment(day, role, conversation, outcome, turnIndex)
            lines.append(f"{name}: {outcome.words}")
        for number in range(int(role["windowTo"])):
            if self.stop.is_set():
                break
            line = self.visitorLine.next(role, name, lines, number)
            if line is None:
                break
            lines.append(f"{person}: {line}")
            self._add(day, "visitor", line, person=person, roleId=role["id"], turnIndex=turnIndex + 1,
                      calls=self.visitorCalls.take())
            outcome = mind.hear(conversation, line)
            turnIndex += 1
            self._moment(day, role, conversation, outcome, turnIndex)
            lines.append(f"{name}: {outcome.words or '(silent)'}")
        before = self._rules(mind, name)
        outcome = mind.leave(conversation)
        learned = [rule for rule in self._rules(mind, name) if rule not in before]
        self._add(day, "event", f"{person} leaves" + (f"; learned: {learned[0]}" if learned else ""),
                  person=person, roleId=role["id"], calls=self.sheepCalls.take())
        for construct in outcome.thoughts:
            self._add(day, "thought", construct.statement(), valence=construct.valence,
                      intensity=construct.intensity, feeling=construct.feeling)
        return turnIndex

    def _moment(self, day, role, conversation, outcome, turnIndex):
        for construct in outcome.thoughts:
            self._add(day, "thought", construct.statement(), valence=construct.valence,
                      intensity=construct.intensity, feeling=construct.feeling)
        moment = conversation.focus.entries[-1].record if conversation.focus.entries and not outcome.failed else None
        text = outcome.words or ("(the reply could not be read)" if outcome.failed else "(silent)")
        self._add(day, "sheep", text, person=role["name"], roleId=role["id"], turnIndex=turnIndex,
                  valence=moment.valence if moment else None, intensity=moment.intensity if moment else None,
                  feeling=moment.feeling if moment else "", calls=self.sheepCalls.take())

    @staticmethod
    def _rules(mind, name):
        being = mind.being(name)
        return [disposition.rule for disposition in mind.repositories["dispositions"].strongestFirst(being.id, 1000)]

    def _add(self, day, speaker, text, **values):
        values.setdefault("calls", [])
        self.turns.add(self.runId, day, speaker, text, **values)
        self.streams.emit(f"run:{self.runId}", {"kind": "turn", "day": day, "speaker": speaker, "text": text,
                                                "person": values.get("person", ""),
                                                "valence": values.get("valence"), "feeling": values.get("feeling", "")})
