#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Рекомендательная система танков (лабораторная работа №2, САИ).

Архитектура:
  * tanks.pl / tank_db.pl — база знаний на Prolog (источник данных, как БД).
  * recommend.py (Python) — парсит запрос пользователя на русском и шлет
    логические запросы в Prolog через swipl.

Формат запроса (3 части, в порядке ввода):
    <вывод> <объект> <условия...>
  1) Вывод:       выведи | подскажи | какой есть
  2) Объект:      танк | уровень | завод | нация
  3) Условия (3.1-3.6, комбинируются, накладываются в порядке входа в запрос):
      нация: советский | немецкий | американский
      тип:   тт | ст | лт
      лвл:   7лвл | 8 лвл (или лвл 7/8)
      с высокой альфой   — урон больше всех на уровне (по умолчанию 8)
      быстрый            — скорость больше всех
      скорострельный     — перезарядка меньше всех
      конкретный танк <имя>

Примеры:
  выведи танк нация советский тип тт лвл 8 с высокой альфой
  подскажи танк немецкий лвл 7 быстрый
  выведи танк американский скорострельный
  какой есть нации
  выведи танк конкретный танк ИС-3

Выход: exit / выход / quit / EOF
"""

import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Set, Tuple

PROLOG = "swipl"
PROG_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(PROG_DIR, "tank_db.pl")

# ---------------------------------------------------------------------------
# Пrolog <-> Python мост
# ---------------------------------------------------------------------------
#
# Примечание: в этой сборке SWI-Prolog 10 ключ -t <goal> приводит к
# ошибке инициализации create_prolog_flag/3 при целях с переменными,
# поэтому цель подается на stdin интерактивногоをつбoplevel-а, а stdout
# парсится построчно.

def prolog(goal: str) -> List[str]:
    """Выполнить цель Prolog в tank_db.pl, вернуть непустые строки stdout."""
    try:
        proc = subprocess.run(
            [PROLOG, "-q", "-f", DB_FILE],
            input=goal + ", halt.\n",
            capture_output=True,
            text=True,
            cwd=PROG_DIR,
        )
    except FileNotFoundError:
        sys.stderr.write("Ошибка: SWI-Prolog (swipl) не найден в PATH.\n")
        sys.exit(1)
    if proc.returncode != 0:
        sys.stderr.write("Ошибка SWI-Prolog: " + proc.stderr.strip() + "\n")
        sys.exit(1)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Загрузка всей выборки характеристик из базы знаний (один запрос при старте)
# ---------------------------------------------------------------------------

# tank_row(Tank, Level, Nation, Class, HP, Alpha, Pen, Armor, Name, Caliber, Reload, Speed)
ALL_ROWS: Dict[str, Tuple] = {}
ALL_IDS: List[str] = []


def load_rows() -> None:
    global ALL_ROWS, ALL_IDS
    ids = prolog("all_tanks(Ts), maplist(writeln, Ts)")
    ALL_IDS = ids
    for tank_id in ids:
        fields = prolog(f"print_tank({tank_id})")
        if not fields:
            continue
        # 8|ussr|heavy|1800|400|225|110|'ИС-3'|122|12.21|37
        parts = fields[0].split("|")
        if len(parts) != 11:
            continue
        (lvl, nat, cls, hp, alpha, pen, armor, name, caliber, reload_, speed) = parts
        ALL_ROWS[tank_id] = (
            int(lvl), nat, cls, int(hp), int(alpha), int(pen), int(armor),
            name.strip("'"), int(caliber), float(reload_), int(speed),
        )


NAME_TO_ID: Dict[str, str] = {}  # lowercased display name -> tank id


def build_name_index() -> None:
    global NAME_TO_ID
    for tank_id, row in ALL_ROWS.items():
        NAME_TO_ID[row[7].lower()] = tank_id  # row[7] = Name


# ---------------------------------------------------------------------------
# Словари для парсинга и вывода (по-русски)
# ---------------------------------------------------------------------------

MODE_ALIASES = {
    "выведи": "show",
    "подскажи": "recommend",
}
ENTITY_ALIASES = {
    "танк": "tank",
    "танки": "tank",
    "уровень": "level",
    "уровни": "level",
    "завод": "manufacturer",
    "заводы": "manufacturer",
    "нация": "nation",
    "нации": "nation",
}
NATION_ALIASES = {
    "советский": "ussr",
    "немецкий": "germany",
    "американский": "usa",
}
CLASS_ALIASES = {
    "тт": "heavy",
    "ст": "medium",
    "лт": "light",
    "пт": "tank_destroyer"
}

NATION_RU = {
    "ussr": "Советский Союз",
    "germany": "Германия",
    "usa": "США",
}
CLASS_RU = {
    "heavy": "тяжёлый",
    "medium": "средний",
    "tank_destroyer": "ПТ-САУ",
    "light": "лёгкий",
}
MANUFACTURER_RU = {
    "chelyabinsk_kirov_plant": "Челябинский кировский завод",
    "henschel": "Хеншель",
    "us_army_ordnance": "Армийское артиллерийское управление США",
    "kharkiv_plant_75": "Харьковский завод №75",
}

ENTITY_LABEL_RU = {
    "tank": "танков",
    "nation": "наций",
    "level": "уровней",
    "manufacturer": "заводов",
}


# ---------------------------------------------------------------------------
# Парсинг запроса
# ---------------------------------------------------------------------------

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()


# Condition: (kind, value)
# kinds: nation | class | level | alpha | speed | reload | specific


def parse_request(text: str) -> Dict:
    tokens = tokenize(text)
    n = len(tokens)

    mode: Optional[str] = None
    entity: Optional[str] = None
    conditions: List[Tuple[str, Optional[str | int]]] = []

    i = 0
    while i < n:
        t = tokens[i]

        # --- режим вывода (первое вхождение) ---
        if mode is None and t in MODE_ALIASES:
            mode = MODE_ALIASES[t]
            i += 1
            continue
        # "какой есть"
        if mode is None and t == "какой" and i + 1 < n and tokens[i + 1] == "есть":
            mode = "what_exists"
            i += 2
            continue

        # --- объект (первое вхождение) ---
        if entity is None and t in ENTITY_ALIASES:
            entity = ENTITY_ALIASES[t]
            i += 1
            continue

        # --- условия (в порядке вхождения) ---
        if t == "с" and i + 2 < n and tokens[i + 1] == "высокой" and tokens[i + 2] == "альфой":
            conditions.append(("alpha", None))
            i += 3
            continue
        if t in NATION_ALIASES:
            conditions.append(("nation", NATION_ALIASES[t]))
            i += 1
            continue
        if t in CLASS_ALIASES:
            conditions.append(("class", CLASS_ALIASES[t]))
            i += 1
            continue
        m = re.fullmatch(r"(\d+)лвл", t)
        if m:
            conditions.append(("level", int(m.group(1))))
            i += 1
            continue
        if t == "лвл" and i + 1 < n and tokens[i + 1] in ("7", "8"):
            conditions.append(("level", int(tokens[i + 1])))
            i += 2
            continue
        if t == "быстрый":
            conditions.append(("speed", None))
            i += 1
            continue
        if t == "скорострельный":
            conditions.append(("reload", None))
            i += 1
            continue
        if t == "конкретный" and i + 1 < n and tokens[i + 1] == "танк":
            # остаток исходной строки после фразы — имя танка (сохраняем регистр)
            phrase = "конкретный танк"
            pos = text.lower().find(phrase, i * 0)  # найдем первое вхождение в исходнике
            # проще: взять всё после позиции фразы в токенах
            rest_tokens = tokens[i + 2:]
            # восстановить имя по оригинальной строке: найти фразу без учета регистра
            lower = text.lower()
            p = lower.find("конкретный танк")
            name = text[p + len("конкретный танк"):].strip() if p != -1 else ""
            name = re.sub(r"\s+", " ", name)
            conditions.append(("specific", name if name else None))
            i = n
            continue

        i += 1

    return {"mode": mode or "show", "entity": entity or "tank", "conditions": conditions}


# ---------------------------------------------------------------------------
# Применение условий (каждое условие — отдельный логический запрос к Prolog)
# ---------------------------------------------------------------------------

def filter_by(kind: str, value, candidates: Set[str], level_hint: Optional[int]) -> Tuple[Set[str], Optional[int]]:
    if kind == "nation":
        ids = set(prolog(f"filter_tanks({value}, any, any, Ts), maplist(writeln, Ts)"))
        return candidates & ids, level_hint
    if kind == "class":
        ids = set(prolog(f"filter_tanks(any, {value}, any, Ts), maplist(writeln, Ts)"))
        return candidates & ids, level_hint
    if kind == "level":
        ids = set(prolog(f"filter_tanks(any, any, {value}, Ts), maplist(writeln, Ts)"))
        return candidates & ids, value
    if kind == "alpha":
        lvl = level_hint if level_hint is not None else 8
        at_lvl = [t for t in candidates if ALL_ROWS[t][0] == lvl]
        if not at_lvl:
            return set(), level_hint
        alpha_ids = set(prolog(f"alpha_max_tanks({lvl}, Ts), maplist(writeln, Ts)"))
        new_cand = {t for t in at_lvl if t in alpha_ids}
        return new_cand, level_hint
    if kind == "speed":
        if not candidates:
            return set(), level_hint
        id_list = ",".join(sorted(candidates))
        ids = set(prolog(f"fastest_tanks([{id_list}], Ts), maplist(writeln, Ts)"))
        return ids, level_hint
    if kind == "reload":
        if not candidates:
            return set(), level_hint
        id_list = ",".join(sorted(candidates))
        ids = set(prolog(f"fastest_reloading_tanks([{id_list}], Ts), maplist(writeln, Ts)"))
        return ids, level_hint
    if kind == "specific":
        tid = NAME_TO_ID.get(str(value).lower()) if value else None
        return ({tid} if tid else set()), level_hint
    return candidates, level_hint


# ---------------------------------------------------------------------------
# Оформление результата
# ---------------------------------------------------------------------------

def tank_line(tank_id: str) -> str:
    lvl, nat, cls, hp, alpha, pen, armor, name, caliber, reload_, speed = ALL_ROWS[tank_id]
    return (
        f"{name} ({NATION_RU.get(nat, nat)}, {lvl} лвл, {CLASS_RU.get(cls, cls)}): "
        f"HP {hp}, урон/выстрел {alpha}, пробитие {pen} мм, броня {armor} мм, "
        f"калибр {caliber} мм, перезарядка {reload_:g} с, скорость {speed} км/ч"
    )


def format_show(entity: str, values: List[Tuple[str, str]]) -> str:
    """values — пары (id_or_key, подпись) для tank, иначе (ключ, ключ)."""
    if not values:
        return "Подходящих объектов не найдено."
    if entity == "tank":
        lines = [f"Найдено {len(values)} танк(ов):"]
        for idx, (tank_id, _) in enumerate(values, 1):
            lines.append(f"{idx}. {tank_line(tank_id)}")
        return "\n".join(lines)
    label = ENTITY_LABEL_RU.get(entity, entity)
    names = []
    for key, _ in values:
        if entity == "nation":
            names.append(NATION_RU.get(key, key))
        elif entity == "manufacturer":
            names.append(MANUFACTURER_RU.get(key, key))
        else:
            names.append(str(key))
    return f"В наличии {label}: {', '.join(names)}"


def format_recommend(entity: str, values: List[Tuple[str, str]],
                     conditions: List[Tuple[str, Optional[str | int]]],
                     level_hint: Optional[int]) -> str:
    if not values:
        return "Подходящих объектов не найдено."
    if entity != "tank":
        return format_show(entity, values)

    tank_id, _ = values[0]
    line = tank_line(tank_id)

    reasons = []
    kinds = {k for k, _ in conditions}
    if "alpha" in kinds:
        lvl = level_hint if level_hint is not None else 8
        alpha = ALL_ROWS[tank_id][4]
        reasons.append(f"самый высокий урон/выстрел на {lvl} уровне ({alpha})")
    if "speed" in kinds:
        speed = ALL_ROWS[tank_id][10]
        reasons.append(f"максимальная скорость ({speed} км/ч)")
    if "reload" in kinds:
        reload_ = ALL_ROWS[tank_id][9]
        reasons.append(f"минимальная перезарядка ({reload_:g} с)")
    if "specific" in kinds:
        reasons.append("подходит под указанное имя")
    if not reasons:
        reasons.append("подходит под все указанные условия")

    extra = ""
    if len(values) > 1 and not (kinds & {"alpha", "speed", "reload"}):
        extra = f" (из {len(values)} подходящих)"

    reason_text = ", ".join(reasons)
    return (
        f"Рекомендую: {ALL_ROWS[tank_id][7]}{extra}\n"
        f"Обоснование: {reason_text}.\n"
        f"{line}"
    )


def format_what_exists(entity: str, values: List[Tuple[str, str]]) -> str:
    return format_show(entity, values)


# ---------------------------------------------------------------------------
# Основной цикл
# ---------------------------------------------------------------------------

def execute(req: Dict) -> str:
    mode = req["mode"]
    entity = req["entity"]
    conditions = req["conditions"]

    candidates: Set[str] = set(ALL_IDS)
    level_hint: Optional[int] = None
    for kind, value in conditions:
        candidates, level_hint = filter_by(kind, value, candidates, level_hint)

    # упорядочим в порядке базы знаний
    ordered = [t for t in ALL_IDS if t in candidates]

    if entity == "tank":
        values = [(t, tank_line(t)) for t in ordered]
    elif entity == "nation":
        seen: Set[str] = set()
        values = []
        for t in ordered:
            nat = ALL_ROWS[t][1]
            if nat not in seen:
                seen.add(nat)
                values.append((nat, ""))
    elif entity == "level":
        seen = set()
        values = []
        for t in ordered:
            lvl = ALL_ROWS[t][0]
            if lvl not in seen:
                seen.add(lvl)
                values.append((str(lvl), ""))
    elif entity == "manufacturer":
        seen = set()
        values = []
        for t in ordered:
            mfrs = prolog(f"tank_manufacturer({t}, M), writeln(M)")
            mfr = mfrs[0] if mfrs else None
            if mfr and mfr not in seen:
                seen.add(mfr)
                values.append((mfr, ""))
    else:
        values = []

    if mode == "show":
        return format_show(entity, values)
    if mode == "recommend":
        return format_recommend(entity, values, conditions, level_hint)
    return format_what_exists(entity, values)


def greet() -> None:
    print("=== Рекомендательная система танков (БЗ на Prolog) ===")
    print("Введите запрос на русском. Примеры:")
    print('  выведи танк нация советский тип тт лвл 8 с высокой альфой')
    print('  подскажи танк немецкий лвл 7 быстрый')
    print('  выведи танк американский скорострельный')
    print('  какой есть нации')
    print('  выведи танк конкретный танк ИС-3')
    print("Для выхода введите: exit | выход | quit (или EOF)")
    print()


def main() -> None:
    load_rows()
    build_name_index()
    greet()
    while True:
        try:
            text = input("> ")
        except EOFError:
            print()
            break
        if not text.strip():
            continue
        if text.strip().lower() in ("exit", "выход", "quit", "end_of_file"):
            break
        req = parse_request(text)
        print(execute(req))
        print()


if __name__ == "__main__":
    main()
