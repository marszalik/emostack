from emostack.core.config import config
from emostack.runtime.engine import engine
from domains.beings.serviceStoreFor import serviceStoreFor
from domains.models.serviceConnect import serviceConnect


class serviceEngineFor:
    """An engine over a person's store, running on the person's model. A conversation gets an
    engine of its own, so that the calls it records are its own."""

    def __init__(self, application):
        self.stores = serviceStoreFor(application)
        self.connect = serviceConnect(application)

    def engine(self, person):
        return engine(config({"databasePath": self.stores.path(person)}), processor=self.connect.processor(person),
                      embedder=self.connect.embedder(person))

    def reader(self, person):
        """An engine for reading and managing beings only: it is given no model and makes no call."""
        return engine(config({"databasePath": self.stores.path(person)}))
