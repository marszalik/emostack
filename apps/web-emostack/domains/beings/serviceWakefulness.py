class serviceWakefulness:
    """Wakes a being or puts it to sleep by hand. Awake, it thinks on its own in the quiet; asleep,
    it folds the day and forgets what is weak."""

    def __init__(self, engine):
        self.engine = engine

    def set(self, beingId, awake):
        being = self.engine.beings.get(beingId)
        if being is None:
            raise ValueError("no such being")
        now = self.engine.time.now()
        if awake:
            being.wake(now)
        else:
            being.fallAsleep(now)
        self.engine.beings.saveWakefulness(being)
        return being.isAwake()
