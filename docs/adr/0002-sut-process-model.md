# ADR-0002: SUT process model

- **Status:** Accepted
- **Date:** 2026-09-14
- **Qualifies:** ADR-0001, Decision 2 (plant ↔ SUT boundary)

## Context

ADR-0001 established that the plant and the SUT exchange data only over CAN. It
did not say how the SUT is hosted at runtime. That question surfaced when
planning stage 1: launching the SUT as a thread inside the test process is
easier to start and stop than launching a real operating-system process,
particularly in a CI runner.

The proposal under consideration was a split: thread locally, subprocess in CI.

## Options considered

| Option | Why not chosen |
|---|---|
| SUT as a thread in the test process | Shares memory with the test; the CAN-only rule becomes a convention rather than a structural property |
| Thread locally, subprocess in CI | Two different benches. What is developed against is not what is verified |
| SUT as a separate process, always | **Chosen** |

## Decision

The SUT runs as a **separate operating-system process, in every environment** —
local development and CI alike. It is started and stopped by a test fixture and
has no interface to the rest of the bench other than the CAN bus.

**The primary reason is fidelity to the system being tested.** A real ECU runs
its function in isolation. It cannot see the internal state of any other node;
it knows only what arrives on the bus. A bench whose SUT can read the test's
memory does not reproduce that property, and the interface it exercises is
therefore not the interface the real system has.

Two consequences follow from the same reasoning:

**The CAN-only rule becomes structural rather than voluntary.** With separate
processes there is no shared memory to bypass the bus with. The constraint is
enforced by the operating system instead of by discipline, which means it cannot
be violated by accident or forgotten under time pressure.

**Local and CI runs exercise the same bench.** A split model would mean
developing against one configuration and verifying against another — the classic
source of failures that appear only in the pipeline. Keeping one model removes
that class of problem entirely, and removes the environment-dependent branch in
the launch code along with it.

## Consequences

**Positive**

- The SUT is isolated by construction; the bus is provably the only interface.
- One bench, one behaviour, in every environment.
- No environment-dependent launch logic to maintain.
- Replacing the Python SUT with a real ECU becomes a change of node, not a
  change of architecture.

**Negative**

- Process startup, shutdown and teardown are more work than thread management,
  and must be handled reliably in a pytest fixture, including on test failure.
- Slower test startup than an in-process thread.
- Debugging across a process boundary is less convenient than stepping through a
  single process.

**Accepted deliberately.** The cost is paid once, in the fixture. The property
bought is permanent.