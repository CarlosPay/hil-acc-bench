# docs/requirements.md

## REQ-ACC-001 — Time gap control in follow mode

**Preconditions**
- ACC is active
- Ego speed between 30 and 180 km/h
- A valid target object is detected
- Target speed is below the ACC set speed
- Target acceleration stays within ±2 m/s²
- Time gap is already established at the target value

**Requirement**
The measured time gap, defined as range divided by ego speed,
shall remain within 1.0 ± 0.15 s in steady state.

**Timing**
- Steady state shall be re-established within 5 s of the last
  target state change
- Time gap overshoot shall not exceed 0.3 s

---

## REQ-ACC-002 — Approach to a slower target

**Preconditions**
- ACC is active
- Ego speed between 30 and 180 km/h
- A valid target object is detected
- Target speed is below the ACC set speed
- Measured time gap is greater than 1.15 s
- Target speed is constant within ±0.5 m/s²

**Requirement**
The ego vehicle shall reduce the time gap to 1.0 ± 0.15 s and
hold it, without the gap ever falling below 0.85 s during the
approach.

**Comfort limits**
- Deceleration during approach shall not exceed 2.0 m/s²
- Jerk shall not exceed 2.5 m/s³

**Timing**
No convergence deadline applies. Approach duration is governed by
the initial gap and the closing speed.

## REQ-SEN-001 — Sensor detection range

The sensor model shall report a valid target object for ranges between
0.90 m and 250.00 m. Outside this interval no valid object is reported.