# ADR-0001: Test level and SUT boundary

- **Status:** Accepted
- **Date:** 2026-09-14

## Context

This project builds a virtual test bench for an Adaptive Cruise Control (ACC)
function. Before any code is written, three coupled questions must be answered:

1. At which test level does this bench operate?
2. Where does the System Under Test end and the environment begin?
3. Where does the range signal consumed by the ACC come from?

These three decisions are recorded together because they constrain each other.
The answer to any one of them makes some answers to the others impossible.

---

## Decision 1 — Test level: SIL at system-function level

### Options considered

| Option | What runs | Why not chosen |
|---|---|---|
| MIL | Function as a model inside the modelling tool | Requires a modelling tool licence; the repository stops being runnable by a third party |
| SIL | Function as executable code, outside a target ECU | **Chosen** |
| PIL | Generated code on the target processor | No target hardware; no code generation in this project |
| HIL | Real ECU on a real-time platform with I/O | Requires a rack; the repository could not be cloned and executed |
| VIL | Full vehicle with the system installed | Out of reach and out of purpose |

### Decision

The bench operates at **Software-in-the-Loop level, testing the ACC as a system
function** rather than as a set of units.

The driving constraint is not the absence of hardware. It is that this
repository must be clonable and executable by anyone, on an ordinary machine,
with no licence and no rig. A bench that depends on a rack cannot demonstrate
anything to a reader who does not own one.

A second consequence follows from the same constraint: only a SIL bench can run
in CI. Without CI there is no continuous evidence that the bench and the
function still work — only a claim that they did once, locally.

### Honest limitation

There is no model-based code generation in this project. The ACC is written
directly as code. Therefore this bench does **not** verify model-to-code
equivalence, which is one of the classic purposes of SIL in an automotive
toolchain. What it verifies is the behaviour of the implemented function against
its requirements.

### Explicitly out of scope

- SUT-internal unit tests
- ECU timing and scheduling behaviour
- Electrical behaviour, wiring faults, bus physical layer
- Hard real-time guarantees

---

## Decision 2 — Plant ↔ SUT boundary: CAN, not direct calls

### Options considered

| Option | Why not chosen |
|---|---|
| Test calls the controller directly as a function | Fastest to build; hides every interface property that a real bench must handle |
| In-process queue between plant and SUT | Decouples the two, but is not an automotive interface and teaches nothing transferable |
| Virtual CAN bus with a DBC | **Chosen** |

### Decision

The plant and the SUT exchange data **only over CAN**. The SUT runs as a separate
process and has no other interface to the rest of the bench.

Three reasons:

**It is the interface the real system uses.** Skipping it saves effort now and
charges interest later: any move toward a real ECU would mean rewriting the
coupling rather than replacing one component.

**It makes the SUT replaceable.** Because the boundary is a bus and a message
catalogue, the Python controller can be removed and a real ECU put in its place
without touching the plant, the scenarios or the test cases. That substitutability
is the property that makes this a bench and not a simulation script.

**It forces the real problems into view from day one.** Message periodicity,
latency, and stale signals are not incidental overhead — they are part of what a
test environment has to manage. A bench that does not deal with them does not
resemble a bench.

### The boundary itself

The SUT is the ACC function. It ends at the **acceleration request**.

Everything else is plant: ego longitudinal dynamics, powertrain and brakes, the
lead vehicle, and the sensor model. The acceptance criteria in
`docs/requirements.md` are expressed in time gap, not in torque or brake
pressure, which is consistent with this boundary: once the ACC has asked for an
acceleration, its responsibility ends.

### Cost accepted

More complexity from the first commit: a DBC file, an encode/decode layer, and a
second process to start and stop in every test. This is accepted deliberately.

---

## Decision 3 — Range source: sensor model block from the start

### Options considered

| Option | Why not chosen |
|---|---|
| SUT reads true range from the plant | No place to inject perception error later without changing the architecture |
| Sensor model added in stage 3, when it is first needed | Introduces a structural change mid-project, invalidating earlier results |
| Sensor model present from stage 1, ideal at first | **Chosen** |

### Decision

Range is produced by a **sensor model block** that exists from stage 1. In stage 1
it is ideal: it passes the true range through unchanged. In stage 3 it becomes
configurable with noise, latency and target loss.

Most of the ACC behaviour can be developed and verified against an ideal sensor.
The realistic sensor is not needed to get the control right; it is needed to test
what the function does when perception is imperfect. Splitting those two concerns
in time is deliberate.

The decisive argument is diagnostic. Because the block is configurable rather
than hard-wired, **the same test case can be executed twice** — once with an
ideal sensor, once with a realistic one. If it passes ideal and fails realistic,
the failure has been isolated to perception without changing anything else. That
separation is impossible if the SUT reads plant truth directly.

---

## Consequences

**Positive**

- The repository can be cloned and executed with no licence and no hardware.
- CI is possible, so every commit carries evidence.
- The SUT can be replaced by a real ECU without redesigning the bench.
- Control failures and perception failures can be told apart by construction.

**Negative**

- CAN encode/decode and a second process from the first commit.
- A sensor model block that does nothing in stage 1 but must still be maintained.
- No claim can be made about ECU timing, electrical behaviour or real-time
  performance. Any such claim would require a different bench.

**Follow-ups**

- Terminology: use SUT consistently across the repository; `CLAUDE.md` still says DUT.
- Stage 3 will require an ADR of its own for the sensor model parameters.