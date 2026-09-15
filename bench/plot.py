"""Plot recorded trace signals against simulation time for a bench run or session.

Reads CSV traces written by bench.trace.TraceWriter and, where present, the
"evaluation" block written by bench.runs.write_manifest, so a plotted
tolerance band or evaluation window always matches the criteria a verdict was
actually judged against, instead of a value typed on the command line.
--target/--tolerance/--window-start/--window-end exist only for exploration
and override the manifest when given.

Known limitation: all --signal values share one y-axis. Signals with very
different scales (e.g. ego_speed_mps next to time_gap_s) will flatten the
smaller one into a near-invisible line close to zero. Pick signals with
comparable units, or make separate plots.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from bench.trace import FIELDNAMES

SIGNAL_CHOICES = [name for name in FIELDNAMES if name != "sim_time_s"]


def _load_manifest(session_dir: Path) -> dict | None:
    manifest_path = session_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text())


def _resolve_evaluation_value(
    key: str, manifest: dict | None, override: float | None
) -> float | None:
    if override is not None:
        return override
    if manifest is not None:
        return manifest.get("evaluation", {}).get(key)
    return None


def _run_csv_paths(session_dir: Path) -> list[Path]:
    return sorted(session_dir.glob("run_*.csv"))


def _resolve_target(
    target: Path, run_index: int | None, overlay: bool
) -> tuple[list[Path], Path]:
    """Returns (csv paths to plot, directory to read the manifest from / default output dir)."""
    if target.is_dir():
        session_dir = target
        if overlay:
            csv_paths = _run_csv_paths(session_dir)
            if not csv_paths:
                raise SystemExit(f"no run_*.csv files found under {session_dir}")
        else:
            index = run_index if run_index is not None else 0
            csv_path = session_dir / f"run_{index:03d}.csv"
            if not csv_path.exists():
                raise SystemExit(f"{csv_path} does not exist")
            csv_paths = [csv_path]
        return csv_paths, session_dir

    if run_index is not None or overlay:
        raise SystemExit(
            "--run/--overlay only apply to a session directory target, not a single CSV"
        )
    if not target.exists():
        raise SystemExit(f"{target} does not exist")
    return [target], target.parent


def _default_output_path(
    output_dir: Path, csv_paths: list[Path], signals: list[str], overlay: bool
) -> Path:
    signal_tag = "_".join(signals)
    if overlay:
        name = f"plot_{signal_tag}_overlay.png"
    elif len(csv_paths) == 1:
        name = f"plot_{signal_tag}_{csv_paths[0].stem}.png"
    else:
        name = f"plot_{signal_tag}.png"
    return output_dir / name


def make_plot(
    csv_paths: list[Path],
    signals: list[str],
    *,
    tolerance_band: bool = False,
    evaluation_window: bool = False,
    target: float | None = None,
    tolerance: float | None = None,
    window_start: float | None = None,
    window_end: float | None = None,
    overlay: bool = False,
) -> plt.Figure:
    fig, ax = plt.subplots()

    if evaluation_window:
        if window_start is None or window_end is None:
            raise SystemExit(
                "--evaluation-window requested but window_start_s/window_end_s are not "
                "available from the manifest or --window-start/--window-end"
            )
        ax.axvspan(
            window_start,
            window_end,
            color="tab:orange",
            alpha=0.12,
            label="evaluation window",
        )

    if tolerance_band:
        if target is None or tolerance is None:
            raise SystemExit(
                "--tolerance-band requested but target_s/tolerance_s are not "
                "available from the manifest or --target/--tolerance"
            )
        ax.axhspan(
            target - tolerance,
            target + tolerance,
            color="tab:gray",
            alpha=0.15,
            label=f"tolerance {target}±{tolerance}",
        )

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, signal in enumerate(signals):
        color = colors[i % len(colors)]
        for j, csv_path in enumerate(csv_paths):
            df = pd.read_csv(csv_path)
            label = signal if j == 0 else None
            alpha = 0.5 if overlay and len(csv_paths) > 1 else 1.0
            ax.plot(df["sim_time_s"], df[signal], color=color, alpha=alpha, label=label)

    ax.set_xlabel("simulation time [s]")
    ax.set_ylabel(", ".join(signals))
    title = ", ".join(signals)
    if overlay:
        title += f" ({len(csv_paths)} runs)"
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="session directory or a single run_NNN.csv")
    parser.add_argument(
        "--signal",
        action="append",
        required=True,
        choices=SIGNAL_CHOICES,
        dest="signals",
        help="trace column to plot; repeat for more than one",
    )
    run_group = parser.add_mutually_exclusive_group()
    run_group.add_argument(
        "--run", type=int, default=None, help="run index within a session directory (default: 0)"
    )
    run_group.add_argument(
        "--overlay", action="store_true", help="plot the signal(s) from every run in the session"
    )
    parser.add_argument("--tolerance-band", action="store_true")
    parser.add_argument("--evaluation-window", action="store_true")
    parser.add_argument(
        "--target", type=float, default=None, dest="target_value",
        help="override the manifest evaluation target_s",
    )
    parser.add_argument(
        "--tolerance", type=float, default=None, dest="tolerance_value",
        help="override the manifest evaluation tolerance_s",
    )
    parser.add_argument(
        "--window-start", type=float, default=None,
        help="override the manifest evaluation window_start_s",
    )
    parser.add_argument(
        "--window-end", type=float, default=None,
        help="override the manifest evaluation window_end_s",
    )
    parser.add_argument("--out", type=Path, default=None, help="output PNG path")
    args = parser.parse_args(argv)

    csv_paths, output_dir = _resolve_target(args.target, args.run, args.overlay)
    manifest = _load_manifest(output_dir)

    eval_target = _resolve_evaluation_value("target_s", manifest, args.target_value)
    eval_tolerance = _resolve_evaluation_value("tolerance_s", manifest, args.tolerance_value)
    eval_window_start = _resolve_evaluation_value("window_start_s", manifest, args.window_start)
    eval_window_end = _resolve_evaluation_value("window_end_s", manifest, args.window_end)

    fig = make_plot(
        csv_paths,
        args.signals,
        tolerance_band=args.tolerance_band,
        evaluation_window=args.evaluation_window,
        target=eval_target,
        tolerance=eval_tolerance,
        window_start=eval_window_start,
        window_end=eval_window_end,
        overlay=args.overlay,
    )

    out_path = args.out or _default_output_path(
        output_dir, csv_paths, args.signals, args.overlay
    )
    fig.savefig(out_path)
    plt.close(fig)
    print(out_path)


if __name__ == "__main__":
    main()
