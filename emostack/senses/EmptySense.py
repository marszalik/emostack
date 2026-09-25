class EmptySense:
    """A channel that carries nothing, and says so: sight, touch, smell and taste, body, place.
    Named as absent, it keeps the being from inventing a scene, a body or a place."""

    all = ("sight", "touch", "smellAndTaste", "body", "place")

    def __init__(self, name):
        self.name = name
