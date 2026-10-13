% 1. ФАКТЫ С ОДНИМ АРГУМЕНТОМ (20+)

% Нации 
nation(ussr).
nation(germany).
nation(usa).

% Классы техники 
tank_class(heavy).
tank_class(medium).
tank_class(tank_destroyer).

% Производители 
manufacturer(chelyabinsk_kirov_plant).
manufacturer(henschel).
manufacturer(us_army_ordnance).
manufacturer(kharkiv_plant_75).

% Уровни техники (2)
level(7).
level(8).

tank(is_3).
tank(t_44).
tank(isu_152).
tank(is).
tank(t_43).
tank(su_152).
tank(tiger_ii).
tank(panther_ii).
tank(ferdinand).
tank(tiger_i).
tank(panther_i).
tank(jpanther).
tank(t32).
tank(pershing).
tank(t28_prot).
tank(t29).
tank(t_20).
tank(t_25_2).



% 2. ФАКТЫ С ДВУМЯ И БОЛЕЕ АРГУМЕНТАМИ 15
tank_stats(is_3,      8, ussr,    heavy,          1800, 400, 225, 110, 'ИС-3',     122, 12.21).
tank_stats(t_44,      8, ussr,    medium,         1400, 400, 230,  90, 'Т-44',     122, 16.72).
tank_stats(isu_152,   8, ussr,    tank_destroyer, 1100, 640, 286,  90, 'ИСУ-152',  152, 12.12).
tank_stats(tiger_i,   7, germany, heavy,          1500, 310, 203, 178, 'Tiger I',  105,  8.00).
tank_stats(panther_i, 7, germany, medium,         1300, 280, 198, 100, 'Panther I', 88,  5.50).
tank_stats(jpanther,  7, germany, tank_destroyer, 1400, 460, 226, 150, 'Jagdpanther', 105, 10.00).
tank_stats(tiger_ii,   8, germany, heavy,          1850, 310, 225, 150, 'Tiger II',   105,  7.58).
tank_stats(panther_ii, 8, germany, medium,         1400, 220, 203, 100, 'Panther II',  88,  5.14).
tank_stats(ferdinand,  8, germany, tank_destroyer, 1400, 460, 246, 200, 'Ferdinand',  128, 10.10).
tank_stats(t29,       7, usa,     heavy,          1600, 400, 198, 140, 'T29',      105, 10.00).
tank_stats(t_20,      7, usa,     medium,         1300, 240, 180,  80, 'T20',       90,  7.00).
tank_stats(t_25_2,    7, usa,     tank_destroyer, 1250, 240, 180, 100, 'T25/2',     90,  8.00).
tank_stats(t32,       8, usa,     heavy,          1850, 310, 218, 150, 'T32',      105,  8.60).
tank_stats(pershing,  8, usa,     medium,         1400, 240, 180,  90, 'Pershing',  90,  8.00).
tank_stats(t28_prot,  8, usa,     tank_destroyer, 1250, 400, 248, 200, 'T28 Prot.', 120, 12.00).
tank_stats(is,        7, ussr,    heavy,          1500, 390, 175, 120, 'ИС',       122, 12.00).
tank_stats(t_43,      7, ussr,    medium,         1250, 390, 175,  75, 'Т-43',     100,  8.50).
tank_stats(su_152,    7, ussr,    tank_destroyer, 1200, 640, 250, 110, 'СУ-152',   152, 17.00).

% built_by(Танк, Производитель, ГодНачалаРазработки) 
built_by(is,         chelyabinsk_kirov_plant, 1943).
built_by(t_43,       kharkiv_plant_75,        1942).
built_by(su_152,     chelyabinsk_kirov_plant, 1943).
built_by(is_3,       chelyabinsk_kirov_plant, 1945).
built_by(t_44,       kharkiv_plant_75,        1944).
built_by(isu_152,    chelyabinsk_kirov_plant, 1943).
built_by(tiger_i,    henschel,                1937).
built_by(panther_i,  henschel,                1941).
built_by(jpanther,   henschel,                1942).
built_by(tiger_ii,   henschel,                1944).
built_by(panther_ii, henschel,                1943).
built_by(ferdinand,  henschel,                1942).
built_by(t29,        us_army_ordnance,        1944).
built_by(t_20,       us_army_ordnance,        1942).
built_by(t_25_2,     us_army_ordnance,        1943).
built_by(t32,        us_army_ordnance,        1945).
built_by(pershing,   us_army_ordnance,        1942).
built_by(t28_prot,   us_army_ordnance,        1943).

% unlocked_from(ТанкVIII, ТанкVII)
unlocked_from(is_3,      is).
unlocked_from(t_44,      t_43).
unlocked_from(isu_152,   su_152).
unlocked_from(tiger_ii,  tiger_i).
unlocked_from(panther_ii, panther_i).
unlocked_from(ferdinand, jpanther).
unlocked_from(t32,       t29).
unlocked_from(pershing,  t_20).
unlocked_from(t28_prot,  t_25_2).

% team(Команда, [Танки]) 
team(ussr_8,    [is_3, t_44, isu_152]).
team(germany_8, [tiger_ii, panther_ii, ferdinand]).
team(usa_8, [t32, pershing, t28_prot]).
team(ussr_7,    [is, t_43, su_152]).
team(germany_7, [tiger_i, panther_i, jpanther]).
team(usa_7, [t29, t_20, t_25_2]).

% team_title(Команда, Название) 
team_title(ussr_7,    '7 уровень СССР').
team_title(germany_7, '7 уровень Германия').
team_title(usa_8, '8 уровень США' ).
team_title(usa_7, '7 уровень США' ).
team_title(ussr_8,    '8 уровень СССР').
team_title(germany_8, '8 уровень Германия').

% 3. ПРАВИЛА (5)
Живучий танк: HP >= 1800.
durable(T) :-
    tank_stats(T, _, _, _, HP, _, _, _, _, _, _),
    HP >= 1800.

Сильное пробитие: >= 220 мм.
hard_hitter(T) :-
    tank_stats(T, _, _, _, _, _, Pen, _, _, _, _),
    Pen >= 220.

% Универсал: И живучий, И пробивной.
% Две цели соединены запятой (конъюнкция) — обе должны быть истинны.
all_rounder(T) :-
    durable(T),
    hard_hitter(T).

% пробивной, но НЕ живучий.
% Отрицание как неудача: \+ durable(T).
glass_cannon(T) :-
    hard_hitter(T),
    \+ durable(T).

% Противники во Второй мировой
% Внутри — дизъюнкция (;), снаружи — конъюнкция (,).
opponents(A, B) :-
    tank_stats(A, _, N1, _, _, _, _, _, _, _, _),
    tank_stats(B, _, N2, _, _, _, _, _, _, _, _),
    A @< B,
    (   N1 = germany, member(N2, [ussr, usa])
    ;   N2 = germany, member(N1, [ussr, usa])
    ).

best_gun(Lvl, T) :-
    level(Lvl),
    findall(Pen-T, tank_stats(T, Lvl, _, _, _, _, Pen, _, _, _, _), L),
    L \== [],
    keysort(L, Sorted),
    last(Sorted, _-T).


% 4. ПРИМЕРЫ ЗАПРОСОВ (вводятся после «?-»)

% --- 4.1 Простые запросы к фактам ---------------------------------
% ?- tank(is_3).                                   % true
% ?- tank(is_1).                                   % false (нет такого)
% ?- nation(germany).                              % true
% ?- level(7).                                     % true
% ?- manufacturer(henschel).                       % true
% ?- tank_class(heavy).                            % true
% ?- built_by(is_3, M, Y).                         % M = kirov_plant, Y = 1945
% ?- unlocked_from(t_44, P).                       % P = t_43
% ?- team(ussr_8, L).                              % L = [is_3, t_44, isu_152]
% ?- team_title(usa_7, T).                         % T = '7 уровень США'

% --- 4.2 Запросы с переменными (поиск по характеристикам) --------
% ?- tank_stats(T, 8, ussr, _, _, _, _, _, _, _, _).
%     % T = is_3 ; T = t_44 ; T = isu_152

% ?- tank_stats(T, _, _, heavy, HP, _, _, _, _, _, _), HP > 1800.
%     % T = tiger_ii ; T = t32

% ?- tank_stats(T, _, _, _, _, Alpha, _, _, _, _, _), Alpha >= 400.
%     % T = is_3 ; T = t_44 ; T = isu_152 ; T = jpanther ;
%     % T = ferdinand ; T = t29 ; T = t28_prot ; T = su_152

% ?- tank_stats(T, 7, usa, _, _, _, _, _, Name, _, _).
%     % T = t29, Name = 'T29' ; T = t_20, Name = 'T20' ;
%     % T = t_25_2, Name = 'T25/2'

% ?- tank_stats(T, _, _, _, _, _, Pen, _, _, _, Reload),
%    Pen >= 220, Reload =< 12.
%     % T = is_3 ; T = isu_152 ; T = tiger_ii ; T = ferdinand ; T = t28_prot

% ?- built_by(T, kirov_plant, _).
%     % T = is_3 ; T = isu_152 (внимание: у вас в фактах
%     % производитель записан как chelyabinsk_kirov_plant!)

% --- 4.3 Логические операторы И / ИЛИ / НЕ ------------------------
% И:   ?- tank_stats(T, 8, ussr, _, _, _, _, _, _, _, _),
%          tank_stats(T, _, _, _, HP, _, _, _, _, _, _), HP > 1500.
%          % T = is_3

% ИЛИ: ?- tank_stats(T, _, _, medium, _, _, _, _, _, _, _) ;
%          tank_stats(T, _, _, tank_destroyer, _, _, _, _, _, _, _).
%          % T = t_44 ; T = panther_i ; T = panther_ii ; T = t_20 ;
%          % T = pershing ; T = isu_152 ; T = jpanther ; T = ferdinand ;
%          % T = t_25_2 ; T = t28_prot ; T = su_152

% НЕ:  ?- tank(T), \+ durable(T).
%          % T = t_44 ; T = isu_152 ; T = tiger_i ; T = panther_i ;
%          % T = jpanther ; T = panther_ii ; T = ferdinand ; T = t29 ;
%          % T = t_20 ; T = t_25_2 ; T = pershing ; T = t28_prot ;
%          % T = is ; T = t_43 ; T = su_152

% --- 4.4 Запросы, требующие выполнения правил ---------------------
% ?- durable(T).
%     % T = is_3 ; T = tiger_ii ; T = t32

% ?- hard_hitter(T).
%     % T = is_3 ; T = isu_152 ; T = jpanther ; T = tiger_ii ;
%     % T = ferdinand ; T = t28_prot ; T = su_152

% ?- all_rounder(T).                 % И durable, И hard_hitter
%     % T = is_3 ; T = tiger_ii ; T = t28_prot? — проверьте у себя
%     % (у t28_prot HP 1250, значит durable ложно → не попадёт)
%     % Фактически: T = is_3 ; T = tiger_ii

% ?- glass_cannon(T).                % hard_hitter И НЕ durable
%     % T = isu_152 ; T = jpanther ; T = ferdinand ; T = t28_prot ;
%     % T = su_152

% ?- opponents(A, B).                % Германия против СССР/США
%     % A = tiger_i,  B = is ; …  (много пар)
%     % A = is_3, B = tiger_ii ; …  и т.д.

% --- 4.5 Запросы с агрегацией / «лучший в уровне» -----------------
% ?- best_gun(8, T).
%     % T = isu_152   (пробитие 286)

% ?- best_gun(7, T).
%     % T = su_152    (пробитие 250)

% ?- findall(HP-T, tank_stats(T, 8, _, _, HP, _, _, _, _, _, _), L),
%    sort(0, @>=, L, Sorted).
%     % Sorted = [1850-tiger_ii, 1850-t32, 1800-is_3,
%     %           1400-t_44, 1400-panther_ii, 1400-ferdinand,
%     %           1250-t28_prot, 1100-isu_152]