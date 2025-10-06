clear all
close all
clc
%%
% MATLAB script for Envelope and Local Extremes Analysis
% Make sure 'data_mod.csv' is in the current MATLAB folder.

% --- 1. Load Data ---
data = readtable('data_mod.csv');
time_ms = data.time_ms;
torque = data.torque;

% --- 2. Find Local Extremes (Peaks and Troughs) ---
% NOTE: 'MinProminence' is not supported in your MATLAB version.
% We use 'MinPeakDistance' (e.g., 50 samples) as an alternative filter
% to capture the main envelope oscillations and suppress high-frequency noise.
min_peak_distance = 50; % Corresponds to 50 ms

% Find peaks (local maxima)
[peak_torques, peaks_indices] = findpeaks(torque, 'MinPeakDistance', min_peak_distance);
peak_times = time_ms(peaks_indices);

% Find troughs (local minima) by finding peaks in the inverted signal
[trough_torques_inverted, troughs_indices] = findpeaks(-torque, 'MinPeakDistance', min_peak_distance);
trough_torques = torque(troughs_indices); % Original torque values for the troughs
trough_times = time_ms(troughs_indices);

% --- 3. Interpolate Envelopes and Calculate Mean Envelope ---

% Use cubic spline interpolation (pchip for smoothness)
f_upper = griddedInterpolant(peak_times, peak_torques, 'pchip', 'pchip');
f_lower = griddedInterpolant(trough_times, trough_torques, 'pchip', 'pchip');

interp_upper_envelope = f_upper(time_ms);
interp_lower_envelope = f_lower(time_ms);

% Calculate the Mean Envelope Signal
mean_envelope_signal = (interp_upper_envelope + interp_lower_envelope) / 2;

% --- 4. Filter Local Extremes Relative to Mean Envelope ---

% Get Mean Envelope values at the exact Peak and Trough times
mean_at_peaks = mean_envelope_signal(peaks_indices);
mean_at_troughs = mean_envelope_signal(troughs_indices);

% Filter Maxima: keep only peaks where torque > mean envelope at that point
filter_peaks = peak_torques > mean_at_peaks;
filtered_peak_times = peak_times(filter_peaks);
filtered_peak_torques = peak_torques(filter_peaks);

% Filter Minima: keep only troughs where torque < mean envelope at that point
filter_troughs = trough_torques < mean_at_troughs;
filtered_trough_times = trough_times(filter_troughs);
filtered_trough_torques = trough_torques(filter_troughs);

% --- 5. Plotting ---
figure;
hold on;
title('Filtered Local Maxima and Minima Relative to Mean Envelope (MATLAB)');
xlabel('Time (ms)');
ylabel('Torque');
grid on;

% Plot the original signal (faint)
plot(time_ms, torque, 'Color', [0 0 1 0.3], 'LineWidth', 1, 'DisplayName', 'Original Signal (Torque)');

% Plot the Mean Envelope Signal (thick black line)
plot(time_ms, mean_envelope_signal, 'k-', 'LineWidth', 3, 'DisplayName', 'Mean Envelope Signal');

% Plot the filtered maximas (above mean)
scatter(filtered_peak_times, filtered_peak_torques, 50, 'r', 'filled', 'DisplayName', 'Maximas Above Mean Envelope');

% Plot the filtered minimas (below mean)
scatter(filtered_trough_times, filtered_trough_torques, 50, 'g', 'filled', 'DisplayName', 'Minimas Below Mean Envelope');

legend('Location', 'best');
hold off;