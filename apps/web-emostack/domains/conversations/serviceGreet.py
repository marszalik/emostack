from domains.conversations.repositoryTranscripts import repositoryTranscripts


class serviceGreet:
    """The person arrives: the being learns who is here and may greet. Runs once per conversation."""

    def __init__(self, application):
        self.application = application

    def greet(self, live):
        with live.lock:
            if live.conversation is not None:
                return None
            live.conversation, outcome = live.engine.open(live.beingName, live.person)
        transcripts = repositoryTranscripts(live.engine.database)
        transcripts.add(live.beingId, live.id, live.person, "arrival", live.person)
        message = live.add("being" if outcome.words else "silence", outcome.words, calls=live.takeCalls())
        transcripts.add(live.beingId, live.id, live.person, message["role"], outcome.words)
        return message
