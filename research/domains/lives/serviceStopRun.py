from research.domains.lives.stopSignals import stopSignals


class serviceStopRun:
    """Asks a running life to stop after the step it is in."""

    def stop(self, runId):
        stopSignals().stop(f"run:{runId}")
