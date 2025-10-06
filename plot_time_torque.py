import csv
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from typing import List, Optional, Tuple


def convert_to_seconds(value_str: str, time_unit: str) -> float:
    value = float(value_str)
    unit_to_seconds = {
        "s": 1.0,
        "sec": 1.0,
        "ms": 1e-3,
        "us": 1e-6,
        "µs": 1e-6,
        "ns": 1e-9,
        "m": 60.0,
        "min": 60.0,
        "h": 3600.0,
        "hr": 3600.0,
        "hrs": 3600.0,
    }
    factor = unit_to_seconds.get(time_unit.lower())
    if factor is None:
        raise ValueError(f"Unsupported time unit: {time_unit}")
    return value * factor


def read_time_ms_and_torque(csv_path: Path, time_unit: str) -> Tuple[List[float], List[float]]:
    times_ms: List[float] = []
    torques: List[float] = []
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        first_timestamp_dt: Optional[datetime] = None
        for row in reader:
            if len(row) < 2:
                continue
            t_s: Optional[float] = None
            try:
                dt = datetime.fromisoformat(row[0])
                if first_timestamp_dt is None:
                    first_timestamp_dt = dt
                t_s = (dt - first_timestamp_dt).total_seconds()
            except Exception:
                try:
                    t_s = convert_to_seconds(row[0], time_unit)
                except Exception:
                    t_s = None
            if t_s is None:
                continue
            try:
                torque = float(row[1])
            except Exception:
                continue
            times_ms.append(t_s * 1000.0)
            torques.append(torque)
    return times_ms, torques


def plot_time_torque(csv_file: Path, time_unit: str, show: bool = False):
    t_ms, torque = read_time_ms_and_torque(csv_file, time_unit)
    if not t_ms:
        sys.stderr.write("No plottable data found.\n")
        return

    fig = plt.figure(figsize=(10, 6))
    plt.plot(t_ms, torque, linewidth=1.0)
    plt.xlabel("Time (ms)")
    plt.ylabel("Torque")
    plt.title("Time vs Torque")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    if show:
        plt.show()
    return fig

def main() -> None:
    parser = ArgumentParser(description="Plot time (ms) vs torque from the first two CSV columns.")
    default_csv = Path(__file__).with_name("data.csv")
    parser.add_argument("csv_path", nargs="?", default=str(default_csv), help="Path to CSV file (default: data.csv next to this script)")
    parser.add_argument("--time-unit", default="s", help="Unit of the first column if numeric (input): s, ms, us, ns, min, h (default: s)")
    args = parser.parse_args()

    csv_file = Path(args.csv_path)
    if not csv_file.exists():
        sys.stderr.write(f"CSV file not found: {csv_file}\n")
        sys.exit(1)

    plot_time_torque(csv_file, args.time_unit, show=True)


if __name__ == "__main__":
    main()


