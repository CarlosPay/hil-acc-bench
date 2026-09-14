# hil-acc-bench

See `CLAUDE.md` for the working agreement and hard constraints, and
`docs/adr/` for the design decisions behind this bench.

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The plant and the SUT communicate over `vcan0`. It does not survive a
restart, so run this once per session before testing:

```
./scripts/setup-vcan.sh
```

## Running the tests

```
pytest
```

## Stage 1 status: walking skeleton

One end-to-end test (`tests/test_walking_skeleton.py`) runs the plant and
the ACC stub as a separate OS process, connected only over `vcan0`, for a
fixed simulation duration, and checks that all three CAN messages
(`EGO_STATUS`, `SENSOR_OBJECT`, `ACC_REQUEST`) were sent and are decodable.
Correct control behaviour is explicitly not the goal of this stage: the ACC
stub always requests zero acceleration.

### Known debt

Driver activation and set speed have no CAN representation yet. The ACC
stub is unconditionally active with no configurable set speed.
TC-ACC-001/002/003 cannot be executed as written until that exists.
