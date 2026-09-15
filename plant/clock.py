class SimClock:
    """Fixed-step simulation clock. Owned exclusively by the plant; sim
    time advances one step at a time and never reads the wall clock."""

    def __init__(self, step_s: float) -> None:
        self.step_s = step_s
        self.steps = 0

    @property
    def sim_time_s(self) -> float:
        return self.steps * self.step_s

    def advance(self) -> float:
        self.steps += 1
        return self.sim_time_s
