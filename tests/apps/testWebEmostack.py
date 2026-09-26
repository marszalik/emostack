import json
import os
import sys
import tempfile
import time
import unittest

here = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "apps", "web-emostack")

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


@unittest.skipIf(TestClient is None, "the web application needs the packages in requirements.txt")
class testWebEmostack(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, here)
        from tests.support.scriptedProcessor import scriptedProcessor
        from tests.support.wordEmbedder import wordEmbedder
        from domains.models.serviceConnect import serviceConnect
        from domains.auth.sessionCookie import sessionCookie
        os.environ["COOKIE_SECRET"] = "test-secret"
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, "config.json")
        with open(path, "w") as f:
            json.dump({"dataFolder": os.path.join(folder, "data"), "adminEmails": ["admin@example.com"], "identity": "cookie",
                       "requireLoginLevel": 1, "defaultLevel": 1, "requireUserModel": True}, f)
        os.environ["EMOSTACK_WEB_CONFIG"] = path
        self.processor = scriptedProcessor()
        serviceConnect.processor = lambda connect, person: self.processor
        serviceConnect.embedder = lambda connect, person: wordEmbedder()
        from app import build
        self.client = TestClient(build())
        self.cookie = sessionCookie("test-secret")

    def signIn(self, email):
        self.client.cookies.set("esSession", self.cookie.make({"email": email}))

    def testTheGateStopsSomeoneNotSignedIn(self):
        response = self.client.get("/", headers={"accept": "text/html"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("signed-in people", response.text)

    def testALocalInstallationNeedsNoSignIn(self):
        self.client.app.state.application.config.values["identity"] = "local"
        self.assertEqual(self.client.get("/").status_code, 200)

    def testAProxyPassesThePerson(self):
        config = self.client.app.state.application.config.values
        config["identity"] = "header"
        self.assertEqual(self.client.get("/", headers={"X-Auth-Email": "guest@example.com"}).status_code, 200)
        self.assertEqual(self.client.get("/", headers={"accept": "text/html"}).status_code, 401)

    def testAGuestNeedsAModelBeforeTalking(self):
        self.signIn("guest@example.com")
        self.assertEqual(self.client.get("/").status_code, 200)
        created = self.client.post("/beings", data={"name": "Maya"}).json()
        response = self.client.post("/conversations", data={"beingId": created["id"], "name": "Ann"})
        self.assertEqual(response.status_code, 409)

    def testAnAdministratorTalksAndTheBeingRemembers(self):
        self.signIn("admin@example.com")
        created = self.client.post("/beings", data={"name": "Maya"}).json()
        conversationId = self.client.post("/conversations", data={"beingId": created["id"], "name": "Ann"}).json()["id"]
        self.assertEqual(self.client.get(f"/conversations/{conversationId}").status_code, 200)
        greeting = self.client.post(f"/conversations/{conversationId}/greeting").json()["message"]
        self.assertEqual(greeting["text"], "Hello.")
        self.assertTrue(greeting["calls"])
        self.assertEqual(self.client.post(f"/conversations/{conversationId}/hear", data={"words": "Hi there."}).status_code, 200)
        for _ in range(50):
            live = self.client.app.state.application.conversations[conversationId]
            if not live.busy:
                break
            time.sleep(0.1)
        self.assertEqual(live.messages[-1]["role"], "being")
        state = self.client.get(f"/conversations/{conversationId}/state").json()
        self.assertTrue(state["focus"])
        self.client.post(f"/conversations/{conversationId}/leave")
        time.sleep(0.5)
        page = self.client.get(f"/beings/{created['id']}")
        self.assertIn("Someone spoke and the being answered.", page.text)

    def testTheAdministratorSeesEveryoneWhoCame(self):
        self.signIn("guest@example.com")
        self.client.get("/")
        self.signIn("admin@example.com")
        page = self.client.get("/people").text
        self.assertIn("guest@example.com", page)
        self.assertIn("Everyone who has signed in", page)

    def testAPersonalModelIsSavedWithoutShowingTheKey(self):
        self.signIn("guest@example.com")
        response = self.client.post("/me/model", data={
            "provider": "openai", "model": "gpt-4o-mini", "apiKey": "sk-secret-key-123456",
            "route.appraisal.provider": "anthropic", "route.appraisal.model": "claude-haiku-4-5-20251001",
            "route.appraisal.apiKey": "sk-ant-other-key-98765"}).json()
        self.assertTrue(response["ok"])
        self.assertNotIn("sk-secret-key-123456", json.dumps(response))
        self.assertEqual(response["saved"]["routes"]["appraisal"]["provider"], "anthropic")
        self.assertNotIn("sk-secret-key-123456", self.client.get("/me/model").text)
