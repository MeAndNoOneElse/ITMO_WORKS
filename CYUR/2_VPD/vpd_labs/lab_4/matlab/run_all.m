clear; clc; close all;
GRAPHICS = fullfile('..', 'graphics');
DATA = fullfile('..', 'data');

if ~exist(GRAPHICS, 'dir')
    mkdir(GRAPHICS);
end

if ~exist(DATA, 'dir')
    error('Папка ../data не найдена');
end

r    = 0.029;
B    = 0.120;
K_s  = 0.5;
K_r  = 2;
K1   = 0.5;
K2   = 1;
MAX_U = 50.0;

assignin('base', 'r',     r);
assignin('base', 'B',     B);
assignin('base', 'K_s',   K_s);
assignin('base', 'K_r',   K_r);
assignin('base', 'K1',    K1);
assignin('base', 'K2',    K2);
assignin('base', 'MAX_U', MAX_U);

fprintf('[1/6] Параметры заданы\n');

%% ============================================================
fprintf('[2/6] Создание p_regulator.slx...\n');

%% =========================
% СОЗДАНИЕ МОДЕЛИ P-РЕГУЛЯТОРА
%% =========================

mdl = 'p_regulator';

% Если модель уже открыта — закрыть без сохранения
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

% Если файл модели уже существует — удалить, чтобы создать заново
if exist([mdl '.slx'], 'file')
    delete([mdl '.slx']);
end

% Создать новую пустую модель и открыть её
new_system(mdl);
open_system(mdl);

% Настройки моделирования:
% время, решатель, переменный шаг, максимальный шаг и точность
set_param(mdl, ...
    'StopTime',  '25', ...
    'Solver',    'ode45', ...
    'SolverType','Variable-step', ...
    'MaxStep',   '0.03', ...
    'RelTol',    '1e-4');

%% Блоки цели
% goal_x, goal_y — координаты целевой точки
add_block('simulink/Sources/Constant', [mdl '/goal_x'], ...
    'Position', [40 120 90 150], 'Value', '1');
add_block('simulink/Sources/Constant', [mdl '/goal_y'], ...
    'Position', [40 180 90 210], 'Value', '0');

%% Вычисление ошибок по координатам
% sub_x = goal_x - x
% sub_y = goal_y - y
add_block('simulink/Math Operations/Add', [mdl '/sub_x'], ...
    'Position', [140 120 180 150], 'Inputs', '+-');
add_block('simulink/Math Operations/Add', [mdl '/sub_y'], ...
    'Position', [140 180 180 210], 'Inputs', '+-');

%% Вычисление расстояния до цели rho
% sq_x = (goal_x - x)^2
% sq_y = (goal_y - y)^2
add_block('simulink/Math Operations/Math Function', [mdl '/sq_x'], ...
    'Position', [230 110 270 150], 'Operator', 'square');
add_block('simulink/Math Operations/Math Function', [mdl '/sq_y'], ...
    'Position', [230 170 270 210], 'Operator', 'square');

% sum_sq = sq_x + sq_y
% rho = sqrt(sum_sq)
add_block('simulink/Math Operations/Add', [mdl '/sum_sq'], ...
    'Position', [310 135 350 185], 'Inputs', '++');
add_block('simulink/Math Operations/Sqrt', [mdl '/rho'], ...
    'Position', [390 140 430 180]);

%% Вычисление азимута и угловой ошибки
% atan2_blk = psi = atan2(goal_y - y, goal_x - x)
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/atan2_blk'], ...
    'Position', [230 250 280 290], 'Operator', 'atan2');

% sub_alpha = psi - theta
add_block('simulink/Math Operations/Add', [mdl '/sub_alpha'], ...
    'Position', [330 250 380 290], 'Inputs', '+-');

% wrap_angle — ограничивает угол в диапазоне [-pi, pi]
add_block('simulink/User-Defined Functions/MATLAB Function', [mdl '/wrap_angle'], ...
    'Position', [430 240 530 300]);

%% Усиление ошибок регулятором
% Ks_gain = K_s * rho
% Kr_gain = K_r * alpha
add_block('simulink/Math Operations/Gain', [mdl '/Ks_gain'], ...
    'Position', [500 130 540 170], 'Gain', 'K_s');
add_block('simulink/Math Operations/Gain', [mdl '/Kr_gain'], ...
    'Position', [560 245 600 285], 'Gain', 'K_r');

%% Формирование сигналов на левый и правый мотор
% Uleft  = Us - Ur
% Uright = Us + Ur
add_block('simulink/Math Operations/Add', [mdl '/Uleft_sum'], ...
    'Position', [650 130 690 170], 'Inputs', '+-');
add_block('simulink/Math Operations/Add', [mdl '/Uright_sum'], ...
    'Position', [650 220 690 260], 'Inputs', '++');

%% Ограничение управляющих сигналов
% Saturation ограничивает напряжение в диапазоне [-MAX_U, MAX_U]
add_block('simulink/Discontinuities/Saturation', [mdl '/sat_left'], ...
    'Position', [740 130 780 170], 'UpperLimit', 'MAX_U', 'LowerLimit', '-MAX_U');
add_block('simulink/Discontinuities/Saturation', [mdl '/sat_right'], ...
    'Position', [740 220 780 260], 'UpperLimit', 'MAX_U', 'LowerLimit', '-MAX_U');

%% Переход к угловым скоростям колёс
% gain_wl = Uleft / r
% gain_wr = Uright / r
add_block('simulink/Math Operations/Gain', [mdl '/gain_wl'], ...
    'Position', [830 130 870 170], 'Gain', '1/r');
add_block('simulink/Math Operations/Gain', [mdl '/gain_wr'], ...
    'Position', [830 220 870 260], 'Gain', '1/r');

%% Вычисление линейной и угловой скорости робота
% v = r/2 * (wl + wr)
add_block('simulink/Math Operations/Add', [mdl '/v_sum'], ...
    'Position', [930 150 970 190], 'Inputs', '++');
add_block('simulink/Math Operations/Gain', [mdl '/v_gain'], ...
    'Position', [1010 150 1050 190], 'Gain', 'r/2');

% w = r/B * (wr - wl)
add_block('simulink/Math Operations/Add', [mdl '/w_sum'], ...
    'Position', [930 230 970 270], 'Inputs', '+-');
add_block('simulink/Math Operations/Gain', [mdl '/w_gain'], ...
    'Position', [1010 230 1050 270], 'Gain', 'r/B');

%% Интегрирование угла
% int_theta даёт текущую ориентацию theta
add_block('simulink/Continuous/Integrator', [mdl '/int_theta'], ...
    'Position', [1100 230 1140 270], 'InitialCondition', '0');

%% Проекция скорости на оси X и Y
% cos_th = cos(theta)
% sin_th = sin(theta)
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/cos_th'], ...
    'Position', [1200 140 1240 170], 'Operator', 'cos');
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/sin_th'], ...
    'Position', [1200 200 1240 230], 'Operator', 'sin');

% vcos = v * cos(theta) = dx/dt
% vsin = v * sin(theta) = dy/dt
add_block('simulink/Math Operations/Product', [mdl '/vcos'], ...
    'Position', [1290 140 1330 180]);
add_block('simulink/Math Operations/Product', [mdl '/vsin'], ...
    'Position', [1290 200 1330 240]);

%% Интегрирование координат
% int_x даёт x
% int_y даёт y
add_block('simulink/Continuous/Integrator', [mdl '/int_x'], ...
    'Position', [1380 140 1420 180], 'InitialCondition', '0');
add_block('simulink/Continuous/Integrator', [mdl '/int_y'], ...
    'Position', [1380 200 1420 240], 'InitialCondition', '0');

%% Вывод результатов в Workspace
% out_x, out_y, out_theta сохраняют траекторию модели
add_block('simulink/Sinks/To Workspace', [mdl '/out_x'], ...
    'Position', [1470 140 1570 180], ...
    'VariableName', 'x', 'SaveFormat', 'Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/out_y'], ...
    'Position', [1470 200 1570 240], ...
    'VariableName', 'y', 'SaveFormat', 'Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/out_theta'], ...
    'Position', [1170 300 1270 340], ...
    'VariableName', 'theta', 'SaveFormat', 'Timeseries');

%% Код для wrap_angle
% Нормализация угла в диапазон [-pi, pi]
wrap_code = sprintf([ ...
'function y = fcn(u)\n' ...
'y = u;\n' ...
'while y > pi\n' ...
'  y = y - 2*pi;\n' ...
'end\n' ...
'while y < -pi\n' ...
'  y = y + 2*pi;\n' ...
'end\n']);

rt = sfroot;
em = rt.find('-isa', 'Stateflow.EMChart', 'Path', [mdl '/wrap_angle']);
if ~isempty(em)
    em.Script = wrap_code;
end

%% Соединение блоков
% подача цели на вычисление ошибок
add_line(mdl, 'goal_x/1', 'sub_x/1', 'autorouting', 'smart');
add_line(mdl, 'goal_y/1', 'sub_y/1', 'autorouting', 'smart');

% вычисление rho
add_line(mdl, 'sub_x/1', 'sq_x/1', 'autorouting', 'smart');
add_line(mdl, 'sub_y/1', 'sq_y/1', 'autorouting', 'smart');
add_line(mdl, 'sq_x/1', 'sum_sq/1', 'autorouting', 'smart');
add_line(mdl, 'sq_y/1', 'sum_sq/2', 'autorouting', 'smart');
add_line(mdl, 'sum_sq/1', 'rho/1', 'autorouting', 'smart');

% вычисление psi и alpha
add_line(mdl, 'sub_y/1', 'atan2_blk/1', 'autorouting', 'smart');
add_line(mdl, 'sub_x/1', 'atan2_blk/2', 'autorouting', 'smart');
add_line(mdl, 'atan2_blk/1', 'sub_alpha/1', 'autorouting', 'smart');
add_line(mdl, 'sub_alpha/1', 'wrap_angle/1', 'autorouting', 'smart');

% регулятор
add_line(mdl, 'rho/1', 'Ks_gain/1', 'autorouting', 'smart');
add_line(mdl, 'wrap_angle/1', 'Kr_gain/1', 'autorouting', 'smart');

% формирование напряжений на моторы
add_line(mdl, 'Ks_gain/1', 'Uleft_sum/1', 'autorouting', 'smart');
add_line(mdl, 'Kr_gain/1', 'Uleft_sum/2', 'autorouting', 'smart');
add_line(mdl, 'Ks_gain/1', 'Uright_sum/1', 'autorouting', 'smart');
add_line(mdl, 'Kr_gain/1', 'Uright_sum/2', 'autorouting', 'smart');

% насыщение
add_line(mdl, 'Uleft_sum/1', 'sat_left/1', 'autorouting', 'smart');
add_line(mdl, 'Uright_sum/1', 'sat_right/1', 'autorouting', 'smart');

% переход к скоростям колёс
add_line(mdl, 'sat_left/1', 'gain_wl/1', 'autorouting', 'smart');
add_line(mdl, 'sat_right/1', 'gain_wr/1', 'autorouting', 'smart');

% вычисление v и w
add_line(mdl, 'gain_wl/1', 'v_sum/1', 'autorouting', 'smart');
add_line(mdl, 'gain_wr/1', 'v_sum/2', 'autorouting', 'smart');
add_line(mdl, 'gain_wr/1', 'w_sum/1', 'autorouting', 'smart');
add_line(mdl, 'gain_wl/1', 'w_sum/2', 'autorouting', 'smart');
add_line(mdl, 'v_sum/1', 'v_gain/1', 'autorouting', 'smart');
add_line(mdl, 'w_sum/1', 'w_gain/1', 'autorouting', 'smart');

% интегрирование theta и обратная связь в alpha
add_line(mdl, 'w_gain/1', 'int_theta/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'cos_th/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'sin_th/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'sub_alpha/2', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'out_theta/1', 'autorouting', 'smart');

% вычисление dx/dt и dy/dt
add_line(mdl, 'v_gain/1', 'vcos/1', 'autorouting', 'smart');
add_line(mdl, 'cos_th/1', 'vcos/2', 'autorouting', 'smart');
add_line(mdl, 'v_gain/1', 'vsin/1', 'autorouting', 'smart');
add_line(mdl, 'sin_th/1', 'vsin/2', 'autorouting', 'smart');

% интегрирование координат
add_line(mdl, 'vcos/1', 'int_x/1', 'autorouting', 'smart');
add_line(mdl, 'vsin/1', 'int_y/1', 'autorouting', 'smart');

% обратная связь координат в ошибку положения
add_line(mdl, 'int_x/1', 'sub_x/2', 'autorouting', 'smart');
add_line(mdl, 'int_y/1', 'sub_y/2', 'autorouting', 'smart');

% вывод в Workspace
add_line(mdl, 'int_x/1', 'out_x/1', 'autorouting', 'smart');
add_line(mdl, 'int_y/1', 'out_y/1', 'autorouting', 'smart');

% сохранить модель
save_system(mdl, [mdl '.slx']);
fprintf('OK: p_regulator.slx создан\n');


%% =========================
% СОЗДАНИЕ МОДЕЛИ ТАНГЕНЦИАЛЬНОГО РЕГУЛЯТОРА
%% =========================

fprintf('[3/6] Создание tangential_regulator.slx...\n');

mdl = 'tangential_regulator';

% Закрыть, если уже была открыта
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

% Удалить старый файл модели
if exist([mdl '.slx'], 'file')
    delete([mdl '.slx']);
end

% Создать новую модель
new_system(mdl);
open_system(mdl);

% Настройки моделирования
set_param(mdl, ...
    'StopTime',  '25', ...
    'Solver',    'ode45', ...
    'SolverType','Variable-step', ...
    'MaxStep',   '0.03', ...
    'RelTol',    '1e-4');

%% Координаты цели
add_block('simulink/Sources/Constant', [mdl '/goal_x'], ...
    'Position', [40 120 90 150], 'Value', '1');
add_block('simulink/Sources/Constant', [mdl '/goal_y'], ...
    'Position', [40 180 90 210], 'Value', '0');

%% Ошибка по координатам
add_block('simulink/Math Operations/Add', [mdl '/sub_x'], ...
    'Position', [140 120 180 150], 'Inputs', '+-');
add_block('simulink/Math Operations/Add', [mdl '/sub_y'], ...
    'Position', [140 180 180 210], 'Inputs', '+-');

%% Расстояние до цели rho
add_block('simulink/Math Operations/Math Function', [mdl '/sq_x'], ...
    'Position', [230 110 270 150], 'Operator', 'square');
add_block('simulink/Math Operations/Math Function', [mdl '/sq_y'], ...
    'Position', [230 170 270 210], 'Operator', 'square');
add_block('simulink/Math Operations/Add', [mdl '/sum_sq'], ...
    'Position', [310 135 350 185], 'Inputs', '++');
add_block('simulink/Math Operations/Sqrt', [mdl '/rho'], ...
    'Position', [390 140 430 180]);

%% Азимут и угловая ошибка
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/atan2_blk'], ...
    'Position', [230 250 280 290], 'Operator', 'atan2');
add_block('simulink/Math Operations/Add', [mdl '/sub_alpha'], ...
    'Position', [330 250 380 290], 'Inputs', '+-');

% Нормализация угла
add_block('simulink/User-Defined Functions/MATLAB Function', [mdl '/wrap_angle'], ...
    'Position', [430 240 530 300]);

%% Тангенциальный регулятор
% tan_ctrl принимает rho и alpha, выдаёт Uleft и Uright
add_block('simulink/User-Defined Functions/MATLAB Function', [mdl '/tan_ctrl'], ...
    'Position', [570 170 760 290]);

%% Скорости колёс
add_block('simulink/Math Operations/Gain', [mdl '/gain_wl'], ...
    'Position', [890 170 930 210], 'Gain', '1/r');
add_block('simulink/Math Operations/Gain', [mdl '/gain_wr'], ...
    'Position', [890 240 930 280], 'Gain', '1/r');

%% Линейная и угловая скорость робота
add_block('simulink/Math Operations/Add', [mdl '/v_sum'], ...
    'Position', [980 180 1020 220], 'Inputs', '++');
add_block('simulink/Math Operations/Gain', [mdl '/v_gain'], ...
    'Position', [1060 180 1100 220], 'Gain', 'r/2');

add_block('simulink/Math Operations/Add', [mdl '/w_sum'], ...
    'Position', [980 250 1020 290], 'Inputs', '+-');
add_block('simulink/Math Operations/Gain', [mdl '/w_gain'], ...
    'Position', [1060 250 1100 290], 'Gain', 'r/B');

%% Интегратор угла theta
add_block('simulink/Continuous/Integrator', [mdl '/int_theta'], ...
    'Position', [1150 250 1190 290], 'InitialCondition', '0');

%% cos(theta), sin(theta)
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/cos_th'], ...
    'Position', [1250 170 1290 200], 'Operator', 'cos');
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/sin_th'], ...
    'Position', [1250 230 1290 260], 'Operator', 'sin');

%% dx/dt и dy/dt
add_block('simulink/Math Operations/Product', [mdl '/vcos'], ...
    'Position', [1340 170 1380 210]);
add_block('simulink/Math Operations/Product', [mdl '/vsin'], ...
    'Position', [1340 230 1380 270]);

%% Интеграторы координат
add_block('simulink/Continuous/Integrator', [mdl '/int_x'], ...
    'Position', [1430 170 1470 210], 'InitialCondition', '0');
add_block('simulink/Continuous/Integrator', [mdl '/int_y'], ...
    'Position', [1430 230 1470 270], 'InitialCondition', '0');

%% Сохранение результатов
add_block('simulink/Sinks/To Workspace', [mdl '/out_x'], ...
    'Position', [1520 170 1620 210], ...
    'VariableName', 'x', 'SaveFormat', 'Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/out_y'], ...
    'Position', [1520 230 1620 270], ...
    'VariableName', 'y', 'SaveFormat', 'Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/out_theta'], ...
    'Position', [1220 310 1320 350], ...
    'VariableName', 'theta', 'SaveFormat', 'Timeseries');

%% Код wrap_angle
wrap_code = sprintf([ ...
'function y = fcn(u)\n' ...
'y = u;\n' ...
'while y > pi\n' ...
'  y = y - 2*pi;\n' ...
'end\n' ...
'while y < -pi\n' ...
'  y = y + 2*pi;\n' ...
'end\n']);

%% Код tan_ctrl
% v — движение вперёд
% w — поворот
% затем формируются сигналы на левый и правый мотор
tan_code = sprintf([ ...
'function [Uleft,Uright] = fcn(rho,alpha)\n' ...
'K1 = 0.5;\n' ...
'K2 = 1.0;\n' ...
'MAX_U = 50.0;\n' ...
'v = K1 * rho * cos(alpha);\n' ...
'w = K1 * cos(alpha) * sin(alpha) + K2 * alpha;\n' ...
'Uleft = v - w;\n' ...
'Uright = v + w;\n' ...
'if Uleft > MAX_U\n' ...
'  Uleft = MAX_U;\n' ...
'end\n' ...
'if Uleft < -MAX_U\n' ...
'  Uleft = -MAX_U;\n' ...
'end\n' ...
'if Uright > MAX_U\n' ...
'  Uright = MAX_U;\n' ...
'end\n' ...
'if Uright < -MAX_U\n' ...
'  Uright = -MAX_U;\n' ...
'end\n']);

% Записать код в MATLAB Function блоки
rt = sfroot;
em = rt.find('-isa', 'Stateflow.EMChart', 'Path', [mdl '/wrap_angle']);
if ~isempty(em)
    em.Script = wrap_code;
end
em = rt.find('-isa', 'Stateflow.EMChart', 'Path', [mdl '/tan_ctrl']);
if ~isempty(em)
    em.Script = tan_code;
end

%% Соединения блоков
add_line(mdl, 'goal_x/1', 'sub_x/1', 'autorouting', 'smart');
add_line(mdl, 'goal_y/1', 'sub_y/1', 'autorouting', 'smart');

add_line(mdl, 'sub_x/1', 'sq_x/1', 'autorouting', 'smart');
add_line(mdl, 'sub_y/1', 'sq_y/1', 'autorouting', 'smart');
add_line(mdl, 'sq_x/1', 'sum_sq/1', 'autorouting', 'smart');
add_line(mdl, 'sq_y/1', 'sum_sq/2', 'autorouting', 'smart');
add_line(mdl, 'sum_sq/1', 'rho/1', 'autorouting', 'smart');

add_line(mdl, 'sub_y/1', 'atan2_blk/1', 'autorouting', 'smart');
add_line(mdl, 'sub_x/1', 'atan2_blk/2', 'autorouting', 'smart');
add_line(mdl, 'atan2_blk/1', 'sub_alpha/1', 'autorouting', 'smart');
add_line(mdl, 'sub_alpha/1', 'wrap_angle/1', 'autorouting', 'smart');

add_line(mdl, 'rho/1', 'tan_ctrl/1', 'autorouting', 'smart');
add_line(mdl, 'wrap_angle/1', 'tan_ctrl/2', 'autorouting', 'smart');

add_line(mdl, 'tan_ctrl/1', 'gain_wl/1', 'autorouting', 'smart');
add_line(mdl, 'tan_ctrl/2', 'gain_wr/1', 'autorouting', 'smart');

add_line(mdl, 'gain_wl/1', 'v_sum/1', 'autorouting', 'smart');
add_line(mdl, 'gain_wr/1', 'v_sum/2', 'autorouting', 'smart');

add_line(mdl, 'gain_wr/1', 'w_sum/1', 'autorouting', 'smart');
add_line(mdl, 'gain_wl/1', 'w_sum/2', 'autorouting', 'smart');

add_line(mdl, 'v_sum/1', 'v_gain/1', 'autorouting', 'smart');
add_line(mdl, 'w_sum/1', 'w_gain/1', 'autorouting', 'smart');

add_line(mdl, 'w_gain/1', 'int_theta/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'cos_th/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'sin_th/1', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'sub_alpha/2', 'autorouting', 'smart');
add_line(mdl, 'int_theta/1', 'out_theta/1', 'autorouting', 'smart');

add_line(mdl, 'v_gain/1', 'vcos/1', 'autorouting', 'smart');
add_line(mdl, 'cos_th/1', 'vcos/2', 'autorouting', 'smart');
add_line(mdl, 'v_gain/1', 'vsin/1', 'autorouting', 'smart');
add_line(mdl, 'sin_th/1', 'vsin/2', 'autorouting', 'smart');

add_line(mdl, 'vcos/1', 'int_x/1', 'autorouting', 'smart');
add_line(mdl, 'vsin/1', 'int_y/1', 'autorouting', 'smart');

add_line(mdl, 'int_x/1', 'sub_x/2', 'autorouting', 'smart');
add_line(mdl, 'int_y/1', 'sub_y/2', 'autorouting', 'smart');

add_line(mdl, 'int_x/1', 'out_x/1', 'autorouting', 'smart');
add_line(mdl, 'int_y/1', 'out_y/1', 'autorouting', 'smart');

% сохранить модель
save_system(mdl, [mdl '.slx']);
fprintf('OK: tangential_regulator.slx создан\n');


%% =========================
% ЗАПУСК СИМУЛЯЦИЙ ДЛЯ 4 ТОЧЕК
%% =========================

fprintf('[4/6] Запуск симуляций для 4 точек...\n');

% Набор целей: вправо, вверх, влево, вниз
goals = [  1  0;
           0  1;
          -1  0;
           0 -1];

% Имена полей для структур с результатами
p_keys = {'p10','p01','pm10','p0m1'};
t_keys = {'t10','t01','tm10','t0m1'};

simP = struct();
simT = struct();

%% Запуск P-регулятора
load_system('p_regulator');

for i = 1:4
    % Установить новую целевую точку
    set_param('p_regulator/goal_x', 'Value', num2str(goals(i,1)));
    set_param('p_regulator/goal_y', 'Value', num2str(goals(i,2)));

    % Сбросить начальное состояние робота
    set_param('p_regulator/int_x', 'InitialCondition', '0');
    set_param('p_regulator/int_y', 'InitialCondition', '0');
    set_param('p_regulator/int_theta', 'InitialCondition', '0');

    % Запуск симуляции
    out = sim('p_regulator', 'StopTime', '25', 'ReturnWorkspaceOutputs', 'on');

    % Сохранить траекторию
    st.t     = out.x.Time;
    st.x     = out.x.Data;
    st.y     = out.y.Data;
    st.theta = out.theta.Data;

    % Записать результат в структуру
    simP.(p_keys{i}) = st;
end

%% Запуск тангенциального регулятора
load_system('tangential_regulator');

for i = 1:4
    % Установить новую целевую точку
    set_param('tangential_regulator/goal_x', 'Value', num2str(goals(i,1)));
    set_param('tangential_regulator/goal_y', 'Value', num2str(goals(i,2)));

    % Сбросить начальное состояние робота
    set_param('tangential_regulator/int_x', 'InitialCondition', '0');
    set_param('tangential_regulator/int_y', 'InitialCondition', '0');
    set_param('tangential_regulator/int_theta', 'InitialCondition', '0');

    % Запуск симуляции
    out = sim('tangential_regulator', 'StopTime', '25', 'ReturnWorkspaceOutputs', 'on');

    % Сохранить траекторию
    st.t     = out.x.Time;
    st.x     = out.x.Data;
    st.y     = out.y.Data;
    st.theta = out.theta.Data;

    % Записать результат в структуру
    simT.(t_keys{i}) = st;
end

% Сохранить все результаты моделирования в файл
save(fullfile(DATA, 'sim_results.mat'), 'simP', 'simT');
fprintf('OK: sim_results.mat сохранён\n');


%% =========================
% СИМУЛЯЦИЯ ДВИЖЕНИЯ ПО КВАДРАТУ
%% =========================

fprintf('[5/6] Симуляция движения по квадрату...\n');

% Последовательность точек квадратной траектории
square_targets = [ ...
    0  0;
    1  1;
   -1  1;
   -1 -1;
    1 -1;
    1  1];

%% Траектория по квадрату для P-регулятора
simSquareP.x     = [];
simSquareP.y     = [];
simSquareP.theta = [];
simSquareP.t     = [];

% Начальное состояние
x0 = 0; y0 = 0; th0 = 0; time_shift = 0;
load_system('p_regulator');

for k = 2:size(square_targets,1)
    % Текущая целевая точка
    gx = square_targets(k,1);
    gy = square_targets(k,2);

    % Передать цель и текущее состояние как начальные условия
    set_param('p_regulator/goal_x', 'Value', num2str(gx));
    set_param('p_regulator/goal_y', 'Value', num2str(gy));
    set_param('p_regulator/int_x', 'InitialCondition', num2str(x0));
    set_param('p_regulator/int_y', 'InitialCondition', num2str(y0));
    set_param('p_regulator/int_theta', 'InitialCondition', num2str(th0));

    % Запустить отдельный участок движения
    out = sim('p_regulator', 'StopTime', '10', 'ReturnWorkspaceOutputs', 'on');

    % Данные участка
    x_seg  = out.x.Data;
    y_seg  = out.y.Data;
    th_seg = out.theta.Data;
    t_seg  = out.x.Time + time_shift;

    % Удалить первую точку участка, чтобы не было дублирования на стыке
    if ~isempty(simSquareP.x)
        x_seg  = x_seg(2:end);
        y_seg  = y_seg(2:end);
        th_seg = th_seg(2:end);
        t_seg  = t_seg(2:end);
    end

    % Добавить участок к общей траектории
    simSquareP.x     = [simSquareP.x;     x_seg];
    simSquareP.y     = [simSquareP.y;     y_seg];
    simSquareP.theta = [simSquareP.theta; th_seg];
    simSquareP.t     = [simSquareP.t;     t_seg];

    % Конец текущего участка становится началом следующего
    x0         = out.x.Data(end);
    y0         = out.y.Data(end);
    th0        = out.theta.Data(end);
    time_shift = simSquareP.t(end);
end

%% Траектория по квадрату для тангенциального регулятора
simSquareT.x     = [];
simSquareT.y     = [];
simSquareT.theta = [];
simSquareT.t     = [];

x0 = 0; y0 = 0; th0 = 0; time_shift = 0;
load_system('tangential_regulator');

for k = 2:size(square_targets,1)
    % Текущая целевая точка
    gx = square_targets(k,1);
    gy = square_targets(k,2);

    % Передать цель и текущее состояние как начальные условия
    set_param('tangential_regulator/goal_x', 'Value', num2str(gx));
    set_param('tangential_regulator/goal_y', 'Value', num2str(gy));
    set_param('tangential_regulator/int_x', 'InitialCondition', num2str(x0));
    set_param('tangential_regulator/int_y', 'InitialCondition', num2str(y0));
    set_param('tangential_regulator/int_theta', 'InitialCondition', num2str(th0));

    % Запустить отдельный участок движения
    out = sim('tangential_regulator', 'StopTime', '10', 'ReturnWorkspaceOutputs', 'on');

    % Данные участка
    x_seg  = out.x.Data;
    y_seg  = out.y.Data;
    th_seg = out.theta.Data;
    t_seg  = out.x.Time + time_shift;

    % Удалить повтор первой точки
    if ~isempty(simSquareT.x)
        x_seg  = x_seg(2:end);
        y_seg  = y_seg(2:end);
        th_seg = th_seg(2:end);
        t_seg  = t_seg(2:end);
    end

    % Добавить участок в общую траекторию
    simSquareT.x     = [simSquareT.x;     x_seg];
    simSquareT.y     = [simSquareT.y;     y_seg];
    simSquareT.theta = [simSquareT.theta; th_seg];
    simSquareT.t     = [simSquareT.t;     t_seg];

    % Обновить начальные условия для следующего участка
    x0         = out.x.Data(end);
    y0         = out.y.Data(end);
    th0        = out.theta.Data(end);
    time_shift = simSquareT.t(end);
end

% Сохранить траектории движения по квадрату
save(fullfile(DATA, 'sim_square.mat'), 'simSquareP', 'simSquareT');
fprintf('OK: sim_square.mat сохранён\n');

%% ============================================================
fprintf('[6/6] Построение итоговых графиков...\n');

p_exp_files = { ...
    fullfile(DATA,'p10.txt'), ...
    fullfile(DATA,'p01.txt'), ...
    fullfile(DATA,'p-10.txt'), ...
    fullfile(DATA,'p0-1.txt')};

t_exp_files = { ...
    fullfile(DATA,'tangential10.txt'), ...
    fullfile(DATA,'tangential01.txt'), ...
    fullfile(DATA,'tangential-10.txt'), ...
    fullfile(DATA,'tangential0-1.txt')};

titles_txt = { ...
    'Траектория из (0,0) в (1,0)', ...
    'Траектория из (0,0) в (0,1)', ...
    'Траектория из (0,0) в (-1,0)', ...
    'Траектория из (0,0) в (0,-1)'};

p_sim_keys = {'p10','p01','pm10','p0m1'};
t_sim_keys = {'t10','t01','tm10','t0m1'};

% Цвета
CPe = [0.00 0.35 0.85];
CTe = [0.85 0.10 0.10];
CPs = [0.35 0.70 1.00];
CTs = [1.00 0.50 0.50];

%% 6 общих графиков (4 перехода + общий + квадрат) — как было

for i = 1:4
    dp = readmatrix(p_exp_files{i});
    dt = readmatrix(t_exp_files{i});

    xp = dp(:,2);
    yp = dp(:,3);

    xt = dt(:,2);
    yt = dt(:,3);

    xps = simP.(p_sim_keys{i}).x * 1000;
    yps = simP.(p_sim_keys{i}).y * 1000;

    xts = simT.(t_sim_keys{i}).x * 1000;
    yts = simT.(t_sim_keys{i}).y * 1000;

    fig = figure('Visible','off','Position',[100 100 820 680]);
    hold on;

    plot(xp, yp, '-', 'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор');
    plot(xt, yt, '-', 'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный');
    plot(xps, yps, '--', 'Color', CPs, 'LineWidth', 2.0, 'DisplayName', 'Simulink P');
    plot(xts, yts, '--', 'Color', CTs, 'LineWidth', 2.0, 'DisplayName', 'Simulink Tangential');

    plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

    xlabel('X, мм');
    ylabel('Y, мм');
    title(titles_txt{i});
    legend('Location', 'best');
    grid on;
    axis equal;

    saveas(fig, fullfile(GRAPHICS, sprintf('point_%d.png', i)));
    close(fig);
end

fig = figure('Visible','off','Position',[100 100 1050 820]);
hold on;

for i = 1:4
    dp = readmatrix(p_exp_files{i});
    dt = readmatrix(t_exp_files{i});

    xp = dp(:,2);
    yp = dp(:,3);

    xt = dt(:,2);
    yt = dt(:,3);

    xps = simP.(p_sim_keys{i}).x * 1000;
    yps = simP.(p_sim_keys{i}).y * 1000;

    xts = simT.(t_sim_keys{i}).x * 1000;
    yts = simT.(t_sim_keys{i}).y * 1000;

    plot(xp, yp, '-', 'Color', CPe, 'LineWidth', 1.4, 'HandleVisibility', 'off');
    plot(xt, yt, '-', 'Color', CTe, 'LineWidth', 1.4, 'HandleVisibility', 'off');
    plot(xps, yps, '--', 'Color', CPs, 'LineWidth', 1.5, 'HandleVisibility', 'off');
    plot(xts, yts, '--', 'Color', CTs, 'LineWidth', 1.5, 'HandleVisibility', 'off');
end

plot(nan,nan,'-','Color',CPe,'LineWidth',2.0,'DisplayName','P-регулятор');
plot(nan,nan,'-','Color',CTe,'LineWidth',2.0,'DisplayName','Тангенциальный');
plot(nan,nan,'--','Color',CPs,'LineWidth',2.0,'DisplayName','Simulink P');
plot(nan,nan,'--','Color',CTs,'LineWidth',2.0,'DisplayName','Simulink Tangential');
plot(0,0,'ko','MarkerFaceColor','k','MarkerSize',7,'DisplayName','Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Общий график для всех переходов');
legend('Location', 'eastoutside');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'all_points.png'));
close(fig);

% экспериментальное движение по квадрату
dp_square = readmatrix(fullfile(DATA,'p_path.txt'));
dt_square = readmatrix(fullfile(DATA,'tangential_path.txt'));

xp_square = dp_square(:,2);
yp_square = dp_square(:,3);

xt_square = dt_square(:,2);
yt_square = dt_square(:,3);

% моделирование по квадрату
xsP = simSquareP.x * 1000;
ysP = simSquareP.y * 1000;

xsT = simSquareT.x * 1000;
ysT = simSquareT.y * 1000;

fig = figure('Visible','off','Position',[100 100 900 760]);
hold on;

plot(xp_square, yp_square, '-', 'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор');
plot(xt_square, yt_square, '-', 'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный');
plot(xsP, ysP, '--', 'Color', CPs, 'LineWidth', 2.0, 'DisplayName', 'Simulink P');
plot(xsT, ysT, '--', 'Color', CTs, 'LineWidth', 2.0, 'DisplayName', 'Simulink Tangential');

plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Траектория по квадрату');
legend('Location', 'best');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'square_path.png'));
close(fig);

%% ДОБАВЛЕНО: 6 отдельных графиков для P и 6 для тангенциального

% 4 графика только для P-регулятора (эксперимент + модель, движение в точку)
for i = 1:4
    dp = readmatrix(p_exp_files{i});

    xp = dp(:,2);
    yp = dp(:,3);

    xps = simP.(p_sim_keys{i}).x * 1000;
    yps = simP.(p_sim_keys{i}).y * 1000;

    fig = figure('Visible','off','Position',[100 100 820 680]);
    hold on;

    plot(xp,  yp,  '-',  'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор (эксп.)');
    plot(xps, yps, '--', 'Color', CPs, 'LineWidth', 2.0, 'DisplayName', 'P-регулятор (Simulink)');

    plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

    xlabel('X, мм');
    ylabel('Y, мм');
    title([titles_txt{i} ' (только P)']);
    legend('Location', 'best');
    grid on;
    axis equal;

    saveas(fig, fullfile(GRAPHICS, sprintf('point_P_%d.png', i)));
    close(fig);
end

% 2 дополнительных графика для P: общий (по точкам) и квадрат

% общий по четырём переходам (только P)
fig = figure('Visible','off','Position',[100 100 1050 820]);
hold on;

for i = 1:4
    dp = readmatrix(p_exp_files{i});
    xp = dp(:,2);
    yp = dp(:,3);

    xps = simP.(p_sim_keys{i}).x * 1000;
    yps = simP.(p_sim_keys{i}).y * 1000;

    plot(xp,  yp,  '-',  'Color', CPe, 'LineWidth', 1.4);
    plot(xps, yps, '--', 'Color', CPs, 'LineWidth', 1.5);
end

plot(0,0,'ko','MarkerFaceColor','k','MarkerSize',7,'DisplayName','Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Общий график для всех переходов (только P)');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'all_points_P.png'));
close(fig);

% квадрат (только P) — берём p_path.txt
fig = figure('Visible','off','Position',[100 100 900 760]);
hold on;

plot(xp_square,  yp_square,  '-',  'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор (эксп.)');
plot(xsP,       ysP,       '--', 'Color', CPs, 'LineWidth', 2.0, 'DisplayName', 'P-регулятор (Simulink)');
plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Траектория по квадрату (только P)');
legend('Location', 'best');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'square_path_P.png'));
close(fig);

% 4 графика только для тангенциального регулятора (эксперимент + модель, движение в точку)
for i = 1:4
    dt = readmatrix(t_exp_files{i});

    xt = dt(:,2);
    yt = dt(:,3);

    xts = simT.(t_sim_keys{i}).x * 1000;
    yts = simT.(t_sim_keys{i}).y * 1000;

    fig = figure('Visible','off','Position',[100 100 820 680]);
    hold on;

    plot(xt,  yt,  '-',  'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный (эксп.)');
    plot(xts, yts, '--', 'Color', CTs, 'LineWidth', 2.0, 'DisplayName', 'Тангенциальный (Simulink)');

    plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

    xlabel('X, мм');
    ylabel('Y, мм');
    title([titles_txt{i} ' (только тангенциальный)']);
    legend('Location', 'best');
    grid on;
    axis equal;

    saveas(fig, fullfile(GRAPHICS, sprintf('point_T_%d.png', i)));
    close(fig);
end

% 2 дополнительных графика для тангенциального: общий (по точкам) и квадрат

% общий по четырём переходам (только тангенциальный)
fig = figure('Visible','off','Position',[100 100 1050 820]);
hold on;

for i = 1:4
    dt = readmatrix(t_exp_files{i});
    xt = dt(:,2);
    yt = dt(:,3);

    xts = simT.(t_sim_keys{i}).x * 1000;
    yts = simT.(t_sim_keys{i}).y * 1000;

    plot(xt,  yt,  '-',  'Color', CTe, 'LineWidth', 1.4);
    plot(xts, yts, '--', 'Color', CTs, 'LineWidth', 1.5);
end

plot(0,0,'ko','MarkerFaceColor','k','MarkerSize',7,'DisplayName','Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Общий график для всех переходов (только тангенциальный)');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'all_points_T.png'));
close(fig);

% квадрат (только тангенциальный) — берём tangential_path.txt
fig = figure('Visible','off','Position',[100 100 900 760]);
hold on;

plot(xt_square,  yt_square,  '-',  'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный (эксп.)');
plot(xsT,       ysT,       '--', 'Color', CTs, 'LineWidth', 2.0, 'DisplayName', 'Тангенциальный (Simulink)');
plot(0, 0, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 7, 'DisplayName', 'Старт');

xlabel('X, мм');
ylabel('Y, мм');
title('Траектория по квадрату (только тангенциальный)');
legend('Location', 'best');
grid on;
axis equal;

saveas(fig, fullfile(GRAPHICS, 'square_path_T.png'));
close(fig);

fprintf('OK: все графики построены\n');