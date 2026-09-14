class LeadVehicle:
    """Kinematic lead vehicle. Acceleration is commandable by the test at
    any time to script a stimulus profile."""

    def __init__(self, initial_speed_mps: float) -> None:
        self.speed_mps = initial_speed_mps
        self.accel_mps2 = 0.0

    def command_acceleration(self, accel_mps2: float) -> None:
        self.accel_mps2 = accel_mps2

    def step(self, dt_s: float) -> None:
        self.speed_mps = max(0.0, self.speed_mps + self.accel_mps2 * dt_s)
