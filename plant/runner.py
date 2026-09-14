import can

from bench import messages
from bench.timing import EGO_STATUS_PERIOD_STEPS, SENSOR_OBJECT_PERIOD_STEPS
from plant.ego import EgoVehicle
from plant.lead import LeadVehicle
from plant.sensor import IdealSensor


class Plant:
    def __init__(
        self,
        bus: can.Bus,
        initial_ego_speed_mps: float,
        initial_lead_speed_mps: float,
        initial_range_m: float,
    ) -> None:
        self._bus = bus
        self.ego = EgoVehicle(initial_ego_speed_mps)
        self.lead = LeadVehicle(initial_lead_speed_mps)
        self.sensor = IdealSensor()
        self.range_m = initial_range_m
        self._step_count = 0
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

    def step(self, dt_s: float) -> None:
        self._drain_acc_requests()

        range_rate_mps = self.lead.speed_mps - self.ego.speed_mps
        self.ego.step(self._accel_request_mps2, dt_s)
        self.lead.step(dt_s)
        self.range_m += range_rate_mps * dt_s

        self._step_count += 1

        if self._step_count % EGO_STATUS_PERIOD_STEPS == 0:
            self._bus.send(messages.build_ego_status(self.ego.speed_mps, self._ego_counter))
            self._ego_counter += 1

        if self._step_count % SENSOR_OBJECT_PERIOD_STEPS == 0:
            range_m, range_rate_m, valid = self.sensor.measure(self.range_m, range_rate_mps)
            self._bus.send(messages.build_sensor_object(range_m, range_rate_m, valid, self._sensor_counter))
            self._sensor_counter += 1
