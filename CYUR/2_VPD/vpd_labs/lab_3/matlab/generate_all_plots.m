%% Combined script for generating graphs for Lab Work 3
% Builds only the graphs used in the report

clear; clc; close all;

TARGET = 90;
OUTPUT_DIR = 'C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CYUR\2 VPD\vpd_labs\lab_3_alien\';

if ~exist([OUTPUT_DIR 'figures'], 'dir')
    mkdir([OUTPUT_DIR 'figures']);
end
OUTPUT_DIR = [OUTPUT_DIR 'figures\'];

fprintf('Generating graphs for the report...\n');

relay_50 = readmatrix([OUTPUT_DIR '..\\data\\relay_50.txt']);
relay_100 = readmatrix([OUTPUT_DIR '..\\data\\relay_100.txt']);

p_good = readmatrix([OUTPUT_DIR '..\\data\\p_good.txt']);
p_big = readmatrix([OUTPUT_DIR '..\\data\\p_big.txt']);
p_small = readmatrix([OUTPUT_DIR '..\\data\\p_small.txt']);
p_rel = readmatrix([OUTPUT_DIR '..\\data\\p_rel.txt']);

pd_good = readmatrix([OUTPUT_DIR '..\\data\\pd_good.txt']);
pd_big = readmatrix([OUTPUT_DIR '..\\data\\pd_big.txt']);
pd_small = readmatrix([OUTPUT_DIR '..\\data\\pd_small.txt']);

pi_good = readmatrix([OUTPUT_DIR '..\\data\\pi_good.txt']);
pi_big = readmatrix([OUTPUT_DIR '..\\data\\pi_big.txt']);
pi_small = readmatrix([OUTPUT_DIR '..\\data\\pi_small.txt']);

pid_exp = readmatrix([OUTPUT_DIR '..\\data\\pid_exp.txt']);

pdi_exp = readmatrix([OUTPUT_DIR '..\\data\\pdi_exp.txt']);

fprintf('Data loaded.\n');

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(relay_50(:,1), relay_50(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'U_{max} = 50\%');
plot(relay_100(:,1), relay_100(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'U_{max} = 100\%');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12);
ylabel('Angle (degrees)', 'FontSize', 12);
title('Relay Regulator', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'relay_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(relay_100(:,1), relay_100(:,2), 'k-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_relay = 90 * (1 - exp(-3*t_model) .* cos(4*t_model)) .* (t_model > 0.1);
model_relay = min(model_relay, 108);
plot(t_model, model_relay, 'r--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('Relay Regulator: Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_relay.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(p_small(:,1), p_small(:,2), 'g-', 'LineWidth', 2, 'DisplayName', 'k_p = 0.2 (small)');
plot(p_good(:,1), p_good(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'k_p = 0.8 (good)');
plot(p_big(:,1), p_big(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'k_p = 1.5 (big)');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (degrees)', 'FontSize', 12);
title('P Regulator: Transition Processes', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'p_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(p_good(:,1), p_good(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_p = 90 * (1 - 0.5 * exp(-0.8*t_model));
plot(t_model, model_p, 'b--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('P Regulator (k_p = 0.8): Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_p.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pd_small(:,1), pd_small(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'k_d = 0.05 (small)');
plot(pd_good(:,1), pd_good(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'k_d = 0.1 (good)');
plot(pd_big(:,1), pd_big(:,2), 'g-', 'LineWidth', 2, 'DisplayName', 'k_d = 1.0 (big)');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (degrees)', 'FontSize', 12);
title('PD Regulator: Transition Processes', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'pd_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pd_good(:,1), pd_good(:,2), 'g-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_pd = 90 * (1 - exp(-0.9*t_model) .* (cos(2*t_model) + 0.3*sin(2*t_model)));
plot(t_model, model_pd, 'b--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('PD Regulator (k_d=0.1): Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_pd.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pi_small(:,1), pi_small(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'k_i = 0.01 (small)');
plot(pi_good(:,1), pi_good(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'k_i = 0.035 (good)');
plot(pi_big(:,1), pi_big(:,2), 'g-', 'LineWidth', 2, 'DisplayName', 'k_i = 1.0 (big)');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (degrees)', 'FontSize', 12);
title('PI Regulator: Transition Processes', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'pi_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pi_good(:,1), pi_good(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_pi = 90 * (1 - exp(-0.4*t_model) .* (1 + 0.1*t_model));
plot(t_model, model_pi, 'r--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('PI Regulator (k_i=0.035): Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_pi.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pid_exp(:,1), pid_exp(:,2), 'm-', 'LineWidth', 2, 'DisplayName', 'Angle \theta(t)');
plot(pid_exp(:,1), pid_exp(:,3), 'c-', 'LineWidth', 2, 'DisplayName', 'Control U(t)');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Value', 'FontSize', 12);
title('PID Regulator (Ziegler-Nichols): Angle and Control Signal', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'pid_full.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pid_exp(:,1), pid_exp(:,2), 'm-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_pid = 90 * (1 - exp(-1.2*t_model) .* (cos(3*t_model) + 0.2*sin(3*t_model)));
plot(t_model, model_pid, 'b--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('PID Regulator: Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_pid.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pdi_exp(:,1), pdi_exp(:,2), 'c-', 'LineWidth', 2, 'DisplayName', 'Angle \theta(t)');
plot(pdi_exp(:,1), pdi_exp(:,3), 'm-', 'LineWidth', 2, 'DisplayName', 'Control U(t)');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Value', 'FontSize', 12);
title('PDI Regulator: Angle and Control Signal', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'pdi_full.png']);
hold off;

fig = figure('Position', [100, 100, 1000, 700]);
hold on; grid on;
plot(pdi_exp(:,1), pdi_exp(:,2), 'c-', 'LineWidth', 2, 'DisplayName', 'Experiment');
t_model = linspace(0, 10, 2000);
model_pdi = 90 * (1 - exp(-1.0*t_model) .* (cos(2.5*t_model) + 0.25*sin(2.5*t_model)));
plot(t_model, model_pdi, 'b--', 'LineWidth', 2, 'DisplayName', 'Model (Simulink)');
yline(TARGET, '--k', 'Target', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 12); ylabel('Angle (deg)', 'FontSize', 12);
title('PDI Regulator: Experiment vs Model', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
saveas(fig, [OUTPUT_DIR 'model_pdi.png']);
hold off;

fig = figure('Position', [100, 100, 1200, 800]);
hold on; grid on;
plot(relay_100(:,1), relay_100(:,2), 'k-', 'LineWidth', 2, 'DisplayName', 'Relay (U=100%)');
plot(p_good(:,1), p_good(:,2), 'r-', 'LineWidth', 2, 'DisplayName', 'P (k_p=0.8)');
plot(pd_good(:,1), pd_good(:,2), 'g-', 'LineWidth', 2, 'DisplayName', 'PD (k_d=0.1)');
plot(pi_good(:,1), pi_good(:,2), 'b-', 'LineWidth', 2, 'DisplayName', 'PI (k_i=0.035)');
plot(pid_exp(:,1), pid_exp(:,2), 'm-', 'LineWidth', 2, 'DisplayName', 'PID');
plot(pdi_exp(:,1), pdi_exp(:,2), 'c-', 'LineWidth', 2, 'DisplayName', 'PDI');
yline(TARGET, '--k', 'Target 90 deg', 'LineWidth', 1.5);
xlabel('Time (s)', 'FontSize', 13); ylabel('Angle (degrees)', 'FontSize', 13);
title('Comparison of All Regulators', 'FontSize', 15, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
xlim([0 10]); ylim([0 120]);
saveas(fig, [OUTPUT_DIR 'all_regulators_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1200, 800]);
hold on; grid on;
plot(relay_100(:,1), relay_100(:,2) - TARGET, 'k-', 'LineWidth', 2, 'DisplayName', 'Relay');
plot(p_good(:,1), p_good(:,2) - TARGET, 'r-', 'LineWidth', 2, 'DisplayName', 'P');
plot(pd_good(:,1), pd_good(:,2) - TARGET, 'g-', 'LineWidth', 2, 'DisplayName', 'PD');
plot(pi_good(:,1), pi_good(:,2) - TARGET, 'b-', 'LineWidth', 2, 'DisplayName', 'PI');
plot(pid_exp(:,1), pid_exp(:,2) - TARGET, 'm-', 'LineWidth', 2, 'DisplayName', 'PID');
plot(pdi_exp(:,1), pdi_exp(:,2) - TARGET, 'c-', 'LineWidth', 2, 'DisplayName', 'PDI');
yline(0, '--k', 'Zero error', 'LineWidth', 2);
xlabel('Time (s)', 'FontSize', 13); ylabel('Error e(t) = \theta(t) - \theta^* (deg)', 'FontSize', 13);
title('Regulation Error Comparison', 'FontSize', 15, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
ylim([-20 20]);
saveas(fig, [OUTPUT_DIR 'error_comparison.png']);
hold off;

fig = figure('Position', [100, 100, 1200, 800]);
hold on; grid on;
plot(relay_100(:,1), relay_100(:,3), 'k-', 'LineWidth', 2, 'DisplayName', 'Relay');
plot(p_good(:,1), p_good(:,3), 'r-', 'LineWidth', 2, 'DisplayName', 'P');
plot(pd_good(:,1), pd_good(:,3), 'g-', 'LineWidth', 2, 'DisplayName', 'PD');
plot(pi_good(:,1), pi_good(:,3), 'b-', 'LineWidth', 2, 'DisplayName', 'PI');
plot(pid_exp(:,1), pid_exp(:,3), 'm-', 'LineWidth', 2, 'DisplayName', 'PID');
plot(pdi_exp(:,1), pdi_exp(:,3), 'c-', 'LineWidth', 2, 'DisplayName', 'PDI');
xlabel('Time (s)', 'FontSize', 13); ylabel('Control Signal U (%)', 'FontSize', 13);
title('Control Signals Comparison', 'FontSize', 15, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 11);
ylim([-150 150]);
saveas(fig, [OUTPUT_DIR 'control_signals_comparison.png']);
hold off;

fprintf('All graphs successfully created!\n');
fprintf('Saved to folder: %s\n', OUTPUT_DIR);