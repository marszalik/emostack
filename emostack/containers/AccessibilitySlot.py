from emostack.construct.SlotRole import SlotRole
from emostack.containers.SlotPlace import SlotPlace


class AccessibilitySlot:
    """What the being holds in mind of its own thoughts (accessibility in Higgins's sense). Three
    places; one is reserved for the newest decision, goal or dream. Beliefs and thoughts fill the
    free places by strength and enter a full set only if at least as strong as the weakest held,
    displacing the oldest. A construct enters when formed or brought back to mind and leaves when
    displaced, or after a week without being brought back. It survives the end of a conversation."""

    def __init__(self, beingId, hippocampus, repository, size=3, days=7.0):
        self.beingId = beingId
        self.hippocampus = hippocampus
        self.repository = repository
        self.size = int(size)
        self.days = float(days)
        self.places = []
        self.loaded = False

    def load(self, now):
        """Reads the slot and lets go of what was not brought back for too long."""
        self.places = []
        expired = False
        for recordId, activatedAt in self.repository.held(self.beingId):
            construct = self.hippocampus.record(recordId)
            if construct is None:
                expired = True
                continue
            if activatedAt < now - self.days * 86400.0:
                expired = True
                continue
            self.places.append((construct, activatedAt))
        if len(self.places) > max(0, self.size):
            self.places = self.places[-self.size:] if self.size > 0 else []
            expired = True
        if expired:
            self._save()
        self.loaded = True

    def held(self):
        return [construct for construct, _ in self.places]

    def ids(self):
        return {construct.id for construct, _ in self.places}

    @staticmethod
    def placeFor(construct):
        return SlotPlace.RESERVED if construct.slotRole is SlotRole.ACT else SlotPlace.FREE

    def activate(self, construct, now):
        """Puts a construct in the slot or refreshes it there. Returns whether it is held."""
        if self.size <= 0:
            return False
        if construct.id in self.ids():
            self.places = [(held, now if held.id == construct.id else at) for held, at in self.places]
            self._save()
            return True
        reserved = [(held, at) for held, at in self.places if self.placeFor(held) is SlotPlace.RESERVED]
        free = [(held, at) for held, at in self.places if self.placeFor(held) is SlotPlace.FREE]
        if self.placeFor(construct) is SlotPlace.RESERVED:
            if reserved:
                self.places = free
            elif len(self.places) >= self.size:
                oldest = min(free, key=lambda place: place[1])
                self.places = [place for place in self.places if place[0].id != oldest[0].id]
        else:
            room = self.size - (1 if reserved else 0)
            if len(free) >= room:
                if not free:
                    return False
                weakest = min(held.intensity for held, _ in free)
                if construct.intensity < weakest:
                    return False
                oldest = min(free, key=lambda place: place[1])
                self.places = [place for place in self.places if place[0].id != oldest[0].id]
        self.places.append((construct, now))
        self._save()
        return True

    def _save(self):
        latest = {}
        for construct, at in self.places:
            latest[construct.id] = (construct, at)
        self.places = sorted(latest.values(), key=lambda place: place[1])
        self.repository.replace(self.beingId, [(construct.id, at) for construct, at in self.places])
