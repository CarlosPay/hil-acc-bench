import time
from pathlib import Path

import can
import pytest

from bench import messages
from bench.sut_process import SutProcess
from bench.timing import STEP_S, FixedStepPacer
from bench.units import kmh_to_ms
from plant.runner import Plant

VCAN_CHANNEL = "vcan0"
SIM_DURATION_S = 2.0


def _require_vcan() -> None:
    if not Path(f"/sys/class/net/{VCAN_CHANNEL}").exists():
        pytest.fail(
            f"{VCAN_CHANNEL} does not exist. Run scripts/setup-vcan.sh first "
            "-- it does not survive a restart."
        )


def test_walking_skeleton_end_to_end() -> None:
    _require_vcan()

    with SutProcess(VCAN_CHANNEL):
        observer_bus = can.Bus(interface="socketcan", channel=VCAN_CHANNEL)
        reader = can.BufferedReader()
        notifier = can.Notifier(observer_bus, [reader])

        plant_bus = can.Bus(interface="socketcan", channel=VCAN_CHANNEL)
        plant = Plant(
            bus=plant_bus,
            initial_ego_speed_mps=kmh_to_ms(75.0),
            initial_lead_speed_mps=kmh_to_ms(75.0),
            initial_range_m=20.8,
        )

        pacer = FixedStepPacer(STEP_S)
        try:
            for _ in range(int(SIM_DURATION_S / STEP_S)):
                plant.step(STEP_S)
                pacer.wait_for_next_step()
        finally:
            plant_bus.shutdown()

        seen_ids = set()
        collect_until = time.monotonic() + SIM_DURATION_S
        while time.monotonic() < collect_until:
            msg = reader.get_message(timeout=collect_until - time.monotonic())
            if msg is None:
                break
            seen_ids.add(msg.arbitration_id)
            if msg.arbitration_id == messages.EGO_STATUS.frame_id:
                messages.decode_ego_status(msg.data)
            elif msg.arbitration_id == messages.SENSOR_OBJECT.frame_id:
                messages.decode_sensor_object(msg.data)
            elif msg.arbitration_id == messages.ACC_REQUEST.frame_id:
                messages.decode_acc_request(msg.data)

        notifier.stop()
        observer_bus.shutdown()

    assert messages.EGO_STATUS.frame_id in seen_ids
    assert messages.SENSOR_OBJECT.frame_id in seen_ids
    assert messages.ACC_REQUEST.frame_id in seen_ids
