# Описание предметов (обозначение, размер, очки)
items = [
    {"name": "Винтовка", "label": "r", "size": 3, "score": 25},
    {"name": "Пистолет", "label": "p", "size": 2, "score": 15},
    {"name": "Боекомплект", "label": "a", "size": 2, "score": 15},
    {"name": "Аптечка", "label": "m", "size": 2, "score": 20},
    {"name": "Ингалятор", "label": "i", "size": 1, "score": 5},
    {"name": "Нож", "label": "k", "size": 1, "score": 15},
    {"name": "Топор", "label": "x", "size": 3, "score": 20},
    {"name": "Оберег", "label": "t", "size": 1, "score": 25},
    {"name": "Фляжка", "label": "f", "size": 1, "score": 15},
    {"name": "Антидот", "label": "d", "size": 1, "score": 10},
    {"name": "Еда", "label": "s", "size": 2, "score": 20},
    {"name": "Арбалет", "label": "c", "size": 2, "score": 20},
]

# Параметры вариантов (размеры, болезнь, стартовые очки)
variants = [
    {"size": (2, 4), "must": None,       "init": 15},  # 1
    {"size": (3, 3), "must": "i",        "init": 10},  # 2
    {"size": (2, 4), "must": "d",        "init": 10},  # 3
    {"size": (3, 3), "must": None,       "init": 15},  # 4
    {"size": (2, 4), "must": "i",        "init": 20},  # 5
    {"size": (3, 3), "must": "d",        "init": 15},  # 6
    {"size": (2, 4), "must": None,       "init": 15},  # 7
    {"size": (3, 3), "must": "i",        "init": 15},  # 8
    {"size": (2, 4), "must": "d",        "init": 20},  # 9
    {"size": (3, 3), "must": None,       "init": 10},  # 10
    {"size": (1, 7), "must": "d", "init": 20},  # 11

]

from itertools import combinations

def pack(variant):
    rows, cols = variant["size"]
    capacity = rows * cols
    initial = variant["init"]
    must_label = variant["must"]

    # Список предметов, обязательных для выбора
    must_items = []
    rem_items = []
    for it in items:
        if must_label and it["label"] == must_label:
            must_items.append(it)
        else:
            rem_items.append(it)
    # Все возможные комбинации предметов, кроме обязательных
    candidates = []
    for n in range(len(rem_items) + 1):
        for combo in combinations(rem_items, n):
            total_size = sum(it["size"] for it in combo) + sum(it["size"] for it in must_items)
            if total_size <= capacity:
                total_score = sum(it["score"] for it in combo) + sum(it["score"] for it in must_items)
                candidates.append((total_score, combo))
    if not candidates:
        # Если нет варианта кроме must_items
        best_combo = []
        best_score = 0
    else:
        best_score, best_combo = max(candidates, key=lambda x: x[0])
    # Финальный набор (с обязательными предметами)
    final_items = list(best_combo) + must_items
    # Для подсчёта по всем предметам: если не взяли, очки вычитаются
    packed_labels = [it["label"] for it in final_items]
    score = initial
    for it in items:
        if it["label"] in packed_labels:
            score += it["score"]
        else:
            score -= it["score"]
    # Формируем двумерный "инвентарь"
    slots = []
    temp = []
    used = []
    for it in final_items:
        for _ in range(it["size"]):
            temp.append(f"[{it['label']}]")
            used.append(it["label"])
            if len(temp) == cols:
                slots.append(temp)
                temp = []
    if temp:
        while len(temp) < cols:
            temp.append(" ")
        slots.append(temp)
    return slots, score

def show(variant_id):
    variant = variants[variant_id - 1]
    slots, score = pack(variant)
    print("Инвентарь:")
    for row in slots:
        print("".join(row))
    print(f"Итоговые очки выживания: {score}")
    if score < 0:
        print("Итоговые очки выживания оказались отрицательными.")
        print(
            "Причина: не удалось уместить в рюкзак достаточно ценных предметов при заданных условиях (размер, обязательные вещи и начальные очки).")
        print("Попробуйте увеличить размер рюкзака, стартовые очки или изменить набор обязательных предметов.")
# Пример использования: запрос варианта у пользователя
num = int(input("Введите номер варианта (1-10): "))
show(num)
