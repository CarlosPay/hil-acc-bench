MIN_VALID_RANGE_M = 0.90  # REQ-SEN-001
MAX_VALID_RANGE_M = 250.00  # REQ-SEN-001


class IdealSensor:
    """Stage 1 sensor model: passes true range and range rate through
    unchanged. Only the valid-target decision is computed here."""

    def measure(self, true_range_m: float, true_range_rate_mps: float) -> tuple[float, float, bool]:
        valid = MIN_VALID_RANGE_M <= true_range_m <= MAX_VALID_RANGE_M
        return true_range_m, true_range_rate_mps, valid
