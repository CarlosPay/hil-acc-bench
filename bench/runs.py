import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from bench.timing import (
    ACC_REQUEST_PERIOD_STEPS,
    EGO_STATUS_PERIOD_STEPS,
    SENSOR_OBJECT_PERIOD_STEPS,
    STEP_S,
)

RUNS_ROOT = Path(__file__).resolve().parents[1] / "runs"


def _git_commit_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def new_session_dir(test_case_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_dir = RUNS_ROOT / f"{timestamp}_{test_case_id}"
    session_dir.mkdir(parents=True)
    return session_dir


def write_manifest(
    session_dir: Path, test_case_id: str, runs: list[dict], evaluation: dict
) -> Path:
    manifest = {
        "test_case_id": test_case_id,
        "git_commit_sha": _git_commit_sha(),
        "step_s": STEP_S,
        "bus_periods_s": {
            "EGO_STATUS": STEP_S * EGO_STATUS_PERIOD_STEPS,
            "SENSOR_OBJECT": STEP_S * SENSOR_OBJECT_PERIOD_STEPS,
            "ACC_REQUEST": STEP_S * ACC_REQUEST_PERIOD_STEPS,
        },
        "evaluation": evaluation,
        "runs": runs,
    }
    manifest_path = session_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path
