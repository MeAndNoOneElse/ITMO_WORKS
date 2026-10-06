from itertools import combinations

# ... (items, variants, и другие данные те же самые)
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
def pack_all_optimal(variant):
    rows, cols = variant["size"]
    capacity = rows * cols
    initial = variant["init"]
    must_label = variant["must"]

    must_items = [it for it in items if must_label and it["label"] == must_label]
    rem_items = [it for it in items if not (must_label and it["label"] == must_label)]

    candidates = []
    for n in range(len(rem_items) + 1):
        for combo in combinations(rem_items, n):
            total_size = sum(it["size"] for it in combo) + sum(it["size"] for it in must_items)
            if total_size <= capacity:
                candidates.append(list(combo) + must_items)
    # Найдём лучший результат (максимальный итог без учёта начальных очков)
    max_score = None
    best_variants = []
    for comb in candidates:
        packed_labels = [it["label"] for it in comb]
        score = initial
        for it in items:
            if it["label"] in packed_labels:
                score += it["score"]
            else:
                score -= it["score"]
        if (max_score is None) or (score > max_score):
            max_score = score
            best_variants = [comb]
        elif score == max_score:
            best_variants.append(comb)
    return best_variants, max_score

def show_all_optimal(variant_id):
    variant = variants[variant_id - 1]
    best_variants, max_score = pack_all_optimal(variant)
    if max_score < 0:
        print("Оптимальный результат всё ещё отрицательный:", max_score)
        print("Причина: не хватает места, обязательные предметы или стартовые очки слишком малы.")
    else:
        print(f"Оптимальный результат: {max_score} очков. Все возможные варианты раскладки:")
    for idx, comb in enumerate(best_variants, 1):
        # Формирование двумерного вывода
        slots = []
        temp = []
        rows, cols = variant["size"]
        slots_count = 0
        for it in comb:
            for _ in range(it["size"]):
                temp.append(f"[{it['label']}]")
                slots_count += 1
                if len(temp) == cols:
                    slots.append(temp)
                    temp = []
        if temp:
            while len(temp) < cols:
                temp.append(" ")
            slots.append(temp)
        print(f"\nВариант {idx}:")
        for row in slots:
            print("".join(row))
    print(f"Итоговые очки выживания: {max_score}")

# Использование
num = int(input("Введите номер варианта (1-10): "))
show_all_optimal(num)
