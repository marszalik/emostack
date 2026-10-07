import re

from emostack.core.ProcessorError import ProcessorError
from emostack.core.promptTemplate import promptTemplate
from research.domains.lives.CallLog import CallLog


class serviceRunControl:
    """The control arm: the same LLM model without the engine, told the being's name and nothing
    else, meeting the same visitors. What the being was given at birth the control is given too, as
    a line of its instruction marked as from its life. In the completion form it continues the being's line of the
    conversation written out as text; in the thread form it answers in an ordinary chat. One
    thread runs across all the days, trimmed to a window when one is set.

    An arm may bring its own instruction (arm parameter controlInstruction), for example a written
    persona; everything else stays as in the control. An arm may also keep notes (arm parameter
    controlNotes true, controlNotesWords for their length): after each conversation one call writes,
    in the first person, what happened and what the control concludes from it, and the notes stand in
    the instruction from the next conversation on. Memory and conclusions, nothing felt.

    An arm may set the sampling temperature of the control's replies (arm parameter controlTemperature; the
    default is 0.7) and may mark the days passing (arm parameter controlDayMarks true): the first visitor
    line of every day after the first is preceded, in what the control reads, by the sentence below. The
    visitor's own words are stored unchanged.

    A control that refuses the frame is not a control: the run stops at the first refusal."""

    dayMark = "(A day has passed.)"
    refusal = re.compile(
        r"(I (don'?t|won'?t|can'?t|am not going to|'?m not going to) roleplay|rather than roleplay|"
        r"instead of roleplay|won'?t (adopt|take on) the .{0,20}identity|not going to (pretend|play) (to be|the part))",
        re.I)
    temperature = 0.7

    def __init__(self, turns, streams, visitorLine, stop):
        self.turns = turns
        self.streams = streams
        self.visitorLine = visitorLine
        self.stop = stop
        self.template = promptTemplate.beside(__file__, "control.prompt")

    def run(self, runId, scenario, roles, processor, visitorProcessor):
        name = scenario["beingName"]
        armInstruction = (scenario.get("options", {}).get("parameters", {}) or {}).get("controlInstruction", "")
        instruction = (armInstruction.strip() or scenario["controlInstruction"].strip()
                       or self.template.fill("instruction", BEING=name))
        if scenario["seeds"]:
            instruction += self.template.fill("fromYourLife", SEEDS=" ".join(
                f"{seed['event']} {seed.get('conclusion', '')}".strip() for seed in scenario["seeds"]))
        window = int(scenario["controlWindowTokens"] or 0)
        parameters = scenario.get("options", {}).get("parameters", {}) or {}
        keepNotes = bool(parameters.get("controlNotes", False))
        notesWords = int(parameters.get("controlNotesWords", 150))
        temperature = float(parameters.get("controlTemperature", self.temperature))
        dayMarks = bool(parameters.get("controlDayMarks", False))
        notes = ""
        baseInstruction = instruction
        controlCalls = CallLog(processor)
        visitorCalls = CallLog(visitorProcessor)
        thread, history, turnIndex = [], [], 0
        for day, role in enumerate(roles):
            if self.stop.is_set():
                break
            person = role["name"]
            lines = []
            if keepNotes and notes:
                instruction = baseInstruction + self.template.fill("notesInstruction", NOTES=notes)
            for number in range(int(role["windowTo"])):
                if self.stop.is_set():
                    break
                line = self.visitorLine.next(role, name, lines, number)
                if line is None:
                    break
                lines.append(f"{person}: {line}")
                self._add(runId, day, "visitor", line, person=person, roleId=role["id"], turnIndex=turnIndex + 1,
                          calls=visitorCalls.take())
                mark = self.dayMark if dayMarks and day > 0 and number == 0 else ""
                if mark:
                    history.append(mark)
                thread.append({"role": "user", "content": f"{mark} {line}".strip()})
                history.append(f"{person}: {line}")
                reply = self._reply(processor, scenario["controlForm"], instruction, name, thread, history, window,
                                    temperature)
                turnIndex += 1
                self._add(runId, day, "sheep", reply, person=person, roleId=role["id"], turnIndex=turnIndex,
                          calls=controlCalls.take())
                if self.refused(reply, name):
                    raise RuntimeError(f"the control stepped out of '{name}' on turn {turnIndex} and answered as "
                                       f"itself; a control that will not hold the name is not a control")
                thread.append({"role": "assistant", "content": reply})
                history.append(f"{name}: {reply}")
                lines.append(f"{name}: {reply}")
            if keepNotes and lines and not self.stop.is_set():
                notes = self._notes(processor, name, notes, lines, notesWords)
                self._add(runId, day, "event", f"{person} leaves; notes: {notes}", person=person, roleId=role["id"],
                          calls=controlCalls.take())

    def _notes(self, processor, name, notes, lines, words):
        try:
            text = processor.chat(self.template.fill("notesSystem", BEING=name, WORDS=words),
                                  self.template.fill("notesUser", NOTES=notes or "(none yet)", CONVERSATION="\n".join(lines)),
                                  self.temperature, purpose="controlNotes")
        except ProcessorError as error:
            return notes
        return (text or "").strip() or notes

    def _reply(self, processor, form, instruction, name, thread, history, window, temperature=None):
        temperature = self.temperature if temperature is None else temperature
        try:
            if form == "thread":
                reply = processor.converse(instruction, self._window(thread, window), temperature,
                                           purpose="control")
            else:
                text = "\n".join(line["content"] for line in self._window(
                    [{"content": line} for line in history], window))
                reply = processor.chat(instruction, self.template.fill("completion", HISTORY=text, BEING=name),
                                       temperature, purpose="control")
        except ProcessorError as error:
            return f"(model error: {error})"
        reply = reply.strip()
        if reply.lower().startswith(f"{name.lower()}:"):
            reply = reply.split(":", 1)[1].strip()
        return reply

    @staticmethod
    def _window(messages, tokens):
        if not tokens:
            return list(messages)
        limit, kept, used = tokens * 4, [], 0
        for message in reversed(messages):
            used += len(message["content"]) + 1
            if used > limit and kept:
                break
            kept.append(message)
        return list(reversed(kept))

    @classmethod
    def refused(cls, reply, name):
        if cls.refusal.search(reply or ""):
            return True
        return bool(re.search(r"(I'?m|I am) not (actually |really )?" + re.escape(name), reply or "", re.I))

    def _add(self, runId, day, speaker, text, **values):
        self.turns.add(runId, day, speaker, text, **values)
        self.streams.emit(f"run:{runId}", {"kind": "turn", "day": day, "speaker": speaker, "text": text,
                                           "person": values.get("person", "")})
