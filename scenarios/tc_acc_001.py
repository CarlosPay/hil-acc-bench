from dataclasses import dataclass
from pathlib import Path

import can

from bench.sut_process import SutProcess
from bench.timing import STEP_S, FixedStepPacer
from bench.trace import TraceWriter
from bench.units import kmh_to_ms
from plant.runner import Plant

VCAN_CHANNEL = "vcan0"
EVALUATION_START_S = 5.0
EVALUATION_END_S = 20.0
GAP_TARGET_S = 1.0
GAP_TOLERANCE_S = 0.15


@dataclass
class RunResult:
    verdict: str
    metrics: dict


def run(csv_path: Path) -> RunResult:
    with SutProcess(VCAN_CHANNEL):
        bus = can.Bus(interface="socketcan", channel=VCAN_CHANNEL)
        gap_samples_in_window: list[float] = []
        out_of_tolerance = False

        try:
            with TraceWriter(csv_path) as trace:
                plant = Plant(
                    bus=bus,
                    initial_ego_speed_mps=kmh_to_ms(75.0),
                    initial_lead_speed_mps=kmh_to_ms(75.0),
                    initial_range_m=20.8,
                    trace=trace,
                )
                pacer = FixedStepPacer(STEP_S)
                n_steps = round(EVALUATION_END_S / STEP_S)
                for _ in range(n_steps):
                    result = plant.step()
                    if EVALUATION_START_S <= result.sim_time_s <= EVALUATION_END_S:
                        gap_samples_in_window.append(result.time_gap_s)
                        if abs(result.time_gap_s - GAP_TARGET_S) > GAP_TOLERANCE_S:
                            out_of_tolerance = True
                    pacer.wait_for_next_step()
        finally:
            bus.shutdown()

    verdict = "FAIL" if out_of_tolerance or not gap_samples_in_window else "PASS"
    mean_gap = (
        sum(gap_samples_in_window) / len(gap_samples_in_window)
        if gap_samples_in_window
        else float("nan")
    )

    return RunResult(
        verdict=verdict,
        metrics={
            "steady_state_time_gap_mean_s": mean_gap,
            "samples_in_window": len(gap_samples_in_window),
        },
    )
