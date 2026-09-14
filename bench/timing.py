import time

STEP_S = 0.010
EGO_STATUS_PERIOD_STEPS = 1
ACC_REQUEST_PERIOD_STEPS = 1
SENSOR_OBJECT_PERIOD_STEPS = 2


class FixedStepPacer:
    """Holds a loop to a fixed wall-clock cadence without accumulating
    drift from per-iteration work."""

    def __init__(self, step_s: float) -> None:
        self._step_s = step_s
        self._next_tick = time.monotonic() + step_s

    def wait_for_next_step(self) -> None:
        delay = self._next_tick - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self._next_tick += self._step_s
