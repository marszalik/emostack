from emostack.action.DoNothing import DoNothing
from emostack.action.FormConstruct import FormConstruct
from emostack.action.KeepThinking import KeepThinking
from emostack.action.SearchMemory import SearchMemory
from emostack.action.Speak import Speak
from emostack.action.StaySilent import StaySilent
from emostack.action.Think import Think


class actionFactory:
    """The answer of the LLM model → the act it names."""

    def fromReply(self, answer, words):
        """A reply call: search memory, stop to think, or else speak `words` (silence when the being
        chose not to answer or has nothing to say)."""
        chosen = answer.get("action") or {}
        name = chosen.get("type") if isinstance(chosen, dict) else None
        text = str(chosen.get("text", "") or "").strip() if isinstance(chosen, dict) else ""
        if name in SearchMemory.replyNames:
            return SearchMemory(text)
        if name in Think.replyNames:
            return Think(text)
        if words:
            return Speak(words)
        return StaySilent()

    def fromReflection(self, answer):
        """A reflection step: keep thinking, search memory, form a construct, or nothing. An act
        that needs a text and has none is nothing."""
        chosen = answer.get("action") or {}
        if not isinstance(chosen, dict):
            return DoNothing()
        name = chosen.get("type")
        text = str(chosen.get("text", "") or "").strip()
        if name in KeepThinking.reflectionNames:
            return KeepThinking(text)
        if name in SearchMemory.reflectionNames and text:
            return SearchMemory(text)
        if name in FormConstruct.reflectionNames and text:
            return FormConstruct(name, text)
        return DoNothing()
