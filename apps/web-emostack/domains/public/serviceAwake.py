import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class serviceAwake:
    """Whether the public being is up. It sleeps at night, it sleeps when an administrator has put
    it to rest, and it is shown asleep when the house LLM model does not answer, because its computer
    is off or busy. The model is probed with a one-token call, and the answer is kept for a while."""

    def __init__(self, settings, folder):
        self.settings = settings
        self.folder = folder
        self.zone = ZoneInfo(settings.get("timezone") or "Europe/Warsaw")
        self.night = settings.get("night") or ["22:00", "08:00"]
        self.lock = threading.Lock()
        self.reachable = False
        self.checkedAt = 0.0

    def now(self):
        return datetime.now(self.zone)

    def day(self):
        return self.now().strftime("%Y-%m-%d")

    def nightId(self):
        """The night a letter belongs to, named by the morning it is read on."""
        at = self.now()
        start = self._minutes(self.night[0])
        if at.hour * 60 + at.minute >= start:
            at = at + timedelta(days=1)
        return at.strftime("%Y-%m-%d")

    def isNight(self):
        at = self.now()
        minute = at.hour * 60 + at.minute
        start, end = self._minutes(self.night[0]), self._minutes(self.night[1])
        return (minute >= start or minute < end) if start > end else (start <= minute < end)

    def isResting(self):
        return os.path.exists(os.path.join(self.folder, "asleep"))

    def rest(self, on):
        flag = os.path.join(self.folder, "asleep")
        if on:
            open(flag, "w").close()
        elif os.path.exists(flag):
            os.remove(flag)

    def modelAnswers(self, force=False):
        with self.lock:
            keep = 45 if self.reachable else 20
            if not force and time.time() - self.checkedAt < keep:
                return self.reachable
        answers = self._probe()
        with self.lock:
            self.reachable, self.checkedAt = answers, time.time()
        return answers

    def status(self):
        if self.isResting():
            return {"awake": False, "reason": "rest", "until": None}
        if self.isNight():
            return {"awake": False, "reason": "night", "until": self.night[1]}
        if not self.modelAnswers():
            return {"awake": False, "reason": "away", "until": None}
        return {"awake": True, "reason": None, "until": None}

    def _probe(self):
        processor = self.settings.get("processor") or {}
        if not processor.get("baseUrl"):
            return False
        body = json.dumps({"model": processor.get("model", ""), "max_tokens": 1,
                           "messages": [{"role": "user", "content": "hi"}]}).encode("utf-8")
        request = urllib.request.Request(
            processor["baseUrl"].rstrip("/") + "/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {processor.get('apiKey', '')}"})
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                return response.status == 200
        except Exception:
            return False

    @staticmethod
    def _minutes(clock):
        hours, minutes = clock.split(":")
        return int(hours) * 60 + int(minutes)
