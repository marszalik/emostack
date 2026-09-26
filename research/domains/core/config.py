import os


class config:
    """Where the panel keeps its own database and the stores of the lives it runs."""

    def __init__(self, root):
        self.root = root
        self.dataFolder = os.environ.get("EMOSTACK_PANEL_DATA", os.path.join(root, "data", "panel"))
        self.databasePath = os.path.join(self.dataFolder, "panel.db")
        self.storesFolder = os.path.join(self.dataFolder, "stores")
        self.scenariosFolder = os.path.join(root, "research", "scenarios")
        os.makedirs(self.storesFolder, exist_ok=True)
