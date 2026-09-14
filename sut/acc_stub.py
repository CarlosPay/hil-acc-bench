import can

from bench import messages
from bench.timing import ACC_REQUEST_PERIOD_STEPS


class AccStub:
    """Stage 1 has no control law. It consumes the bus inputs to prove the
    interface works and always requests zero acceleration."""

    def __init__(self, bus: can.Bus) -> None:
        self._bus = bus
        self._step_count = 0
        self._counter = 0

    def _drain_inputs(self) -> None:
        while True:
            msg = self._bus.recv(timeout=0)
            if msg is None:
                return
            if msg.arbitration_id == messages.EGO_STATUS.frame_id:
                messages.decode_ego_status(msg.data)
            elif msg.arbitration_id == messages.SENSOR_OBJECT.frame_id:
                messages.decode_sensor_object(msg.data)

    def step(self) -> None:
        self._drain_inputs()
        self._step_count += 1
        if self._step_count % ACC_REQUEST_PERIOD_STEPS == 0:
            self._bus.send(messages.build_acc_request(0.0, "ACTIVE", self._counter))
            self._counter += 1
