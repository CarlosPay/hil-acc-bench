# ADR-0003: Time advance and repeatability

- Status: Accepted
- Date: 2026-09-14
- Supersedes: none
- Related: ADR-0001 (test level and SUT boundary), ADR-0002 (SUT process model)

## Decision

The SUT runs free. It does not synchronise with the simulation and has no
knowledge of the bench clock. It reacts only to the CAN messages it receives.

The plant advances on a fixed step and publishes at a constant period, which
gives the bench a stable time base to measure against.

The bench does not promise bit-identical traces between runs. It promises
**verdict stability**: repeated executions of the same scenario produce the same
pass/fail outcome, and the run-to-run dispersion of the evaluated metrics is
measured and held below a stated budget.

## Context

ADR-0002 placed the SUT in a separate operating system process. The OS
scheduler therefore decides when each process runs, and that decision varies
between executions. As a consequence, two runs of the same scenario do not
produce identical traces.

Stage 2 requires a verifiable statement about the repeatability of the bench.
That forces an explicit decision about how time advances and about what the
bench actually guarantees.

## Alternatives considered

### Master clock with explicit synchronisation

A dedicated component issues a tick. The plant advances one step, publishes,
and the SUT confirms completion before the next tick is issued.

This yields true determinism — bit-identical traces across runs.

Rejected for two reasons. It requires a synchronisation channel outside CAN,
which contradicts the rule that the SUT communicates over the bus only. And it
departs from the behaviour of a HIL bench, where the ECU never waits for
permission to execute.

### Synchronisation over CAN itself

The plant publishes and does not advance until it receives the ACC_REQUEST for
that cycle. No side channel is needed, since the message already exists.

Rejected because it makes the SUT part of the control loop for time: if the SUT
does not answer, the plant stalls, and a timeout becomes load-bearing. It also
still differs from HIL, where the plant advances regardless of what the ECU
does.

## Consequences

### Accepted benefits

- The bench behaves like a real HIL setup. The plant advances regardless of the
  SUT, and the SUT is unaware that a simulation clock exists.
- The CAN-only rule stays intact. There is no side channel between plant and
  SUT.
- The SUT remains replaceable by a physical ECU with no change to the bench. A
  master clock would have broken this, since a real ECU does not acknowledge
  simulation steps.

### Accepted costs

- No bit-for-bit reproducibility. Identical scenarios produce slightly different
  traces, and the bench does not claim otherwise.
- Verdict stability must be demonstrated rather than asserted. Run-to-run
  dispersion is measured against a budget. For steady-state time gap the budget
  is 10 ms, roughly an order of magnitude below the REQ-ACC-001 tolerance of
  ±0.15 s.
- Every run must be recorded to CSV. Dispersion cannot be computed without
  per-run data, so trace logging becomes stage 2 infrastructure rather than a
  reporting feature.
- The repeatability test is expensive — twenty runs of the same scenario — so it
  does not execute on every push. It runs on a separate cadence.

### Open points

- The dispersion budget for settling time is not yet fixed. Settling time is a
  threshold crossing and is inherently noisier than a steady-state value. The
  budget will be derived from measurement and documented as such.

- The repeatability claim is stated but not yet validated. Stage 2's SUT is a
  stub with no control law: it emits a constant acceleration request, so the
  evaluated metric (steady-state time gap) has no causal dependence on SUT
  timing, and twenty runs produce a run-to-run standard deviation of exactly
  zero. That is not evidence the bench holds dispersion below budget — it is
  an artifact of the stub having nothing for timing to act on. Validation is
  deferred to stage 4, once a real control law exists for the metric to
  actually vary against.