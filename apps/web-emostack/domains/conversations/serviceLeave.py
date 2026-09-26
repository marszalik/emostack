import threading

from domains.conversations.repositoryTranscripts import repositoryTranscripts


class serviceLeave:
    """The person leaves. The being has its quiet and may learn a disposition; this runs in the
    background, and the conversation is closed."""

    def __init__(self, application):
        self.application = application

    def leave(self, live):
        if live.closed:
            return
        live.closed = True
        self.application.conversations.pop(live.id, None)
        threading.Thread(target=self._leave, args=(live,), daemon=True).start()

    @staticmethod
    def _leave(live):
        try:
            with live.lock:
                if live.conversation is not None:
                    outcome = live.engine.leave(live.conversation)
                    transcripts = repositoryTranscripts(live.engine.database)
                    transcripts.add(live.beingId, live.id, live.person, "departure", live.person)
                    for construct in outcome.thoughts:
                        transcripts.add(live.beingId, live.id, live.person, "thought", construct.statement())
        finally:
            live.engine.close()
