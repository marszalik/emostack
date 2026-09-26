import base64
import hashlib
import hmac
import json
import time


class sessionCookie:
    """A signed cookie holding who signed in, set by a sign-in domain added to the application. The
    email in it can be trusted as far as that sign-in verified it: the server signed it."""

    name = "esSession"
    stateName = "esOauthState"
    maxAge = 30 * 24 * 3600

    def __init__(self, secret):
        self.secret = secret or ""

    def make(self, profile):
        return self._sign({"email": profile["email"], "name": profile.get("name", ""),
                           "picture": profile.get("picture", ""), "issuedAt": time.time()})

    def read(self, token):
        if not token or not self.secret or "." not in token:
            return None
        body, _, signature = token.partition(".")
        if not hmac.compare_digest(signature, self._signature(body)):
            return None
        try:
            data = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        except ValueError:
            return None
        if time.time() - float(data.get("issuedAt", 0)) > self.maxAge or not data.get("email"):
            return None
        return data

    def _sign(self, data):
        body = base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()
        return f"{body}.{self._signature(body)}"

    def _signature(self, body):
        digest = hmac.new(self.secret.encode(), body.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
