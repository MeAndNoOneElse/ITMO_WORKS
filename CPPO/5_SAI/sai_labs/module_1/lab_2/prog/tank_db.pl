
:- consult('tanks.pl').
speed(is_3,      37).
speed(t_44,      53).
speed(isu_152,   26).
speed(tiger_i,   45).
speed(panther_i, 55).
speed(jpanther,  46).
speed(tiger_ii,  34).
speed(panther_ii,46).
speed(ferdinand, 22).
speed(t29,       35).
speed(t_20,      40).
speed(t_25_2,    40).
speed(t32,       35).
speed(pershing,  40).
speed(t28_prot,  13).
speed(is,        37).
speed(t_43,      42).
speed(su_152,    28).

all_tanks(Ts) :-
    findall(T, tank(T), Ts).


filter_tanks(Nation, Class, Level, Ts) :-
    findall(T,
            (   tank_stats(T, Lvl, Nat, Cls, _, _, _, _, _, _, _),
                (   Nation = any ; Nat = Nation ),
                (   Class  = any ; Cls  = Class  ),
                (   Level  = any ; Lvl  = Level  )
            ),
            Ts).

alpha_max_tanks(Level, Ts) :-
    findall(Alpha-Tank,
            tank_stats(Tank, Level, _, _, _, Alpha, _, _, _, _, _),
            Pairs),
    (   Pairs = [] -> Ts = []
    ;   keysort(Pairs, Sorted),
        last(Sorted, MaxAlpha-_),
        findall(Tank, (member(Alpha-Tank, Pairs), Alpha = MaxAlpha), Ts)
    ).

fastest_tanks(Ids, Ts) :-
    findall(Speed-Tank,
            (   member(Tank, Ids),
                speed(Tank, Speed)
            ),
            Pairs),
    (   Pairs = [] -> Ts = []
    ;   keysort(Pairs, Sorted),
        last(Sorted, MaxSpeed-_),
        findall(Tank, (member(Speed-Tank, Pairs), Speed = MaxSpeed), Ts)
    ).

fastest_reloading_tanks(Ids, Ts) :-
    findall(Reload-Tank,
            (   member(Tank, Ids),
                tank_stats(Tank, _, _, _, _, _, _, _, _, _, Reload)
            ),
            Pairs),
    (   Pairs = [] -> Ts = []
    ;   keysort(Pairs, Sorted),
        Sorted = [MinReload-_|_],
        findall(Tank, (member(Reload-Tank, Pairs), Reload = MinReload), Ts)
    ).

tank_by_name(Name, Tank) :-
    tank_stats(Tank, _, _, _, _, _, _, _, Name, _, _).

tank_row(Tank, Level, Nation, Class, HP, Alpha, Pen, Armor, Name, Caliber, Reload, Speed) :-
    tank_stats(Tank, Level, Nation, Class, HP, Alpha, Pen, Armor, Name, Caliber, Reload),
    speed(Tank, Speed).

print_tank(Tank) :-
    tank_row(Tank, Lvl, Nat, Cls, HP, Alpha, Pen, Armor, Name, Caliber, Reload, Speed),
    writeln(Lvl|Nat|Cls|HP|Alpha|Pen|Armor|Name|Caliber|Reload|Speed).

all_nations(Ns) :- findall(N, nation(N), Ns).
all_levels(Ls)  :- findall(L, level(L), Ls).
all_manufacturers(Ms) :- findall(M, manufacturer(M), Ms).

tank_manufacturer(Tank, Manufacturer) :-
    built_by(Tank, Manufacturer, _).
