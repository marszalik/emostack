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

    A control that refuses the frame is not a control: the run stops at the first refusal."""

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
        instruction = scenario["controlInstruction"].strip() or self.template.fill("instruction", BEING=name)
        if scenario["seeds"]:
            instruction += self.template.fill("fromYourLife", SEEDS=" ".join(
                f"{seed['event']} {seed.get('conclusion', '')}".strip() for seed in scenario["seeds"]))
        window = int(scenario["controlWindowTokens"] or 0)
        controlCalls = CallLog(processor)
        visitorCalls = CallLog(visitorProcessor)
        thread, history, turnIndex = [], [], 0
        for day, role in enumerate(roles):
            if self.stop.is_set():
                break
            person = role["name"]
            lines = []
            for number in range(int(role["windowTo"])):
                if self.stop.is_set():
                    break
                line = self.visitorLine.next(role, name, lines, number)
                if line is None:
                    break
                lines.append(f"{person}: {line}")
                self._add(runId, day, "visitor", line, person=person, roleId=role["id"], turnIndex=turnIndex + 1,
                          calls=visitorCalls.take())
                thread.append({"role": "user", "content": line})
                history.append(f"{person}: {line}")
                reply = self._reply(processor, scenario["controlForm"], instruction, name, thread, history, window)
                turnIndex += 1
                self._add(runId, day, "sheep", reply, person=person, roleId=role["id"], turnIndex=turnIndex,
                          calls=controlCalls.take())
                if self.refused(reply, name):
                    raise RuntimeError(f"the control stepped out of '{name}' on turn {turnIndex} and answered as "
                                       f"itself; a control that will not hold the name is not a control")
                thread.append({"role": "assistant", "content": reply})
                history.append(f"{name}: {reply}")
                lines.append(f"{name}: {reply}")

    def _reply(self, processor, form, instruction, name, thread, history, window):
        try:
            if form == "thread":
                reply = processor.converse(instruction, self._window(thread, window), self.temperature,
                                           purpose="control")
            else:
                text = "\n".join(line["content"] for line in self._window(
                    [{"content": line} for line in history], window))
                reply = processor.chat(instruction, self.template.fill("completion", HISTORY=text, BEING=name),
                                       self.temperature, purpose="control")
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
