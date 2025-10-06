import csv
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from plot_time_torque import plot_time_torque
from typing import Optional
from plot_time_torque import read_time_ms_and_torque
from envelope_analys import envelope_analysis


def convert_to_seconds(value_str: str, time_unit: str) -> float:
    value = float(value_str)
    unit_to_seconds = {
        "s": 1.0,
        "sec": 1.0,
        "ms": 1e-3,
        "us": 1e-6,
        "µs": 1e-6,
        "ns": 1e-9,
        "m": 60.0,  # minutes
        "min": 60.0,
        "h": 3600.0,
        "hr": 3600.0,
        "hrs": 3600.0,
    }
    factor = unit_to_seconds.get(time_unit.lower())
    if factor is None:
        raise ValueError(f"Unsupported time unit: {time_unit}")
    return value * factor


def print_first_two_columns(
    csv_path: Path,
    time_unit: str,
    time_precision: int,
    torque_precision: int,
) -> None:
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        first_timestamp_dt: Optional[datetime] = None
        for row in reader:
            if len(row) < 2:
                continue
            time_seconds: Optional[float] = None
            # Try timestamp first
            try:
                dt = datetime.fromisoformat(row[0])
                if first_timestamp_dt is None:
                    first_timestamp_dt = dt
                time_seconds = (dt - first_timestamp_dt).total_seconds()
            except Exception:
                # Fallback to numeric value with unit
                try:
                    time_seconds = convert_to_seconds(row[0], time_unit)
                except Exception:
                    time_seconds = None

            if time_seconds is None:
                continue
            try:
                torque_value = float(row[1])
            except Exception:
                continue
            time_ms = time_seconds * 1000.0
            if time_precision >= 0 and torque_precision >= 0:
                print(f"{time_ms:.{time_precision}f}\t{torque_value:.{torque_precision}f}")
            elif time_precision >= 0 and torque_precision < 0:
                print(f"{time_ms:.{time_precision}f}", torque_value, sep="\t")
            elif time_precision < 0 and torque_precision >= 0:
                print(time_ms, f"{torque_value:.{torque_precision}f}", sep="\t")
            else:
                print(time_ms, torque_value, sep="\t")


def parse_args():
    parser = ArgumentParser(description="Print time (in milliseconds) and torque from the first two CSV columns. If the first column is a timestamp, outputs milliseconds since the first timestamp.")
    default_csv = Path(__file__).with_name("data.csv")
    parser.add_argument("csv_path", nargs="?", default=str(default_csv), help="Path to CSV file (default: data.csv next to this script)")
    parser.add_argument("--time-unit", default="s", help="Unit of the first column if numeric (input): s, ms, us, ns, min, h (default: s)")
    parser.add_argument("--precision", type=int, default=None, help="If set, decimal places for both time(ms) and torque; use -1 for raw")
    parser.add_argument("--time-precision", type=int, default=3, help="Decimal places for time in ms; use -1 for raw (default: 3)")
    parser.add_argument("--torque-precision", type=int, default=18, help="Decimal places for torque; use -1 for raw (default: 18)")
    parser.add_argument("--min-peak-distance", type=int, default=20, help="Minimum distance between peaks (in samples) for envelope analysis (default: 50)")
    return parser.parse_args()


def main(args) -> None:
    csv_file = Path(args.csv_path)
    if not csv_file.exists():
        sys.stderr.write(f"CSV file not found: {csv_file}\n")
        sys.exit(1)

    # Global override if --precision is provided
    if args.precision is not None:
        time_precision = args.precision
        torque_precision = args.precision
    else:
        time_precision = args.time_precision
        torque_precision = args.torque_precision

    print_first_two_columns(csv_file, args.time_unit, time_precision, torque_precision)

    # Write data_mod.csv with time(ms) and torque at 20 decimal places for torque
    try:
        t_ms, torques = read_time_ms_and_torque(csv_file, args.time_unit)
        out_path = csv_file.with_name("data_mod.csv")
        with out_path.open("w", encoding="utf-8", newline="") as outf:
            writer = csv.writer(outf)
            writer.writerow(["time_ms", "torque"])
            for t, q in zip(t_ms, torques):
                writer.writerow([f"{t:.3f}", f"{q:.20f}"])
    except Exception as e:
        sys.stderr.write(f"Failed to write data_mod.csv: {e}\n")



if __name__ == "__main__":
    args = parse_args()
    main(args)
    fig1 = plot_time_torque(Path(args.csv_path), args.time_unit, show=False)

    # Envelope/extreme analysis: use function that accepts time and torque
    try:
        t_ms, torques = read_time_ms_and_torque(Path(args.csv_path), args.time_unit)
        fig2 = envelope_analysis(t_ms, torques, min_peak_distance=args.min_peak_distance, show=False)
    except Exception as e:
        sys.stderr.write(f"Envelope analysis failed: {e}\n")

    # Show all figures together at the end
    try:
        import matplotlib.pyplot as plt
        plt.show()
    except Exception:
        pass