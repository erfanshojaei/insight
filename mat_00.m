clc
clear all
close all
%%
% Read numeric CSV
data = readmatrix('data_mod.csv');  % Replace with your CSV file name

% Extract columns
col1 = data(:, 1);
col2 = data(:, 2);
%%
% Find peaks
[peaks, locs] = findpeaks(col2, col1 );  % 'peaks' are values, 'locs' are times
%%
figure
hold on
grid on
plot(col1,col2, 'o')

figure
hold on
grid on
plot(locs, peaks, 'ro'); % mark peaks


%%

%% Filtered Local Maxima and Minima Relative to Mean Envelope

%% Load your signal
% Example: replace 'your_signal.csv' with your CSV file containing one column
% signal = csvread('your_signal.csv'); % if CSV has only one column
% For demonstration, let's create a sample vibration signal:
t = col1;  % time vector
signal = col2;

%% Compute the mean envelope (oscillation center)
upper_env = envelope(signal, 50, 'peak');  % upper envelope
lower_env = envelope(signal, 50, 'peak');  
lower_env = -lower_env;                    % invert for lower envelope
mean_env = (upper_env + lower_env)/2;      % mean envelope

%% Find local maxima and minima
[all_max, locs_max] = findpeaks(signal);
[all_min, locs_min] = findpeaks(-signal);
all_min = -all_min;

%% Filter maxima above mean envelope and minima below mean envelope
max_above_mean = all_max(all_max > mean_env(locs_max));
locs_max_above = locs_max(all_max > mean_env(locs_max));

min_below_mean = all_min(all_min < mean_env(locs_min));
locs_min_below = locs_min(all_min < mean_env(locs_min));

%% Plot everything
figure('Color','w'); hold on; grid on;

plot(t, signal, 'Color', [0.6 0.8 1], 'LineWidth', 1.5); % Original signal in light blue
plot(t, mean_env, 'k', 'LineWidth', 2);                   % Mean envelope in black
plot(t(locs_max_above), max_above_mean, 'ro', 'MarkerFaceColor', 'r'); % Maxima above mean
plot(t(locs_min_below), min_below_mean, 'go', 'MarkerFaceColor', 'g'); % Minima below mean

xlabel('Time (s)');
ylabel('Amplitude');
title('Filtered Local Maxima and Minima Relative to Mean Envelope');
legend('Original Signal', 'Mean Envelope', 'Maxima Above Mean', 'Minima Below Mean');


 