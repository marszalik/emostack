import threading


class stopSignals:
    """A stop request for a run or an experiment, seen by the worker between two steps."""

    _events = {}
    _lock = threading.Lock()

    def signal(self, key):
        with self._lock:
            return self._events.setdefault(key, threading.Event())

    def stop(self, key):
        self.signal(key).set()

    def forget(self, key):
        with self._lock:
            self._events.pop(key, None)
