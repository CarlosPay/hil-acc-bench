class EgoVehicle:
    """First-order longitudinal ego dynamics: actual acceleration lags the
    requested acceleration with a fixed time constant."""

    def __init__(self, initial_speed_mps: float, time_constant_s: float = 0.5) -> None:
        self.speed_mps = initial_speed_mps
        self.accel_mps2 = 0.0
        self._time_constant_s = time_constant_s

    def step(self, requested_accel_mps2: float, dt_s: float) -> None:
        self.accel_mps2 += (requested_accel_mps2 - self.accel_mps2) * (dt_s / self._time_constant_s)
        self.speed_mps = max(0.0, self.speed_mps + self.accel_mps2 * dt_s)
