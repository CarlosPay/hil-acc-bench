from dataclasses import dataclass

import can

from bench import messages
from bench.timing import EGO_STATUS_PERIOD_STEPS, SENSOR_OBJECT_PERIOD_STEPS, STEP_S
from bench.trace import TraceWriter
from plant.clock import SimClock
from plant.ego import EgoVehicle
from plant.lead import LeadVehicle
from plant.sensor import IdealSensor


@dataclass
class StepResult:
    sim_time_s: float
    ego_speed_mps: float
    lead_speed_mps: float
    range_m: float
    time_gap_s: float
    accel_request_mps2: float


class Plant:
    def __init__(
        self,
        bus: can.Bus,
        initial_ego_speed_mps: float,
        initial_lead_speed_mps: float,
        initial_range_m: float,
        step_s: float = STEP_S,
        trace: TraceWriter | None = None,
    ) -> None:
        self._bus = bus
        self.clock = SimClock(step_s)
        self.ego = EgoVehicle(initial_ego_speed_mps)
        self.lead = LeadVehicle(initial_lead_speed_mps)
        self.sensor = IdealSensor()
        self.range_m = initial_range_m
        self._trace = trace
        self._ego_counter = 0
        self._sensor_counter = 0
        self._accel_request_mps2 = 0.0

    def _drain_acc_requests(self) -> None:
        while True:
            msg = self._bus.recv(timeout=0)
            if msg is None:
                return
            if msg.arbitration_id == messages.ACC_REQUEST.frame_id:
                decoded = messages.decode_acc_request(msg.data)
                self._accel_request_mps2 = float(decoded["AccelRequest"])

    def step(self) -> StepResult:
        self._drain_acc_requests()

        dt_s = self.clock.step_s
        range_rate_mps = self.lead.speed_mps - self.ego.speed_mps
        self.ego.step(self._accel_request_mps2, dt_s)
        self.lead.step(dt_s)
        self.range_m += range_rate_mps * dt_s

        sim_time_s = self.clock.advance()
        step_index = self.clock.steps

        if step_index % EGO_STATUS_PERIOD_STEPS == 0:
            self._bus.send(messages.build_ego_status(self.ego.speed_mps, self._ego_counter))
            self._ego_counter += 1

        if step_index % SENSOR_OBJECT_PERIOD_STEPS == 0:
            range_m, range_rate_m, valid = self.sensor.measure(self.range_m, range_rate_mps)
            self._bus.send(messages.build_sensor_object(range_m, range_rate_m, valid, self._sensor_counter))
            self._sensor_counter += 1

        time_gap_s = self.range_m / self.ego.speed_mps if self.ego.speed_mps > 0 else float("nan")

        result = StepResult(
            sim_time_s=sim_time_s,
            ego_speed_mps=self.ego.speed_mps,
            lead_speed_mps=self.lead.speed_mps,
            range_m=self.range_m,
            time_gap_s=time_gap_s,
            accel_request_mps2=self._accel_request_mps2,
        )

        if self._trace is not None:
            self._trace.write_row(**result.__dict__)

        return result
