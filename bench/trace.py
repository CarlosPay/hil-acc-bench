import csv
from pathlib import Path

FIELDNAMES = [
    "sim_time_s",
    "ego_speed_mps",
    "lead_speed_mps",
    "range_m",
    "time_gap_s",
    "accel_request_mps2",
]


class TraceWriter:
    """One CSV row per simulation step, written as the plant steps."""

    def __init__(self, path: Path) -> None:
        self._file = path.open("w", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDNAMES)
        self._writer.writeheader()

    def write_row(self, **fields: float) -> None:
        self._writer.writerow(fields)

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "TraceWriter":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
