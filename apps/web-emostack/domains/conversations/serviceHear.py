import threading

from domains.conversations.repositoryTranscripts import repositoryTranscripts


class serviceHear:
    """The person says something. The being's turn takes seconds and runs in the background; its
    reply, and any thought it formed on the way, reach the page through the live stream."""

    def __init__(self, application):
        self.application = application

    def hearInBackground(self, live, words):
        if live.busy:
            raise ValueError("the being is still answering")
        if not words.strip():
            raise ValueError("say something")
        if len(words) > self.application.config.maxWords:
            raise ValueError("that is too long")
        live.busy = True
        live.add("person", words)
        threading.Thread(target=self._turn, args=(live, words), daemon=True).start()

    def _turn(self, live, words):
        key = f"conversation:{live.id}"
        transcripts = repositoryTranscripts(live.engine.database)
        transcripts.add(live.beingId, live.id, live.person, "person", words)
        try:
            with live.lock:
                outcome = live.engine.hear(live.conversation, words)
            for construct in outcome.thoughts:
                message = live.add("thought", construct.statement(), conclusion=construct.conclusion)
                transcripts.add(live.beingId, live.id, live.person, "thought", construct.statement())
                self.application.streams.emit(key, {"kind": "message", "message": message})
            moment = live.conversation.focus.entries[-1].record if not outcome.failed else None
            role = "failed" if outcome.failed else ("being" if outcome.words else "silence")
            message = live.add(role, outcome.words, calls=live.takeCalls(),
                               feeling=moment.feeling if moment else "",
                               valence=moment.valence if moment else None,
                               intensity=moment.intensity if moment else None)
            transcripts.add(live.beingId, live.id, live.person, role, outcome.words,
                            {"feeling": message["feeling"], "valence": message["valence"]})
            self.application.streams.emit(key, {"kind": "message", "message": message})
        except Exception as error:
            self.application.streams.emit(key, {"kind": "error", "text": str(error)[:300]})
        finally:
            live.busy = False
