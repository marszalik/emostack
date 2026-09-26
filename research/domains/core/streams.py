import asyncio
import json
import threading
from collections import deque


class streams:
    """Live events of runs and experiments for the browser (server-sent events). Workers run in
    threads; `emit` is thread-safe; every stream keeps a short tail for a page opened late."""

    def __init__(self, tail=200):
        self.lock = threading.Lock()
        self.tails = {}
        self.listeners = {}
        self.tailSize = tail

    def emit(self, key, event):
        with self.lock:
            self.tails.setdefault(key, deque(maxlen=self.tailSize)).append(event)
            listeners = list(self.listeners.get(key, []))
        for loop, queue in listeners:
            loop.call_soon_threadsafe(queue.put_nowait, event)

    def tail(self, key):
        with self.lock:
            return list(self.tails.get(key, []))

    async def follow(self, key):
        loop = asyncio.get_running_loop()
        queue = asyncio.Queue()
        with self.lock:
            self.listeners.setdefault(key, []).append((loop, queue))
        try:
            for event in self.tail(key):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            with self.lock:
                self.listeners[key] = [item for item in self.listeners.get(key, []) if item[1] is not queue]
