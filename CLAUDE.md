# hil-acc-bench

Virtual test bench demonstrating the chain from an ADAS requirement
to the capabilities a test environment must provide to verify it.

## Working agreement

- Do NOT make architecture or design decisions. Propose options with
  trade-offs and wait for my choice.
- Every design decision needs an ADR in docs/adr/ that I write, not you.
  If I ask for code before the ADR exists, remind me.
- Explain what you are about to do before doing it. I am here to learn
  the reasoning, not just to receive files.
- Prefer small, focused commits. Message explains WHY, not what.

## Hard constraints

- No proprietary content. Everything generic and invented. No real OEM
  architectures, project names, DBC files or requirements.
- The DUT communicates ONLY over the CAN bus. Never a direct function
  call between plant and DUT.
- Determinism is a requirement, not a nice-to-have. Fixed-step clock,
  single time base, reproducible traces.
- No measurement artifacts committed to the repo. CI generates them.

## Stack

Python, python-can (virtual bus locally, vcan in CI), cantools, pytest,
numpy, PyYAML. English only, in code and docs.
