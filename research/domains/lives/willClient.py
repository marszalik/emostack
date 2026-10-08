"""A client for one life of Will (mindot-ai/will, Apache-2.0), run as its HTTP sidecar in its own process with its own
mind file, on the same LLM model as the sheep through the local gateway. The panel perceives each visitor line to it and
waits for its next utterance; silence is recorded as silence. Between days the mind is left alone for a while on its own
tick clock. Everything the sidecar prints is kept in a log next to the panel's data."""
import json
import os
import socket
import subprocess
import time
import urllib.request

WILL_DIR = "/home/eli/dev/will"
BUN = os.path.expanduser("~/.bun/bin/bun")


class willClient:
    def __init__(self, runId, name, identity, model, baseUrl, apiKey, logDir, tickMs=200, idleSeconds=90):
        self.runId = runId
        self.name = name
        self.identity = identity
        self.model = model
        self.baseUrl = baseUrl
        self.apiKey = apiKey
        self.logDir = logDir
        self.tickMs = tickMs
        self.idleSeconds = idleSeconds
        self.port = self._freePort()
        self.process = None
        self.log = None

    @staticmethod
    def _freePort():
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def start(self):
        os.makedirs(self.logDir, exist_ok=True)
        env = dict(os.environ)
        env.update({"WILL_NAME": self.name, "WILL_IDENTITY": self.identity, "WILL_LLM_PROVIDER": "vllm",
                    "WILL_LLM_BASE_URL": self.baseUrl, "WILL_LLM_API_KEY": self.apiKey, "WILL_LLM_MODEL": self.model,
                    "WILL_PMA_PATH": os.path.join(self.logDir, f"run{self.runId}.pma.json"),
                    "WILL_PORT": str(self.port), "WILL_HOST": "127.0.0.1", "WILL_TICK_MS": str(self.tickMs)})
        self.log = open(os.path.join(self.logDir, f"run{self.runId}.will.log"), "w")
        self.process = subprocess.Popen([BUN, "src/surface/cli.ts", "serve"], cwd=WILL_DIR, env=env,
                                        stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(60):
            time.sleep(2)
            try:
                self._get("/health", timeout=2)
                return
            except Exception:
                if self.process.poll() is not None:
                    raise RuntimeError(f"Will sidecar died at start (run {self.runId}); see its log")
        raise RuntimeError(f"Will sidecar did not answer /health in 120 s (run {self.runId})")

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                self._post("/save", {}, timeout=30)
            except Exception:
                pass
            self.process.terminate()
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.log:
            self.log.close()

    def say(self, person, text, withinMs=120000):
        self._post("/perceive", {"text": text, "from": person.lower(), "speaker": person}, timeout=300)
        answer = self._get(f"/next-utterance?within_ms={withinMs}&from={person.lower()}", timeout=withinMs / 1000 + 30)
        if answer.get("silence"):
            return ""
        return (answer.get("utterance") or {}).get("content", "") or ""

    def idle(self):
        time.sleep(self.idleSeconds)

    def state(self):
        try:
            return self._get("/state", timeout=10)
        except Exception as error:
            return {"error": str(error)}

    def _get(self, path, timeout):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=timeout) as r:
            return json.load(r)

    def _post(self, path, body, timeout):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", json.dumps(body).encode(),
                                     {"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
