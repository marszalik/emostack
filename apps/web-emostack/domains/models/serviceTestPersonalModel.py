from emostack.core.ProcessorError import ProcessorError
from emostack.core.localEmbedder import localEmbedder
from domains.models.Provider import Provider


class serviceTestPersonalModel:
    """One tiny call on the person's key, and one embedding: does it work before a being depends
    on it?"""

    def __init__(self, connect, serverEmbedder):
        self.connect = connect
        self.serverEmbedder = serverEmbedder

    def test(self, model):
        try:
            answer = self.connect.processorFor(model).chat("Reply with the single word OK.", "Say OK.", 0.0,
                                                           purpose="test")
            provider = Provider.named(model["provider"])
            embedder = (localEmbedder({"baseUrl": model["baseUrl"], "apiKey": model["apiKey"],
                                       "model": provider.embedModel}) if provider.hasEmbeddings()
                        else localEmbedder(self.serverEmbedder))
            vector = embedder.embed("a short test sentence")
        except ProcessorError as error:
            message = str(error)
            return False, message.replace(model["apiKey"], "…")[:300]
        return True, f"the model replied: {answer.strip()[:60]} · a memory vector of {len(vector)} numbers"
