from pathlib import Path

import can
import cantools

_DBC_PATH = Path(__file__).parent / "bench.dbc"
_db = cantools.database.load_file(_DBC_PATH)

EGO_STATUS = _db.get_message_by_name("EGO_STATUS")
SENSOR_OBJECT = _db.get_message_by_name("SENSOR_OBJECT")
ACC_REQUEST = _db.get_message_by_name("ACC_REQUEST")


def build_ego_status(ego_speed_mps: float, counter: int) -> can.Message:
    data = EGO_STATUS.encode({"EgoSpeed": ego_speed_mps, "Counter": counter % 256})
    return can.Message(arbitration_id=EGO_STATUS.frame_id, data=data, is_extended_id=False)


def decode_ego_status(data: bytes) -> dict:
    return EGO_STATUS.decode(data)


def build_sensor_object(range_m: float, range_rate_mps: float, valid: bool, counter: int) -> can.Message:
    data = SENSOR_OBJECT.encode(
        {
            "Range": range_m,
            "RangeRate": range_rate_mps,
            "ObjectValid": int(valid),
            "Counter": counter % 256,
        }
    )
    return can.Message(arbitration_id=SENSOR_OBJECT.frame_id, data=data, is_extended_id=False)


def decode_sensor_object(data: bytes) -> dict:
    return SENSOR_OBJECT.decode(data)


def build_acc_request(accel_request_mps2: float, state: str, counter: int) -> can.Message:
    data = ACC_REQUEST.encode(
        {
            "AccelRequest": accel_request_mps2,
            "AccState": state,
            "Counter": counter % 256,
        }
    )
    return can.Message(arbitration_id=ACC_REQUEST.frame_id, data=data, is_extended_id=False)


def decode_acc_request(data: bytes) -> dict:
    return ACC_REQUEST.decode(data)
