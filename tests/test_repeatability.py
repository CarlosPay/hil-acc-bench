import statistics

import pytest

from bench.runs import new_session_dir, write_manifest
from scenarios import tc_acc_001

NUM_RUNS = 20
GAP_STDEV_BUDGET_S = 0.010


@pytest.mark.repeatability
@pytest.mark.skip(
    reason=(
        "Not load-bearing yet: the ACC stub emits a constant acceleration "
        "request, so the steady-state gap has no causal dependence on SUT "
        "timing and this test cannot currently fail. Meaningful once stage 4 "
        "gives the SUT a real control law."
    )
)
def test_tc_acc_001_repeatability() -> None:
    session_dir = new_session_dir("TC-ACC-001")

    run_entries = []
    for index in range(NUM_RUNS):
        csv_path = session_dir / f"run_{index:03d}.csv"
        result = tc_acc_001.run(csv_path)
        run_entries.append(
            {
                "index": index,
                "seed": 0,
                "verdict": result.verdict,
                "metrics": result.metrics,
            }
        )

    write_manifest(session_dir, "TC-ACC-001", run_entries)

    verdicts = {entry["verdict"] for entry in run_entries}
    assert len(verdicts) == 1, f"verdicts were not identical: {run_entries}"

    gaps = [entry["metrics"]["steady_state_time_gap_mean_s"] for entry in run_entries]
    stdev = statistics.stdev(gaps)
    assert stdev < GAP_STDEV_BUDGET_S, f"steady-state gap stdev {stdev:.6f}s exceeds {GAP_STDEV_BUDGET_S}s budget"
