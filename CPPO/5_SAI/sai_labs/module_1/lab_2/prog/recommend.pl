% ---------------------------------------------------------------------------
% Лабораторная работа №2. Система поддержки принятия решений (рекомендательная
% система) на основе базы знаний из лабораторной №1 (tanks.pl).
%
% Программа принимает свободный текст пользователя, парсит его в факты,
% вычисляет для каждого танка рейтинг соответствия (score) и выдаёт
% отсортированный топ рекомендаций с обоснованием.
%
% Автор: Ануфриев А.С. 465029
% ---------------------------------------------------------------------------

:- use_module(library(lists)).

% Подключаем базу знаний из лабораторной №1 (рабочая копия в lab_2/prog/)
:- consult('tanks.pl').

% ===========================================================================
% ТОЧКА ВХОДА
% ===========================================================================

% start/0 — запуск диалога с пользователем
start :-
    format('~n=== Tank Recommendation System (Lab 2) ===~n', []),
    format('Based on tanks.pl knowledge base (Lab 1)~n', []),
    format('~nEnter briefly about yourself and your preferences. Example: '),
    format('"I am 13 years old, I like USSR, heavy tanks, VIII level, durable"~n', []),
    format('To exit type: end_of_file.~n~n', []),

    read_line(UserInput),
    (   UserInput = end_of_file -> halt
    ;   true
    ),

    format('~n--- Analyzing your request ---~n', []),
    parse_user_input(UserInput, Prefs),
    print_prefs(Prefs),

    format('~n--- Computing rating and ranking ---~n', []),
    rank_tanks(Prefs, Ranked),
    (   Ranked = [] ->
        format('No matching tanks found.~n', [])
    ;   print_ranked(Ranked)
    ),

    format('~n=== End ===~n~n', []).

% ===========================================================================
% ЧТЕНИЕ СТРОКИ
% ===========================================================================

read_line(Atom) :-
    read_line_to_string(user_input, Line),
    (   Line = end_of_file -> Atom = end_of_file
    ;   string_to_atom(Line, Atom)
    ).

% ===========================================================================
% ПАРСИНГ СВОБОДНОГО ТЕКСТА ПОЛЬЗОВАТЕЛЯ
% ===========================================================================

% parse_user_input/2 — извлекает предпочтения из свободного текста
parse_user_input(String, Prefs) :-
    downcase_atom(String, Lower),
    parse_nation(Lower, Nation),
    parse_class(Lower, Class),
    parse_level(Lower, Level),
    parse_style(Lower, Style),
    parse_age(Lower, Age),
    Prefs = prefs(Nation, Class, Level, Style, Age).

% parse_nation/2 — определяет нацию по ключевым словам
parse_nation(String, ussr) :-
    (   sub_atom(String, _, _, _, ussr)
    ;   sub_atom(String, _, _, _, 'ussr')
    ;   sub_atom(String, _, _, _, 'soviet')
    ;   sub_atom(String, _, _, _, 'russia')
    ;   sub_atom(String, _, _, _, 'ссср')
    ;   sub_atom(String, _, _, _, 'сср')
    ;   sub_atom(String, _, _, _, 'совет')
    ;   sub_atom(String, _, _, _, 'россий')
    ).
parse_nation(String, germany) :-
    (   sub_atom(String, _, _, _, germany)
    ;   sub_atom(String, _, _, _, 'german')
    ;   sub_atom(String, _, _, _, 'nazi')
    ;   sub_atom(String, _, _, _, 'герман')
    ;   sub_atom(String, _, _, _, 'немец')
    ;   sub_atom(String, _, _, _, 'германи')
    ).
parse_nation(String, usa) :-
    (   sub_atom(String, _, _, _, usa)
    ;   sub_atom(String, _, _, _, 'usa')
    ;   sub_atom(String, _, _, _, 'amer')
    ;   sub_atom(String, _, _, _, 'сша')
    ;   sub_atom(String, _, _, _, 'америк')
    ).
parse_nation(_, any).   % по умолчанию — любая нация

% parse_class/2 — определяет класс техники
parse_class(String, heavy) :-
    (   sub_atom(String, _, _, _, heavy)
    ;   sub_atom(String, _, _, _, 'heavy')
    ;   sub_atom(String, _, _, _, 'heavy_tank')
    ;   sub_atom(String, _, _, _, 'тяж')
    ;   sub_atom(String, _, _, _, 'тяжёлый')
    ;   sub_atom(String, _, _, _, 'тяжелый')
    ;   sub_atom(String, _, _, _, 'тт')
    ).
parse_class(String, medium) :-
    (   sub_atom(String, _, _, _, medium)
    ;   sub_atom(String, _, _, _, 'medium')
    ;   sub_atom(String, _, _, _, 'med')
    ;   sub_atom(String, _, _, _, 'средн')
    ;   sub_atom(String, _, _, _, 'средний')
    ).
parse_class(String, tank_destroyer) :-
    (   sub_atom(String, _, _, _, tank_destroyer)
    ;   sub_atom(String, _, _, _, 'td')
    ;   sub_atom(String, _, _, _, 'destroyer')
    ;   sub_atom(String, _, _, _, 'artiller')
    ;   sub_atom(String, _, _, _, 'пт')
    ;   sub_atom(String, _, _, _, 'сау')
    ;   sub_atom(String, _, _, _, 'птсау')
    ).
parse_class(_, any).

% parse_level/2 — уровень 7 или 8 (включая римские VII/VIII)
parse_level(String, 8) :-
    (   sub_atom(String, _, _, _, 'viii')
    ;   sub_atom(String, _, _, _, '8')
    ).
parse_level(String, 7) :-
    (   sub_atom(String, _, _, _, 'vii')
    ;   sub_atom(String, _, _, _, '7')
    ).
parse_level(_, any).

% parse_style/2 — стиль боя
parse_style(String, durable) :-
    (   sub_atom(String, _, _, _, durable)
    ;   sub_atom(String, _, _, _, 'durable')
    ;   sub_atom(String, _, _, _, 'tanky')
    ;   sub_atom(String, _, _, _, 'hp')
    ;   sub_atom(String, _, _, _, 'живуч')
    ;   sub_atom(String, _, _, _, 'броня')
    ;   sub_atom(String, _, _, _, 'хп')
    ;   sub_atom(String, _, _, _, 'живучест')
    ).
parse_style(String, hard_hitter) :-
    (   sub_atom(String, _, _, _, hard_hitter)
    ;   sub_atom(String, _, _, _, 'penetr')
    ;   sub_atom(String, _, _, _, 'gun')
    ;   sub_atom(String, _, _, _, 'power')
    ;   sub_atom(String, _, _, _, 'damage')
    ;   sub_atom(String, _, _, _, 'пробит')
    ;   sub_atom(String, _, _, _, 'пушк')
    ;   sub_atom(String, _, _, _, 'мощн')
    ;   sub_atom(String, _, _, _, 'урон')
    ;   sub_atom(String, _, _, _, 'быстр')
    ;   sub_atom(String, _, _, _, 'перезаряд')
    ;   sub_atom(String, _, _, _, 'альф')
    ).
parse_style(String, all_rounder) :-
    (   sub_atom(String, _, _, _, all_rounder)
    ;   sub_atom(String, _, _, _, 'универсал')
    ).
parse_style(String, glass_cannon) :-
    (   sub_atom(String, _, _, _, glass_cannon)
    ;   sub_atom(String, _, _, _, 'стеклян')
    ).
parse_style(_, any).

% parse_age/2 — извлекает возраст (число), any если не найдено
parse_age(String, any) :-
    \+ has_age(String).
parse_age(String, Age) :-
    has_age(String),
    extract_age(String, Age).

has_age(String) :-
    atom_codes(String, Codes),
    has_digit(Codes).

has_digit([]) :- !, fail.
has_digit([C|_]) :- C >= 48, C =< 57, !.
has_digit([_|Cs]) :- has_digit(Cs).

extract_age(String, Age) :-
    atom_codes(String, Codes),
    extract_first_integer(Codes, Age),
    Age > 0.

extract_first_integer([], 0).
extract_first_integer([C|Cs], Age) :-
    (   C >= 48, C =< 57 ->
        collect_digits(Cs, [C], DigitsRev),
        reverse(DigitsRev, Digits),
        number_codes(Age, Digits)
    ;   extract_first_integer(Cs, Age)
    ).

collect_digits([], Acc, Acc).
collect_digits([C|Cs], Acc0, Acc) :-
    (   C >= 48, C =< 57 ->
        collect_digits(Cs, [C|Acc0], Acc)
    ;   Acc = Acc0
    ).

% print_prefs/1 — выводит распознанные предпочтения
print_prefs(prefs(Nation, Class, Level, Style, Age)) :-
    format('  Nation: ~w~n', [Nation]),
    format('  Class: ~w~n', [Class]),
    format('  Level: ~w~n', [Level]),
    format('  Style: ~w~n', [Style]),
    format('  Age: ~w~n', [Age]).

% ===========================================================================
% СИСТЕМА РЕЙТИНГА И РАНЖИРОВАНИЯ
% ===========================================================================

% rank_tanks/2 — вычисляет рейтинг всех танков и сортирует по убыванию score
rank_tanks(Prefs, Ranked) :-
    findall(S-T, tank_score(Prefs, _, S, T), Scores),
    (   Scores = [] -> Ranked = []
    ;   keysort(Scores, Sorted),
        reverse(Sorted, Ranked)
    ).

% tank_score/4 — считает рейтинг одного танка (score, tank)
tank_score(prefs(Nation, Class, Level, Style, _Age), T, Score, Tank) :-
    Tank = T,
    tank_stats(T, Lvl, Nat, Cls, HP, _Alpha, Pen, _Armor, _Name, _Caliber, _Reload),

    % Базовые баллы за совпадение нации/класса/уровня (по 25 каждый)
    (   Nation == any -> ScoreNation = 25 ; Nat == Nation -> ScoreNation = 25 ; ScoreNation = 0 ),
    (   Class  == any -> ScoreClass  = 25 ; Cls == Class  -> ScoreClass  = 25 ; ScoreClass  = 0 ),
    (   Level  == any -> ScoreLevel  = 25 ; Lvl == Level  -> ScoreLevel  = 25 ; ScoreLevel  = 0 ),

    % Баллы за стиль боя (до 25)
    (   Style == any -> ScoreStyle = 25
    ;   match_style(T, Style) -> ScoreStyle = 25
    ;   ScoreStyle = 0
    ),

    % Бонус за характеристики в зависимости от стиля
    (   Style == durable, HP >= 1800 -> ScoreBonus = 10
    ;   Style == hard_hitter, Pen >= 220 -> ScoreBonus = 10
    ;   Style == all_rounder, HP >= 1800, Pen >= 220 -> ScoreBonus = 10
    ;   Style == glass_cannon, Pen >= 220, HP < 1800 -> ScoreBonus = 10
    ;   ScoreBonus = 0
    ),

    Score0 is ScoreNation + ScoreClass + ScoreLevel + ScoreStyle + ScoreBonus,
    (   Score0 > 100 -> Score = 100 ; Score = Score0 ).

% match_style/2 — фильтрация по стилю боя (переиспользуем правила из tanks.pl)
match_style(_, any).
match_style(T, durable) :- durable(T).
match_style(T, hard_hitter) :- hard_hitter(T).
match_style(T, all_rounder) :- all_rounder(T).
match_style(T, glass_cannon) :- glass_cannon(T).

% ===========================================================================
% ВЫВОД РЕКОМЕНДАЦИЙ
% ===========================================================================

% print_ranked/1 — выводит отсортированный список рекомендаций
print_ranked([]).
print_ranked([S-T|Rest]) :-
    tank_stats(T, Lvl, Nat, Cls, HP, Alpha, Pen, Armor, Name, Caliber, Reload),
    format('  ~w. ~w --- rating ~d/100~n', [S, Name, S]),
    format('      nation: ~w, level: ~w, class: ~w~n', [Nat, Lvl, Cls]),
    format('      HP: ~d, damage/shot: ~d, penetration: ~d mm, armor: ~d mm~n', [HP, Alpha, Pen, Armor]),
    format('      caliber: ~w mm, reload: ~w s~n', [Caliber, Reload]),
    print_style_reason(T),
    format('~n', []),
    print_ranked(Rest).

% print_style_reason/1 — обоснование почему этот танк подходит под стиль
print_style_reason(T) :-
    (   durable(T) ->
        tank_stats(T, _, _, _, HP, _, _, _, _, _, _),
        format('      Fits style "durable" (HP = ~d >= 1800).~n', [HP])
    ;   hard_hitter(T) ->
        tank_stats(T, _, _, _, _, _, Pen, _, _, _, _),
        format('      Fits style "hard_hitter" (penetration = ~d >= 220 mm).~n', [Pen])
    ;   all_rounder(T) ->
        format('      Fits style "all_rounder" (durable + hard_hitter).~n', [])
    ;   glass_cannon(T) ->
        format('      Fits style "glass_cannon" (high penetration, low durability).~n', [])
    ;   true
    ).

% ===========================================================================
% ТЕСТОВЫЕ СЦЕНАРИИ
% ===========================================================================

test_recommend :-
    format('~n=== Recommendation system tests ===~n', []),

    run_test('ussr, heavy, 8, durable', [ussr, heavy, 8, durable, any]),
    run_test('germany, any, 7, hard_hitter', [germany, any, 7, hard_hitter, any]),
    run_test('usa, medium, 8, all_rounder', [usa, medium, 8, all_rounder, any]),

    format('~n=== All tests completed ===~n~n', []).

run_test(Name, [Nation, Class, Level, Style, _Age]) :-
    format('~nTest: ~w~n', [Name]),
    prefs_rank(Nation, Class, Level, Style, Ranked),
    print_ranked(Ranked).

prefs_rank(Nation, Class, Level, Style, Ranked) :-
    Prefs = prefs(Nation, Class, Level, Style, any),
    rank_tanks(Prefs, Ranked).
