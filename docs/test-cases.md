# docs/test-cases.md

## TC-ACC-001 — Steady state gap, constant target speed

Verifies: REQ-ACC-001
Type: nominal

### Preconditions
- ACC active, set speed 100 km/h
- Ego speed 75 km/h
- Valid target detected, range 20.8 m (gap = 1.0 s)
- Target speed 75 km/h, constant

### Stimulus
Target holds 75 km/h from t = 0 s to t = 20 s.

### Measurement
Time gap = range / ego speed, sampled every 10 ms.

### Evaluation window
t = 5 s to t = 20 s.

### Acceptance criteria
- AC1: time gap stays within 1.0 ± 0.15 s across the whole window
- AC2: no sample outside tolerance

### Environment capabilities required
- Initialize the scenario at a given ego speed, target speed and
  range, without a run-up phase
- Activate ACC and set the driver set speed
- Command target vehicle speed and acceleration over time
- Observe ego speed
- Observe range to the target
- Observe the ACC control output (torque or acceleration request)
- Observe ACC state (active / inactive)
- Sample all observed signals at 10 ms or faster, on a shared
  time base


---

## TC-ACC-002 — Target decelerates within envelope

Verifies: REQ-ACC-001
Type: nominal, dynamic

### Preconditions
- ACC active, set speed 100 km/h
- Ego speed 75 km/h
- Valid target detected, range 20.8 m (gap = 1.0 s)
- Target speed 75 km/h, constant

### Stimulus
- t = 0 s to 5 s: target holds 75 km/h
- t = 5 s to 9 s: target decelerates at 1.5 m/s²
- t = 9 s to 25 s: target holds 53.4 km/h

### Measurement
Time gap = range / ego speed, sampled every 10 ms.

### Evaluation window
- Steady state before: t = 2 s to 5 s
- Transient (excluded from AC1): t = 5 s to 14 s
- Steady state after: t = 14 s to 25 s

### Acceptance criteria
- AC1: gap within 1.0 ± 0.15 s during both steady-state windows
- AC2: gap overshoot during transient does not exceed 0.3 s
- AC3: steady state re-established by t = 14 s

### Environment capabilities required
- Initialize the scenario at a given ego speed, target speed and
  range, without a run-up phase
- Activate ACC and set the driver set speed
- Command target vehicle speed and acceleration over time
- Observe ego speed
- Observe range to the target
- Observe the ACC control output (torque or acceleration request)
- Observe ACC state (active / inactive)
- Sample all observed signals at 10 ms or faster, on a shared
  time base
- Command a target acceleration profile with a specified magnitude
  and duration, not only a constant speed
- Apply stimulus changes at exact simulation timestamps, with no
  jitter relative to the simulation clock
---

## TC-ACC-003 — Target accelerates at envelope boundary

Verifies: REQ-ACC-001
Type: boundary value

### Preconditions
- ACC active, set speed 130 km/h
- Ego speed 75 km/h
- Valid target detected, range 20.8 m (gap = 1.0 s)
- Target speed 75 km/h, constant

### Stimulus
- t = 0 s to 5 s: target holds 75 km/h
- t = 5 s to 10 s: target accelerates at 2.0 m/s²
- t = 10 s to 25 s: target holds 111 km/h

### Measurement
Time gap = range / ego speed, sampled every 10 ms.

### Evaluation window
- Steady state before: t = 2 s to 5 s
- Transient (excluded from AC1): t = 5 s to 15 s
- Steady state after: t = 15 s to 25 s

### Acceptance criteria
- AC1: gap within 1.0 ± 0.15 s during both steady-state windows
- AC2: gap undershoot during transient does not exceed 0.3 s
- AC3: steady state re-established by t = 15 s

### Environment capabilities required
- Initialize the scenario at a given ego speed, target speed and
  range, without a run-up phase
- Activate ACC and set the driver set speed
- Command target vehicle speed and acceleration over time
- Observe ego speed
- Observe range to the target
- Observe the ACC control output (torque or acceleration request)
- Observe ACC state (active / inactive)
- Sample all observed signals at 10 ms or faster, on a shared
  time base
- Command a target acceleration profile with a specified magnitude
  and duration, not only a constant speed
- Apply stimulus changes at exact simulation timestamps, with no
  jitter relative to the simulation clock