from domains.conversations.repositoryTranscripts import repositoryTranscripts


class serviceThink:
    """The being stops to think now, with nobody asking."""

    def think(self, live):
        with live.lock:
            thoughts = live.engine.think(live.conversation)
        transcripts = repositoryTranscripts(live.engine.database)
        messages = []
        calls = live.takeCalls()
        for construct in thoughts:
            messages.append(live.add("thought", construct.statement(), conclusion=construct.conclusion, calls=calls))
            transcripts.add(live.beingId, live.id, live.person, "thought", construct.statement())
            calls = []
        return messages
