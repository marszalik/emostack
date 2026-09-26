class clock:
    """The slow path in time. An awake being reflects first thing on waking and once after a
    silence; after a long silence it falls asleep; some minutes into sleep the awake period is
    folded and what is too weak for its age is forgotten."""

    def __init__(self, beings, mindFor, time, parameters):
        self.beings = beings
        self.mindFor = mindFor
        self.time = time
        self.parameters = parameters

    def tick(self):
        now = self.time.now()
        for being in self.beings.all():
            if being.isAwake():
                self._awake(being, now)
            elif not being.consolidated and being.sleptAt > 0:
                self._asleep(being, now)

    def _awake(self, being, now):
        if being.wakePending:
            self.mindFor(being).reflection().run()
            being.wakePending = False
            being.introspectedIdle = True
            self.beings.saveWakefulness(being)
            return
        idle = now - being.lastActivity
        if idle >= self.parameters["sleepAfterSeconds"]:
            if not being.introspectedIdle:
                self.mindFor(being).reflection().run()
                being.introspectedIdle = True
            being.fallAsleep(now)
            self.beings.saveWakefulness(being)
        elif idle >= self.parameters["silenceSeconds"] and not being.introspectedIdle:
            self.mindFor(being).reflection().run()
            being.introspectedIdle = True
            self.beings.saveWakefulness(being)

    def _asleep(self, being, now):
        if now - being.sleptAt < self.parameters["consolidateAfterSleepSeconds"]:
            return
        mind = self.mindFor(being)
        if being.wokeAt > 0:
            mind.sleep().consolidate(being, being.wokeAt)
        mind.sleep().forget()
        being.consolidated = True
        self.beings.saveWakefulness(being)
