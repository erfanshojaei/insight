import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import PchipInterpolator

from plot_time_torque import read_time_ms_and_torque


def parse_args():
    parser = ArgumentParser(description="Envelope analysis: mean envelope and filtered extremes plot")
    default_csv = Path(__file__).with_name("data.csv")
    parser.add_argument("csv_path", nargs="?", default=str(default_csv), help="Path to CSV file (default: data.csv next to this script)")
    parser.add_argument("--time-unit", default="s", help="Unit of the first column if numeric (input): s, ms, us, ns, min, h (default: s)")
    parser.add_argument("--min-peak-distance", type=int, default=50, help="Minimum distance between peaks (in samples). Default: 50")
    return parser.parse_args()


def envelope_analysis(time_ms, torque, min_peak_distance: int = 50, show: bool = False):
    """Plot mean envelope and filtered extremes given time (ms) and torque arrays."""
    time_ms = np.asarray(time_ms)
    torque = np.asarray(torque)

    # --- 2. Find Local Extremes (Peaks and Troughs) ---
    peaks_indices, _ = find_peaks(torque, distance=min_peak_distance)
    peak_torques = torque[peaks_indices]
    peak_times = time_ms[peaks_indices]

    troughs_indices, _ = find_peaks(-torque, distance=min_peak_distance)
    trough_torques = torque[troughs_indices]
    trough_times = time_ms[troughs_indices]

    if peak_times.size < 2 or trough_times.size < 2:
        sys.stderr.write("Not enough peaks/troughs to interpolate envelopes. Try lowering min_peak_distance.\n")
        return

    # --- 3. Interpolate Envelopes and Calculate Mean Envelope ---
    f_upper = PchipInterpolator(peak_times, peak_torques)
    f_lower = PchipInterpolator(trough_times, trough_torques)

    interp_upper_envelope = f_upper(time_ms)
    interp_lower_envelope = f_lower(time_ms)

    mean_envelope_signal = (interp_upper_envelope + interp_lower_envelope) / 2

    # --- 4. Filter Local Extremes Relative to Mean Envelope ---
    mean_at_peaks = mean_envelope_signal[peaks_indices]
    mean_at_troughs = mean_envelope_signal[troughs_indices]

    filter_peaks = peak_torques > mean_at_peaks
    filtered_peak_times = peak_times[filter_peaks]
    filtered_peak_torques = peak_torques[filter_peaks]

    filter_troughs = trough_torques < mean_at_troughs
    filtered_trough_times = trough_times[filter_troughs]
    filtered_trough_torques = trough_torques[filter_troughs]

    # --- 5. Plotting ---
    fig = plt.figure(figsize=(10, 6))
    plt.plot(time_ms, mean_envelope_signal, 'k', linewidth=2, label='Mean Envelope Signal')
    plt.plot(filtered_peak_times, filtered_peak_torques, 'r', linewidth=1, label='Connected Maximas (Upper)')
    plt.plot(filtered_trough_times, filtered_trough_torques, 'g', linewidth=1, label='Connected Minimas (Lower)')
    #plt.scatter(filtered_peak_times, filtered_peak_torques, color='r', s=50)
    #plt.scatter(filtered_trough_times, filtered_trough_torques, color='g', s=50)
    plt.xlabel('Time (ms)')
    plt.ylabel('Torque')
    plt.title('Mean Envelope and Connected Filtered Extremes (Lines)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def main() -> None:
    args = parse_args()
    csv_file = Path(args.csv_path)
    if not csv_file.exists():
        sys.stderr.write(f"CSV file not found: {csv_file}\n")
        sys.exit(1)

    # --- 1. Load your data ---
    # Use helper to read first two columns as time in ms and torque
    time_ms_list, torque_list = read_time_ms_and_torque(csv_file, args.time_unit)
    if not time_ms_list:
        sys.stderr.write("No data found to analyze.\n")
        sys.exit(2)

    time_ms = np.asarray(time_ms_list)
    torque = np.asarray(torque_list)

    # Use the reusable function with CLI-provided min-peak-distance
    envelope_analysis(time_ms, torque, min_peak_distance=args.min_peak_distance)


if __name__ == "__main__":
    main()


