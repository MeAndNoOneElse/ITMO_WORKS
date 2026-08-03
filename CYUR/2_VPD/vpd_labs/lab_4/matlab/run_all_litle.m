%% run_all_litle.m
% Один файл для 4 лабы: запуск симуляций и построение графиков

DATA = fullfile('..', 'data');
GRAPHICS = fullfile('..', 'graphics');

%% ============================================================
%% ШАГ 1. ПАРАМЕТРЫ
%% ============================================================
r = 0.029;      % радиус колеса, м
B = 0.120;      % база, м

K_s = 0.5;      % коэффициенты P-регулятора
K_r = 2;

K1 = 0.5;       % коэффициенты тангенциального регулятора
K2 = 1;

MAX_U = 50.0;

assignin('base', 'r', r);
assignin('base', 'B', B);
assignin('base', 'K_s', K_s);
assignin('base', 'K_r', K_r);
assignin('base', 'K1', K1);
assignin('base', 'K2', K2);
assignin('base', 'MAX_U', MAX_U);

%% ============================================================
%% ШАГ 2. СОЗДАНИЕ МОДЕЛЕЙ (пропущено - модели создаются отдельно)
%% ============================================================
% p_regulator.slx и tangential_regulator.slx должны быть созданы заранее

%% ============================================================
%% ШАГ 3. ЗАГРУЗКА МОДЕЛЕЙ (пропущено - модели загружаются при симуляции)
%% ============================================================

%% ============================================================
%% ШАГ 4. СИМУЛЯЦИИ ДЛЯ 4 ТОЧЕК
%% ============================================================
goals = [ 1  0;
          0  1;
         -1  0;
          0 -1];

p_keys = {'p10','p01','pm10','p0m1'};
t_keys = {'t10','t01','tm10','t0m1'};

simP = struct();
simT = struct();

load_system('p_regulator');
for i = 1:4
    set_param('p_regulator/goal_x', 'Value', num2str(goals(i,1)));
    set_param('p_regulator/goal_y', 'Value', num2str(goals(i,2)));
    set_param('p_regulator/int_x', 'InitialCondition', '0');
    set_param('p_regulator/int_y', 'InitialCondition', '0');
    set_param('p_regulator/int_theta', 'InitialCondition', '0');

    out = sim('p_regulator', 'StopTime', '25', 'ReturnWorkspaceOutputs', 'on');

    st.t = out.x.Time;
    st.x = out.x.Data;
    st.y = out.y.Data;
    st.theta = out.theta.Data;
    simP.(p_keys{i}) = st;
end

load_system('tangential_regulator');
for i = 1:4
    set_param('tangential_regulator/goal_x', 'Value', num2str(goals(i,1)));
    set_param('tangential_regulator/goal_y', 'Value', num2str(goals(i,2)));
    set_param('tangential_regulator/int_x', 'InitialCondition', '0');
    set_param('tangential_regulator/int_y', 'InitialCondition', '0');
    set_param('tangential_regulator/int_theta', 'InitialCondition', '0');

    out = sim('tangential_regulator', 'StopTime', '25', 'ReturnWorkspaceOutputs', 'on');

    st.t = out.x.Time;
    st.x = out.x.Data;
    st.y = out.y.Data;
    st.theta = out.theta.Data;
    simT.(t_keys{i}) = st;
end

%% ============================================================
%% ШАГ 5. СИМУЛЯЦИЯ КВАДРАТА
%% ============================================================
square_targets = [ ...
     0  0;
     1  1;
    -1  1;
    -1 -1;
     1 -1;
     1  1];

simSquareP.x = [];
simSquareP.y = [];
simSquareP.theta = [];
simSquareP.t = [];

x0 = 0; y0 = 0; th0 = 0; time_shift = 0;
load_system('p_regulator');

for k = 2:size(square_targets,1)
    gx = square_targets(k,1);
    gy = square_targets(k,2);

    set_param('p_regulator/goal_x', 'Value', num2str(gx));
    set_param('p_regulator/goal_y', 'Value', num2str(gy));
    set_param('p_regulator/int_x', 'InitialCondition', num2str(x0));
    set_param('p_regulator/int_y', 'InitialCondition', num2str(y0));
    set_param('p_regulator/int_theta', 'InitialCondition', num2str(th0));

    out = sim('p_regulator', 'StopTime', '10', 'ReturnWorkspaceOutputs', 'on');

    x_seg = out.x.Data;
    y_seg = out.y.Data;
    th_seg = out.theta.Data;
    t_seg = out.x.Time + time_shift;

    if ~isempty(simSquareP.x)
        x_seg = x_seg(2:end);
        y_seg = y_seg(2:end);
        th_seg = th_seg(2:end);
        t_seg = t_seg(2:end);
    end

    simSquareP.x = [simSquareP.x; x_seg];
    simSquareP.y = [simSquareP.y; y_seg];
    simSquareP.theta = [simSquareP.theta; th_seg];
    simSquareP.t = [simSquareP.t; t_seg];

    x0 = out.x.Data(end);
    y0 = out.y.Data(end);
    th0 = out.theta.Data(end);
    time_shift = simSquareP.t(end);
end

simSquareT.x = [];
simSquareT.y = [];
simSquareT.theta = [];
simSquareT.t = [];

x0 = 0; y0 = 0; th0 = 0; time_shift = 0;
load_system('tangential_regulator');

for k = 2:size(square_targets,1)
    gx = square_targets(k,1);
    gy = square_targets(k,2);

    set_param('tangential_regulator/goal_x', 'Value', num2str(gx));
    set_param('tangential_regulator/goal_y', 'Value', num2str(gy));
    set_param('tangential_regulator/int_x', 'InitialCondition', num2str(x0));
    set_param('tangential_regulator/int_y', 'InitialCondition', num2str(y0));
    set_param('tangential_regulator/int_theta', 'InitialCondition', num2str(th0));

    out = sim('tangential_regulator', 'StopTime', '10', 'ReturnWorkspaceOutputs', 'on');

    x_seg = out.x.Data;
    y_seg = out.y.Data;
    th_seg = out.theta.Data;
    t_seg = out.x.Time + time_shift;

    if ~isempty(simSquareT.x)
        x_seg = x_seg(2:end);
        y_seg = y_seg(2:end);
        th_seg = th_seg(2:end);
        t_seg = t_seg(2:end);
    end

    simSquareT.x = [simSquareT.x; x_seg];
    simSquareT.y = [simSquareT.y; y_seg];
    simSquareT.theta = [simSquareT.theta; th_seg];
    simSquareT.t = [simSquareT.t; t_seg];

    x0 = out.x.Data(end);
    y0 = out.y.Data(end);
    th0 = out.theta.Data(end);
    time_shift = simSquareT.t(end);
end

%% ============================================================
%% ШАГ 6. ПОСТРОЕНИЕ ИТОГОВЫХ ГРАФИКОВ
%% ============================================================
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

CPe = [0.00 0.35 0.85];
CTe = [0.85 0.10 0.10];
CPs = [0.35 0.70 1.00];
CTs = [1.00 0.50 0.50];

%% 4 графика по точкам
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

    plot(xp,  yp,  '-',  'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор');
    plot(xt,  yt,  '-',  'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный');
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

%% Общий график
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

    plot(xp,  yp,  '-',  'Color', CPe, 'LineWidth', 1.4, 'HandleVisibility', 'off');
    plot(xt,  yt,  '-',  'Color', CTe, 'LineWidth', 1.4, 'HandleVisibility', 'off');
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

%% График по квадрату
dp = readmatrix(fullfile(DATA,'p_path.txt'));
dt = readmatrix(fullfile(DATA,'tangential_path.txt'));

xp = dp(:,2);
yp = dp(:,3);

xt = dt(:,2);
yt = dt(:,3);

xsP = simSquareP.x * 1000;
ysP = simSquareP.y * 1000;

xsT = simSquareT.x * 1000;
ysT = simSquareT.y * 1000;

fig = figure('Visible','off','Position',[100 100 900 760]);
hold on;

plot(xp,  yp,  '-',  'Color', CPe, 'LineWidth', 2.1, 'DisplayName', 'P-регулятор');
plot(xt,  yt,  '-',  'Color', CTe, 'LineWidth', 2.1, 'DisplayName', 'Тангенциальный');
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