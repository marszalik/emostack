import json
import os
import re
import sys
import threading
import time
from types import SimpleNamespace

from emostack.core.config import config
from emostack.core.localEmbedder import localEmbedder
from emostack.core.openAiCompatibleProcessor import openAiCompatibleProcessor
from emostack.runtime.engine import engine
from domains.beings.serviceListBeings import serviceListBeings
from domains.conversations.LiveConversation import LiveConversation
from domains.conversations.repositoryTranscripts import repositoryTranscripts
from domains.conversations.serviceConversationState import serviceConversationState
from domains.conversations.serviceLeave import serviceLeave
from domains.public.repositoryVisitors import repositoryVisitors
from domains.public.serviceAwake import serviceAwake


class serviceRoom:
    """The public room: one being everyone talks to, on the house LLM model. One visitor speaks at a
    time, the others wait in a queue and watch; a visit is a few messages long and ends with silence
    or when the tab is gone. The being sleeps at night and whenever its computer is off; asleep, it
    takes letters and answers them when it wakes, one by one, as short visits. Everything said here
    becomes part of the being's memory and is shown to everyone."""

    KEY = "public"
    namePattern = re.compile(r"^[A-Za-zŁÓŚĄĘĆŻŹŃłóśąęćżźń0-9 _-]{1,24}$")

    def __init__(self, application):
        self.application = application
        self.settings = application.config.publicSheep
        self.folder = os.path.join(application.config.dataFolder, "public")
        os.makedirs(self.folder, exist_ok=True)
        self.store = os.path.join(self.folder, "emostack.db")
        self.name = self.settings.get("name") or "Maya"
        self.awake = serviceAwake(self.settings, self.folder)
        self.visitors = repositoryVisitors(application.database)
        self.lock = threading.RLock()
        self.live = None
        self.speaker = None
        self.queue = []
        self.delivering = False
        self.wasAwake = None
        threading.Thread(target=self._janitor, daemon=True).start()

    # --- settings -------------------------------------------------------------------------------
    def setting(self, name, default):
        return self.settings.get(name, default)

    def engine(self):
        embedder = self.settings.get("embedder") or self.application.config.serverEmbedder
        return engine(config({"databasePath": self.store}), processor=openAiCompatibleProcessor(self.settings["processor"]),
                      embedder=localEmbedder(embedder))

    def reader(self):
        return engine(config({"databasePath": self.store}))

    # --- what the page shows ----------------------------------------------------------------------
    def status(self, visitor, address):
        status = self.awake.status()
        with self.lock:
            speaker = dict(self.speaker) if self.speaker else None
            position = next((i + 1 for i, entry in enumerate(self.queue) if entry["visitor"] == visitor), None)
            busy = bool(self.live and self.live.busy)
            waiting = len(self.queue)
        mine = speaker is not None and speaker["visitor"] == visitor
        turnsPerVisit = int(self.setting("turnsPerVisit", 8))
        day = self.awake.day()
        return {
            "being": self.name, "awake": status["awake"], "reason": status["reason"], "until": status["until"],
            "speaker": speaker["name"] if speaker else None,
            "mail": bool(speaker and speaker.get("mail")),
            "me": "speaker" if mine else ("queue" if position else None),
            "position": position, "waiting": waiting, "busy": busy,
            "turnsLeft": max(0, turnsPerVisit - speaker["turns"]) if mine else None,
            "turnsPerVisit": turnsPerVisit,
            "visitsLeft": max(0, int(self.setting("visitsPerDay", 2)) - self.visitors.visitsToday(visitor, address, day)),
            "idleSeconds": int(self.setting("idleSeconds", 180)),
            "maxWords": int(self.setting("maxWords", 600)),
            "letters": self.visitors.mailOf(visitor),
            "lettersLeft": max(0, int(self.setting("mailPerNight", 1))
                               - self.visitors.mailTonight(visitor, address, self.awake.nightId())),
        }

    def seen(self, visitor):
        now = time.time()
        with self.lock:
            if self.speaker and self.speaker["visitor"] == visitor:
                self.speaker["lastSeen"] = now
            for entry in self.queue:
                if entry["visitor"] == visitor:
                    entry["lastSeen"] = now

    def log(self, limit=80):
        reader = self.reader()
        try:
            being = reader.beings.named(self.name)
            if being is None:
                return []
            repositoryTranscripts(reader.database)
            rows = reader.database.read(
                "SELECT person, role, text, details, at FROM transcripts WHERE beingId = ? ORDER BY id DESC LIMIT ?",
                (being.id, limit))
        finally:
            reader.close()
        return [dict(role=row["role"], text=row["text"], who=row["person"], at=row["at"],
                     **{k: v for k, v in json.loads(row["details"] or "{}").items() if k in ("feeling", "valence")})
                for row in reversed(rows)]

    def about(self):
        reader = self.reader()
        try:
            found = [being for being in serviceListBeings(reader).list() if being["name"] == self.name]
        finally:
            reader.close()
        return found[0] if found else {"name": self.name, "awake": False, "records": 0, "mood": None, "talking": []}

    def inner(self):
        with self.lock:
            live = self.live
        if live is not None and live.conversation is not None:
            try:
                return serviceConversationState().state(live)
            except Exception:
                return None
        reader = self.reader()
        try:
            being = reader.beings.named(self.name)
            if being is None:
                return None
            quiet = SimpleNamespace(engine=reader, beingId=being.id, conversation=None, person="")
            return serviceConversationState().state(quiet)
        finally:
            reader.close()

    # --- taking a seat ----------------------------------------------------------------------------
    def join(self, visitor, address, name):
        name = (name or "").strip()
        if not self.namePattern.match(name):
            raise ValueError("a name: letters, digits, spaces, up to 24 characters")
        if not self.awake.status()["awake"]:
            raise PermissionError(f"{self.name} is asleep")
        if self.visitors.visitsToday(visitor, address, self.awake.day()) >= int(self.setting("visitsPerDay", 2)):
            raise PermissionError("that is all for today; come back tomorrow")
        now = time.time()
        with self.lock:
            if self.speaker and self.speaker["visitor"] == visitor:
                return {"me": "speaker"}
            for i, entry in enumerate(self.queue):
                if entry["visitor"] == visitor:
                    entry["name"], entry["lastSeen"] = name, now
                    return {"me": "queue", "position": i + 1}
            entry = {"visitor": visitor, "address": address, "name": name, "joinedAt": now, "lastSeen": now}
            if self.speaker is None and not self.queue:
                self._seat(entry)
                return {"me": "speaker"}
            self.queue.append(entry)
            return {"me": "queue", "position": len(self.queue)}

    def say(self, visitor, words):
        words = (words or "").strip()
        with self.lock:
            if not self.speaker or self.speaker["visitor"] != visitor:
                raise PermissionError("it is not your turn")
            live = self.live
            if live.conversation is None:
                raise ValueError(f"wait for {self.name} to notice you")
            if live.busy:
                raise ValueError(f"{self.name} is still answering")
            if self.speaker["turns"] >= int(self.setting("turnsPerVisit", 8)):
                raise PermissionError("your visit is over")
            if not words:
                raise ValueError("say something")
            if len(words) > int(self.setting("maxWords", 600)):
                raise ValueError("that is too long")
            self.speaker["turns"] += 1
            self.speaker["lastSaid"] = self.speaker["lastSeen"] = time.time()
            last = self.speaker["turns"] >= int(self.setting("turnsPerVisit", 8))
            live.busy = True
            message = live.add("person", words, who=live.person)
        self._emit({"kind": "message", "message": self._shown(message)})
        threading.Thread(target=self._turn, args=(live, words, last), daemon=True).start()

    def leave(self, visitor, force=False):
        with self.lock:
            if self.speaker and (force or self.speaker["visitor"] == visitor):
                self._unseat()
            elif force:
                self.queue.clear()
            else:
                self.queue = [entry for entry in self.queue if entry["visitor"] != visitor]
            self._seatNext()

    def mail(self, visitor, address, name, words):
        name, words = (name or "").strip(), (words or "").strip()
        if not self.namePattern.match(name):
            raise ValueError("a name: letters, digits, spaces, up to 24 characters")
        if not words:
            raise ValueError("write something")
        if len(words) > 400:
            raise ValueError("a letter is up to 400 characters")
        if self.awake.status()["awake"]:
            raise PermissionError(f"{self.name} is awake; come in instead")
        night = self.awake.nightId()
        if self.visitors.mailTonight(visitor, address, night) >= int(self.setting("mailPerNight", 1)):
            raise PermissionError("one letter a night")
        self.visitors.leaveMail(visitor, address, name, words, night)

    def report(self, visitor, address, about, note):
        self.visitors.report(visitor, address, about or "", note or "")

    def rest(self, on):
        self.awake.rest(on)
        if on:
            self.leave(None, force=True)
        self.awake.modelAnswers(force=True)
        self._emit({"kind": "room"})

    # --- inside -------------------------------------------------------------------------------------
    def _seat(self, entry, mail=None):
        """Under the lock: the next visitor sits down; the being notices them in the background."""
        mind = self.engine()
        being = mind.being(self.name)
        live = LiveConversation(f"public:{entry['visitor']}", 2, being.id, being.name, entry["name"], mind)
        now = time.time()
        self.live = live
        self.speaker = dict(entry, seatedAt=now, lastSeen=now, lastSaid=now, turns=0, mail=mail is not None)
        if mail is None:
            self.visitors.visited(entry["visitor"], entry["address"], entry["name"], self.awake.day())
        self._emit({"kind": "room"})
        threading.Thread(target=self._greet, args=(live,), daemon=True).start()
        return live

    def _greet(self, live):
        try:
            with live.lock:
                if live.closed:
                    return
                live.conversation, outcome = live.engine.open(live.beingName, live.person)
            transcripts = repositoryTranscripts(live.engine.database)
            transcripts.add(live.beingId, live.id, live.person, "arrival", live.person)
            message = live.add("being" if outcome.words else "silence", outcome.words, who=live.beingName)
            transcripts.add(live.beingId, live.id, live.person, message["role"], outcome.words)
            self._emit({"kind": "message", "message": self._shown(message)})
        except Exception as error:
            print(f"public room, greeting: {error}", file=sys.stderr)
            self._emit({"kind": "error", "text": f"{self.name} could not answer; its computer may be off"})
            self.awake.modelAnswers(force=True)
            with self.lock:
                if self.live is live:
                    self._unseat()
                    self._seatNext()

    def _turn(self, live, words, last):
        try:
            self._hear(live, words)
        finally:
            live.busy = False
            if last:
                with self.lock:
                    if self.live is live:
                        self._unseat()
                        self._seatNext()

    def _hear(self, live, words):
        """One turn of the being, recorded and shown to the room. Returns what it said."""
        transcripts = repositoryTranscripts(live.engine.database)
        transcripts.add(live.beingId, live.id, live.person, "person", words)
        try:
            with live.lock:
                outcome = live.engine.hear(live.conversation, words)
            for construct in outcome.thoughts:
                message = live.add("thought", construct.statement(), conclusion=construct.conclusion, who=live.beingName)
                transcripts.add(live.beingId, live.id, live.person, "thought", construct.statement())
                self._emit({"kind": "message", "message": self._shown(message)})
            moment = live.conversation.focus.entries[-1].record if not outcome.failed else None
            role = "failed" if outcome.failed else ("being" if outcome.words else "silence")
            message = live.add(role, outcome.words, who=live.beingName, feeling=moment.feeling if moment else "",
                               valence=moment.valence if moment else None)
            transcripts.add(live.beingId, live.id, live.person, role, outcome.words,
                            {"feeling": message["feeling"], "valence": message["valence"]})
            self._emit({"kind": "message", "message": self._shown(message)})
            return outcome.words
        except Exception as error:
            print(f"public room, turn: {error}", file=sys.stderr)
            self._emit({"kind": "error", "text": f"{self.name} could not answer this time"})
            self.awake.modelAnswers(force=True)
            return None

    def _unseat(self):
        """Under the lock: the speaker leaves; the being has its quiet in the background."""
        live, self.live, self.speaker = self.live, None, None
        if live is not None:
            serviceLeave(self.application).leave(live)
        self._emit({"kind": "room"})

    def _seatNext(self):
        """Under the lock."""
        if self.speaker is None and self.queue and self.awake.status()["awake"]:
            self._seat(self.queue.pop(0))

    def _janitor(self):
        while True:
            time.sleep(5)
            try:
                self._sweep()
            except Exception as error:
                print(f"public room, sweep: {error}", file=sys.stderr)

    def _sweep(self):
        now = time.time()
        status = self.awake.status()
        with self.lock:
            self.queue = [entry for entry in self.queue if now - entry["lastSeen"] < 40]
            if self.speaker is not None and not self.speaker.get("mail"):
                gone = now - self.speaker["lastSeen"] > 40
                idle = now - self.speaker["lastSaid"] > int(self.setting("idleSeconds", 180)) and not (self.live and self.live.busy)
                if gone or idle or not status["awake"]:
                    self._unseat()
            if not status["awake"]:
                self.queue.clear()
            self._seatNext()
        if self.wasAwake and not status["awake"] and status["reason"] in ("night", "rest"):
            self._nightFalls()
        if status["awake"]:
            self._deliverMail()
        self.wasAwake = status["awake"]

    def _nightFalls(self):
        """The being is put to sleep now, so that the clock folds its day and forgets what is weak."""
        reader = self.reader()
        try:
            being = reader.beings.named(self.name)
            if being is not None and being.isAwake():
                being.fallAsleep(reader.time.now())
                reader.beings.saveWakefulness(being)
        finally:
            reader.close()

    def _deliverMail(self):
        with self.lock:
            if self.delivering or self.speaker is not None:
                return
            letters = self.visitors.undelivered()
            if not letters:
                return
            self.delivering = True
        threading.Thread(target=self._deliver, args=(letters,), daemon=True).start()

    def _deliver(self, letters):
        """Each letter is a short visit: the writer arrives, says their words, and leaves; the answer
        waits for them on the page."""
        try:
            for letter in letters:
                with self.lock:
                    if self.speaker is not None or not self.awake.status()["awake"]:
                        return
                    live = self._seat({"visitor": f"mail:{letter['id']}", "address": letter["address"],
                                       "name": letter["name"], "joinedAt": time.time(), "lastSeen": time.time()}, mail=letter)
                for _ in range(120):
                    time.sleep(1)
                    if live.conversation is not None or live.closed:
                        break
                if live.conversation is None:
                    return
                with self.lock:
                    live.busy = True
                    message = live.add("person", letter["words"], who=letter["name"], letter=True)
                self._emit({"kind": "message", "message": self._shown(message)})
                try:
                    reply = self._hear(live, letter["words"])
                finally:
                    live.busy = False
                self.visitors.deliver(letter["id"], reply if reply is not None else "")
                with self.lock:
                    if self.live is live:
                        self._unseat()
                time.sleep(3)
        finally:
            self.delivering = False
            with self.lock:
                self._seatNext()

    def _shown(self, message):
        return {k: v for k, v in message.items() if k != "calls"}

    def _emit(self, event):
        self.application.streams.emit(self.KEY, event)
