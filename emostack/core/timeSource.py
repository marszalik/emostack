import time

from emostack.core.promptTemplate import promptTemplate


class timeSource:
    """Now, and the words for when. A scenario moves the clock forward instead of moving the
    memories back; a test fixes it."""

    def __init__(self, fixed=None):
        self._fixed = fixed
        self._offset = 0.0
        self._words = promptTemplate.beside(__file__, "time.prompt")

    def now(self):
        base = self._fixed if self._fixed is not None else time.time()
        return base + self._offset

    def advance(self, seconds):
        self._offset += float(seconds)

    def fix(self, timestamp):
        self._fixed = float(timestamp)
        self._offset = 0.0

    def formatAbsolute(self, timestamp):
        local = time.localtime(timestamp)
        return self._words.fill(
            "absolute",
            WEEKDAY=self._words.text("weekdays").split("|")[local.tm_wday],
            DAY=local.tm_mday,
            MONTH=self._words.text("months").split("|")[local.tm_mon - 1],
            YEAR=local.tm_year,
            HOUR=f"{local.tm_hour:02d}", MINUTE=f"{local.tm_min:02d}", SECOND=f"{local.tm_sec:02d}")

    def formatShort(self, timestamp):
        local = time.localtime(timestamp)
        return self._words.fill("short", DAY=f"{local.tm_mday:02d}",
                                MONTH=self._words.text("months").split("|")[local.tm_mon - 1][:3],
                                HOUR=f"{local.tm_hour:02d}", MINUTE=f"{local.tm_min:02d}")

    def formatAgo(self, timestamp, now=None):
        now = self.now() if now is None else now
        delta = max(0.0, now - timestamp)
        if delta < 60:
            return self._words.text("momentAgo")
        if delta < 3600:
            return self._words.fill("minutesAgo", MINUTES=int(delta // 60))
        nowLocal = time.localtime(now)
        thenLocal = time.localtime(timestamp)
        if nowLocal.tm_year == thenLocal.tm_year and nowLocal.tm_yday == thenLocal.tm_yday:
            return self._words.fill("hoursAgoToday", HOURS=int(delta // 3600),
                                    HOUR=f"{thenLocal.tm_hour:02d}", MINUTE=f"{thenLocal.tm_min:02d}")
        yesterday = ((nowLocal.tm_year == thenLocal.tm_year and nowLocal.tm_yday - thenLocal.tm_yday == 1)
                     or (nowLocal.tm_year - thenLocal.tm_year == 1
                         and thenLocal.tm_yday >= 365 and nowLocal.tm_yday == 1))
        if yesterday:
            return self._words.fill("yesterday", HOUR=f"{thenLocal.tm_hour:02d}",
                                    MINUTE=f"{thenLocal.tm_min:02d}")
        day, week, month, year = self._words.text("units").split("|")
        days = int(delta // 86400)
        if days < 7:
            return self._plural(days, day)
        if days < 30:
            return self._plural(days // 7, week)
        if days // 30 < 12:
            return self._plural(days // 30, month)
        return self._plural(days // 365, year)

    def formatDuration(self, seconds):
        if seconds < 60:
            return self._words.fill("seconds", COUNT=int(seconds))
        if seconds < 3600:
            return self._words.fill("minutes", COUNT=int(seconds // 60))
        if seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            if minutes:
                return self._words.fill("hoursMinutes", COUNT=hours, MINUTES=minutes)
            return self._words.fill("hours", COUNT=hours)
        days = int(seconds // 86400)
        return self._words.fill("oneDay" if days == 1 else "days", COUNT=days)

    def _plural(self, count, unit):
        return self._words.fill("unitAgo" if count == 1 else "unitsAgo", COUNT=count, UNIT=unit)
