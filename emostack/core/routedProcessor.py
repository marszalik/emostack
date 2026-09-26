from emostack.core.processor import processor


class routedProcessor(processor):
    """Several LLM models behind one processor: each call goes to the model chosen for its
    purpose (reply, appraisal, introspection, …), or to the default one. The calls are recorded
    here, whichever model answered them. One instance serves one conversation at a time."""

    def __init__(self, default, routes=None):
        super().__init__()
        self.default = default
        self.routes = dict(routes or {})
        self._target = default

    def converse(self, system, messages, temperature, responseFormat=None, purpose=""):
        self._target = self.routes.get(purpose, self.default)
        return super().converse(system, messages, temperature, responseFormat, purpose)

    def _send(self, system, messages, temperature, responseFormat):
        return self._target._send(system, messages, temperature, responseFormat)
