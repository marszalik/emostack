import json
import os


class repositorySnapshots:
    """Beings that have lived, offered as a copy to take: snapshots/snapshots.json lists them
    ({slug, name, tagline, description, beingId}) and snapshots/<slug>.db holds each."""

    def __init__(self, dataFolder):
        self.folder = os.path.join(dataFolder, "snapshots")

    def all(self):
        listing = os.path.join(self.folder, "snapshots.json")
        if not os.path.exists(listing):
            return []
        with open(listing, encoding="utf-8") as f:
            items = json.load(f)
        return [dict(item, path=os.path.join(self.folder, f"{item['slug']}.db")) for item in items
                if os.path.exists(os.path.join(self.folder, f"{item['slug']}.db"))]

    def get(self, slug):
        return next((item for item in self.all() if item["slug"] == slug), None)
