import json
import re
import time

from emostack.core.ProcessorError import ProcessorError
from emostack.core.promptTemplate import promptTemplate


class processor:
    """The LLM model: it composes one answer from exactly the text it is given and holds nothing
    between calls. Every call is recorded in full: the prompt as sent and the answer as received.
    An implementation provides `_send`."""

    def __init__(self):
        self.recorders = []

    def addRecorder(self, recorder):
        """recorder(call) is called after every call with a dict: purpose, system, user,
        temperature, responseFormat, answer, at."""
        self.recorders.append(recorder)

    def removeRecorder(self, recorder):
        if recorder in self.recorders:
            self.recorders.remove(recorder)

    def chat(self, system, user, temperature, responseFormat=None, purpose=""):
        return self.converse(system, [{"role": "user", "content": user}], temperature, responseFormat, purpose)

    def converse(self, system, messages, temperature, responseFormat=None, purpose=""):
        """A call over a thread of messages as they happened: [{role: user|assistant, content}]."""
        answer = self._send(system, messages, temperature, responseFormat)
        call = {
            "purpose": purpose,
            "system": system,
            "user": "\n".join(message["content"] for message in messages) if len(messages) == 1
                    else "\n".join(f"[{message['role']}] {message['content']}" for message in messages),
            "temperature": temperature,
            "responseFormat": responseFormat,
            "answer": answer,
            "at": time.time(),
        }
        for recorder in list(self.recorders):
            recorder(call)
        return answer

    def chatJson(self, system, user, temperature, responseFormat=None, purpose="", retries=1):
        """chat + tolerant JSON parsing. A failed parse is asked again with a note that the answer
        was not valid JSON, up to `retries` more times; then ProcessorError."""
        retryNote = promptTemplate.beside(__file__, "processor.prompt").text("retryNote")
        lastError = None
        text = user
        for _ in range(retries + 1):
            answer = self.chat(system, text, temperature, responseFormat, purpose)
            try:
                return self.parseJson(answer)
            except (ValueError, ProcessorError) as error:
                lastError = error
                text = user + retryNote
        raise ProcessorError(f"JSON parse failed after {retries + 1} attempt(s): {lastError}")

    @staticmethod
    def parseJson(text):
        """Strips markdown fences, repairs a leading '+' on numbers, falls back to the first
        {...} block."""
        if text is None:
            raise ProcessorError("the LLM model returned no text")
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        cleaned = re.sub(r'([:\[,]\s*)\+(?=[0-9.])', r'\1', cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end > start:
                return json.loads(cleaned[start:end + 1])
            raise

    def _send(self, system, messages, temperature, responseFormat):
        raise NotImplementedError
