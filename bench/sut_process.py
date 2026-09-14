import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STARTUP_DELAY_S = 0.2


class SutProcess:
    """Launches the ACC stub as a real OS process on the given CAN channel.
    Used identically in local runs and in CI -- no environment branch."""

    def __init__(self, channel: str) -> None:
        self._channel = channel
        self._proc: subprocess.Popen | None = None

    def __enter__(self) -> "SutProcess":
        self._proc = subprocess.Popen(
            [sys.executable, "-m", "sut.run", "--channel", self._channel],
            cwd=REPO_ROOT,
        )
        time.sleep(STARTUP_DELAY_S)
        return self

    def __exit__(self, *exc_info: object) -> None:
        assert self._proc is not None
        self._proc.terminate()
        self._proc.wait(timeout=5)
