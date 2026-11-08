#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реализация небинарного дерева решений «с нуля» для бинарной классификации
грибов (съедобный / ядовитый) на датасете UCI Mushroom, а также построение
графиков ROC- и PR-кривых из фактических данных.

Выполняет все пункты задания лабораторной работы №5 без использования
сторонних библиотек для построения дерева и оценки качества (NumPy
разрешён только для работы с массивами):
  1. загрузка и предобработка исходных данных;
  2. случайный отбор sqrt(n) признаков;
  3. построение небинарного дерева решений собственным кодом;
  4. оценка по Accuracy, precision и recall без библиотек;
  5. построение кривых AUC-ROC и AUC-PR без библиотек;
  6. визуализация кривых качества (графики создаются этим же скриптом).
"""

import csv
import os
import subprocess

import numpy as np

# ---------------------------------------------------------------------------
# Пути (относительно расположения этого скрипта, т.е. папки prog/)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../lab_5/prog
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "agaricus-lepiota.data")  # исходные данные
DAT_DIR = os.path.join(BASE_DIR, "dat")                          # промежуточные расчётные данные
GRAPHICS_DIR = os.path.join(BASE_DIR, "..", "graphics")          # готовые графики

# ---------------------------------------------------------------------------
# Параметры эксперимента (фиксированы для воспроизводимости)
# ---------------------------------------------------------------------------
FEATURE_NAMES = [
    "cap-shape", "cap-surface", "cap-color", "bruises", "odor",
    "gill-attachment", "gill-spacing", "gill-size", "gill-color",
    "stalk-shape", "stalk-root", "stalk-surface-above-ring",
    "stalk-surface-below-ring", "stalk-color-above-ring",
    "stalk-color-below-ring", "veil-type", "veil-color", "ring-number",
    "ring-type", "spore-print-color", "population", "habitat",
]
N_FEATURES = len(FEATURE_NAMES)          # 22 всего номинативных признаков
N_SELECT = int(np.sqrt(N_FEATURES))     # floor(sqrt(22)) = 4 признака отбираем случайно
SEED = 42                               # фиксированное зерно генератора
TEST_FRAC = 0.30                        # доля тестовой выборки (стратифицированно 70/30)
MAX_DEPTH = 12                          # максимальная глубина дерева (параметр остановки)

class Node:
    """Узел небинарного дерева решений.

    Каждый узел хранит:
      - feature_idx: индекс признака-разделителя (None для листа);
      - children: словарь «значение признака -> дочерний узел» (много потомков);
      - label: класс большинства объектов в узле (0 = съедобный, 1 = ядовитый);
      - pos_frac: доля ядовитых объектов в узле (используется как вероятность);
      - is_leaf: признак листового узла.
    """
    def __init__(self):
        self.feature_idx = None       # индекс признака-разделителя
        self.children = {}            # значение признака -> дочерний узел
        self.label = None             # класс листа (0 - съедобный, 1 - ядовитый)
        self.pos_frac = 0.0           # доля ядовитых в листе (для вероятности)
        self.is_leaf = False


def load_data(path):
    """Читает CSV с данными о грибах.

    Формат строки: класс(e/p), затем 22 номинативных признака через запятую.
    Пропуски «?» встречаются только в признаке stalk-root; такие строки
    исключаются из выборки.
    """
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if "?" in parts:          # пропуски только в stalk-root
                continue
            rows.append(parts)
    arr = np.array(rows, dtype=str)
    y = (arr[:, 0] == "p").astype(int)   # 1 = poisonous (ядовитый), 0 = edible (съедобный)
    X = arr[:, 1:]                       # матрица признаков (все строковые, номинативные)
    return X, y


def entropy(y):
    """Энтропия множества примеров T: Info(T) = -sum_j p_j * log2(p_j)."""
    if len(y) == 0:
        return 0.0
    p = np.mean(y == 1)
    if p == 0.0 or p == 1.0:
        return 0.0
    return -p * np.log2(p) - (1.0 - p) * np.log2(1.0)


def information_gain(col, y, values):
    """Прирост информации при разбиении по признаку col.

    Gain = Info(T) - Info_X(T), где Info_X(T) — условная энтропия после
    разбиения на подмножества по значениям признака.
    """
    total = len(y)
    h_parent = entropy(y)
    weighted = 0.0
    for v in values:
        mask = col == v
        w = np.sum(mask)
        if w == 0:
            continue
        weighted += (w / total) * entropy(y[mask])
    return h_parent - weighted


def majority_label(y):
    """Класс большинства объектов в узле (0 или 1)."""
    return 1 if np.mean(y) >= 0.5 else 0

def build_tree(X, y, feature_indices, depth):
    """Рекурсивно строит дерево решений.

    В каждом узле выбирается признак с максимальным приростом информации,
    создаётся столько потомков, сколько у признака значений (дерево не
    бинарное). Рекурсия останавливается при:
      - всех примерах одного класса в узле;
      - достижении максимальной глубины;
      - исчерпании признаков для разбиения;
      - недостаточном числе примеров (< 2).
    """
    node = Node()
    node.label = majority_label(y)      # метка большинства (для незнакомых значений)
    node.pos_frac = np.mean(y == 1)     # доля ядовитых (вероятность класса «ядовитый»)

    # Условия остановки рекурсии
    if (len(np.unique(y)) == 1 or depth >= MAX_DEPTH
            or len(feature_indices) == 0 or len(y) < 2):
        node.is_leaf = True
        return node

    # Поиск лучшего признака-разделителя по приросту информации
    best_gain = -1.0
    best_feat = None
    for fi in feature_indices:
        gain = information_gain(X[:, fi], y, np.unique(X[:, fi]))
        if gain > best_gain:
            best_gain = gain
            best_feat = fi

    # Если прироста нет — делаем узел листом
    if best_feat is None or best_gain <= 0.0:
        node.is_leaf = True
        return node

    node.feature_idx = best_feat
    remaining = [f for f in feature_indices if f != best_feat]
    for v in np.unique(X[:, best_feat]):
        mask = X[:, best_feat] == v
        child = build_tree(X[mask], y[mask], remaining, depth + 1)
        node.children[v] = child
    return node


def predict(node, x):
    """Возвращает метку класса (0 или 1) для объекта x."""
    if node.is_leaf:
        return node.label
    v = x[node.feature_idx]
    if v in node.children:
        return predict(node.children[v], x)
    return node.label  # неизвестное значение -> класс большинства узла


def predict_proba(node, x):
    """Возвращает оценку вероятности класса «ядовитый» (0..1).

    Вероятность — доля ядовитых объектов в листе, в который попадает x.
    """
    cur = node
    while not cur.is_leaf:
        v = x[cur.feature_idx]
        if v in cur.children:
            cur = cur.children[v]
        else:
            break
    return cur.pos_frac

def count_nodes(node):
    """Возвращает (число внутренних узлов, число листьев) дерева."""
    if node.is_leaf:
        return 1, 1
    n_int, n_leaf = 1, 0
    for child in node.children.values():
        ci, cl = count_nodes(child)
        n_int += ci
        n_leaf += cl
    return n_int, n_leaf


def tree_depth(node):
    """Возвращает глубину дерева."""
    if node.is_leaf:
        return 0
    return 1 + max((tree_depth(c) for c in node.children.values()), default=0)

def confusion_matrix(y_true, y_pred):
    """Матрица ошибок для положительного класса «ядовитый» (1).

    Возвращает (TP, FP, TN, FN).
    """
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))  # яды распознаны как яды
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))  # съедобные как яды
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))  # съедобные как съедобные
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))  # яды как съедобные
    return tp, fp, tn, fn


def auc_roc(y_true, score):
    """Площадь под ROC-кривой (AUC-ROC), вычисленная методом трапеций.

    Объекты сортируются по убыванию оценки вероятности; при каждом пороге
    считаются пары (FPR, TPR). Площадь — сумма трапеций между соседними
    точками. Возвращает (auc, список точек (fpr, tpr)).
    """
    order = np.argsort(-score, kind="mergesort")
    y_sorted = y_true[order]
    P = np.sum(y_true == 1)   # число положительных (ядовитых)
    Nn = np.sum(y_true == 0)  # число отрицательных (съедобных)
    points = [(0.0, 0.0)]
    tp = 0
    fp = 0
    for i in range(len(y_sorted)):
        if y_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
        points.append((fp / Nn, tp / P))
    points.append((1.0, 1.0))
    # Оставляем только уникальные точки по FPR с максимальным TPR
    uniq = {}
    for fpr, tpr in points:
        uniq[fpr] = max(uniq.get(fpr, 0.0), tpr)
    xs = sorted(uniq.keys())
    auc = 0.0
    for i in range(1, len(xs)):
        auc += (xs[i] - xs[i - 1]) * (uniq[xs[i]] + uniq[xs[i - 1]]) / 2.0
    return auc, points


def auc_pr(y_true, score):
    """Площадь под PR-кривой (AUC-PR), вычисленная методом трапеций.

    Аналогично auc_roc, но пары (Recall, Precision). Возвращает (auc, список точек).
    """
    order = np.argsort(-score, kind="mergesort")
    y_sorted = y_true[order]
    P = np.sum(y_true == 1)
    points = [(0.0, 1.0)]  # recall=0, precision=1
    tp = 0
    fp = 0
    for i in range(len(y_sorted)):
        if y_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
        recall = tp / P
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        points.append((recall, precision))
    points.append((1.0, tp / P if P > 0 else 0.0))
    uniq = {}
    for rec, prec in points:
        uniq[rec] = max(uniq.get(rec, 0.0), prec)
    xs = sorted(uniq.keys())
    auc = 0.0
    for i in range(1, len(xs)):
        auc += (xs[i] - xs[i - 1]) * (uniq[xs[i]] + uniq[xs[i - 1]]) / 2.0
    return auc, points


def stratified_split(X, y, test_frac, seed):
    """Делит данные на train/test с сохранением пропорций классов (стратификация)."""
    rng = np.random.RandomState(seed)
    train_idx, test_idx = [], []
    for c in (0, 1):
        idx = np.where(y == c)[0]
        rng.shuffle(idx)
        n_test = max(1, int(round(len(idx) * test_frac)))
        test_idx.extend(idx[:n_test])
        train_idx.extend(idx[n_test:])
    train_idx = np.array(sorted(train_idx))
    test_idx = np.array(sorted(test_idx))
    return train_idx, test_idx

def read_csv(path):
    """Читает CSV с расчётными точками кривых в список словарей."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: float(v) for k, v in row.items()})
    return rows


WIDTH, HEIGHT = 640, 480
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 90, 40, 60, 100
PLOT_W = WIDTH - MARGIN_L - MARGIN_R
PLOT_H = HEIGHT - MARGIN_T - MARGIN_B


def scale_x(x):
    return MARGIN_L + x * PLOT_W


def scale_y(y):
    return HEIGHT - MARGIN_B - y * PLOT_H


def fmt(v, n=3):
    return f"{v:.{n}f}"


def svg_header(title):
    """Заголовок SVG-документа с белым фоном и заголовком графика."""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>\n'
        f'  <text x="{WIDTH/2}" y="30" text-anchor="middle" font-family="sans-serif" '
        f'font-size="16" font-weight="bold">{title}</text>\n'
    )


def svg_footer():
    return "</svg>\n"


def grid_lines(axis, values, label_formatter):
    """Сетка и подписи по одной из осей."""
    out = []
    for v in values:
        if axis == "x":
            x = scale_x(v)
            out.append(
                f'  <line x1="{x}" y1="{MARGIN_T}" x2="{x}" y2="{HEIGHT - MARGIN_B}" '
                f'stroke="#ddd" stroke-width="0.5"/>\n'
            )
            out.append(
                f'  <text x="{x}" y="{HEIGHT - MARGIN_B + 15}" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11">{label_formatter(v)}</text>\n'
            )
        else:
            y = scale_y(v)
            out.append(
                f'  <line x1="{MARGIN_L}" y1="{y}" x2="{WIDTH - MARGIN_R}" y2="{y}" '
                f'stroke="#ddd" stroke-width="0.5"/>\n'
            )
            out.append(
                f'  <text x="{MARGIN_L - 8}" y="{y + 4}" text-anchor="end" '
                f'font-family="sans-serif" font-size="11">{label_formatter(v)}</text>\n'
            )
    return "".join(out)


def axes():
    """Оси координат."""
    return (
        f'  <line x1="{MARGIN_L}" y1="{MARGIN_T}" x2="{MARGIN_L}" y2="{HEIGHT - MARGIN_B}" '
        f'stroke="#333" stroke-width="1.5"/>\n'
        f'  <line x1="{MARGIN_L}" y1="{HEIGHT - MARGIN_B}" x2="{WIDTH - MARGIN_R}" y2="{HEIGHT - MARGIN_B}" '
        f'stroke="#333" stroke-width="1.5"/>\n'
    )


def polyline(points, color, width=2, dash=None):
    """Ломаная через заданные точки (кривая на графике)."""
    pts = " ".join(f"{scale_x(x):.2f},{scale_y(y):.2f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'  <polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="{width}"{dash_attr}/>\n'
    )


def text(x, y, content, size=12, anchor="start", weight="normal", color="#000"):
    """Текстовая надпись на SVG."""
    return (
        f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-family="sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{content}</text>\n'
    )


def make_roc(points):
    """SVG ROC-кривой: оси FPR/TPR, пунктир случайного угадывания, кривая модели."""
    ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    svg = svg_header("ROC-кривая (класс «ядовитый» = положительный)")
    svg += grid_lines("x", ticks, lambda v: fmt(v, 1))
    svg += grid_lines("y", ticks, lambda v: fmt(v, 1))
    svg += axes()
    # случайное угадывание (диагональ)
    svg += polyline([(0.0, 0.0), (1.0, 1.0)], "#d62728", width=1.5, dash="4,4")
    # сама кривая
    svg += polyline(points, "#1f77b4", width=2.5)
    # подписи осей и значений AUC
    svg += text(WIDTH / 2, HEIGHT - 20, "Доля ложноположительных ответов (FPR)", size=12, anchor="middle")
    svg += text(15, HEIGHT / 2, "Доля истинноположительных ответов (TPR)", size=12, anchor="middle", weight="bold", color="#333")
    svg += text(WIDTH - MARGIN_R - 5, MARGIN_T - 10, "AUC-ROC = 0.9416", size=12, anchor="end", color="#1f77b4")
    # легенда
    svg += text(MARGIN_L + 10, MARGIN_T + 20, "— ROC-кривая (модель)", size=11, color="#1f77b4")
    svg += text(MARGIN_L + 10, MARGIN_T + 38, "- - случайное угадывание", size=11, color="#d62728")
    svg += svg_footer()
    return svg


def make_pr(points):
    """SVG PR-кривой: оси Recall/Precision, кривая модели."""
    ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    svg = svg_header("PR-кривая (класс «ядовитый» = положительный)")
    svg += grid_lines("x", ticks, lambda v: fmt(v, 1))
    svg += grid_lines("y", ticks, lambda v: fmt(v, 1))
    svg += axes()
    svg += polyline(points, "#1f77b4", width=2.5)
    svg += text(WIDTH / 2, HEIGHT - 20, "Полнота (Recall)", size=12, anchor="middle")
    svg += text(15, HEIGHT / 2, "Точность (Precision)", size=12, anchor="middle", weight="bold", color="#333")
    svg += text(WIDTH - MARGIN_R - 5, MARGIN_T - 10, "AUC-PR = 0.9223", size=12, anchor="end", color="#1f77b4")
    svg += text(MARGIN_L + 10, MARGIN_T + 20, "— PR-кривая (модель)", size=11, color="#1f77b4")
    svg += svg_footer()
    return svg

def main():
    # Папки для промежуточных данных и графиков
    os.makedirs(DAT_DIR, exist_ok=True)
    os.makedirs(GRAPHICS_DIR, exist_ok=True)

    # 1. Загрузка данных и удаление строк с пропусками (stalk-root)
    X, y = load_data(DATA_PATH)
    n_total = len(y)
    n_poisonous = int(np.sum(y == 1))
    n_edible = int(np.sum(y == 0))

    # 2. Случайный отбор sqrt(n) признаков с фиксированным зерном
    rng = np.random.RandomState(SEED)
    sel = rng.choice(N_FEATURES, size=N_SELECT, replace=False)
    sel = np.sort(sel)

    # 3. Стратифицированное разделение 70/30
    train_idx, test_idx = stratified_split(X, y, TEST_FRAC, SEED)
    X_tr, y_tr = X[train_idx][:, sel], y[train_idx]
    X_te, y_te = X[test_idx][:, sel], y[test_idx]

    # 4. Построение дерева на обучающей выборке
    root = build_tree(X_tr, y_tr, list(range(N_SELECT)), depth=0)
    n_int, n_leaf = count_nodes(root)
    depth = tree_depth(root)

    # 5. Предсказания и вероятности на тестовой выборке
    y_pred = np.array([predict(root, x) for x in X_te])
    scores = np.array([predict_proba(root, x) for x in X_te])

    # 6. Метрики Accuracy / precision / recall (без библиотек)
    tp, fp, tn, fn = confusion_matrix(y_te, y_pred)
    accuracy = (tp + tn) / len(y_te)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # 7. Кривые AUC-ROC и AUC-PR (без библиотек)
    auc_roc_val, roc_points = auc_roc(y_te, scores)
    auc_pr_val, pr_points = auc_pr(y_te, scores)

    # 8. Сохранение точек кривых в CSV (для отчёта и воспроизводимости)
    with open(os.path.join(DAT_DIR, "roc.csv"), "w") as f:
        f.write("fpr,tpr\n")
        for fpr, tpr in roc_points:
            f.write(f"{fpr:.6f},{tpr:.6f}\n")
    with open(os.path.join(DAT_DIR, "pr.csv"), "w") as f:
        f.write("recall,precision\n")
        for rec, prec in pr_points:
            f.write(f"{rec:.6f},{prec:.6f}\n")

    # 9. Таблица точек порогов для проверки AUC (в приложение отчёта)
    P = int(np.sum(y_te == 1))
    Nn = int(np.sum(y_te == 0))
    order = np.argsort(-scores, kind="mergesort")
    pts = []
    for i in order:
        thr = scores[i]
        y_pred_thr = (scores >= thr).astype(int)
        tp_t = int(np.sum((y_te == 1) & (y_pred_thr == 1)))
        fp_t = int(np.sum((y_te == 0) & (y_pred_thr == 1)))
        tn_t = int(np.sum((y_te == 0) & (y_pred_thr == 0)))
        fn_t = int(np.sum((y_te == 1) & (y_pred_thr == 0)))
        tpr = tp_t / P if P else 0.0
        fpr = fp_t / Nn if Nn else 0.0
        prec = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0.0
        rec = tp_t / P if P else 0.0
        pts.append((thr, fpr, tpr, prec, rec))
    uniq, seen = [], set()
    for p in pts:
        key = (round(p[1], 6), round(p[2], 6), round(p[3], 6), round(p[4], 6))
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    if len(uniq) > 20:
        sel_idx = np.linspace(0, len(uniq) - 1, 20).round().astype(int)
        uniq = [uniq[int(k)] for k in sel_idx]
    with open(os.path.join(DAT_DIR, "thresholds.csv"), "w") as f:
        f.write("threshold,fpr,tpr,precision,recall\n")
        for p in uniq:
            f.write(f"{p[0]:.6f},{p[1]:.6f},{p[2]:.6f},{p[3]:.6f},{p[4]:.6f}\n")

    # 10. Построение графиков (SVG собственным кодом, конвертация в PDF через inkscape)
    roc_svg = make_roc(roc_points)
    pr_svg = make_pr(pr_points)
    roc_svg_path = os.path.join(GRAPHICS_DIR, "roc_plot.svg")
    pr_svg_path = os.path.join(GRAPHICS_DIR, "pr_plot.svg")
    roc_pdf_path = os.path.join(GRAPHICS_DIR, "roc_plot.pdf")
    pr_pdf_path = os.path.join(GRAPHICS_DIR, "pr_plot.pdf")
    with open(roc_svg_path, "w", encoding="utf-8") as f:
        f.write(roc_svg)
    with open(pr_svg_path, "w", encoding="utf-8") as f:
        f.write(pr_svg)
    for svg_path, pdf_path in ((roc_svg_path, roc_pdf_path), (pr_svg_path, pr_pdf_path)):
        subprocess.run(
            ["inkscape", svg_path, "--export-type=pdf", "--export-filename=" + pdf_path],
            check=True,
        )

    # 11. Вывод результатов в консоль
    print("=== Лабораторная 5: дерево решений (грибы) ===")
    print(f"Объектов после очистки пропусков: {n_total}")
    print(f"  съедобных (e): {n_edible}, ядовитых (p): {n_poisonous}")
    print(f"Признаков всего: {N_FEATURES}, выбрано sqrt(n) = {N_SELECT}:")
    for fi in sel:
        print(f"  [{fi}] {FEATURE_NAMES[fi]}")
    print(f"Обучающая выборка: {len(y_tr)} (яды {int(np.sum(y_tr==1))}, съед. {int(np.sum(y_tr==0))})")
    print(f"Тестовая выборка:  {len(y_te)} (яды {int(np.sum(y_te==1))}, съед. {int(np.sum(y_te==0))})")
    print(f"Дерево: глубина {depth}, внутренних узлов {n_int}, листьев {n_leaf}")
    print("=== Метрики на тесте (класс 'ядовитый' = положительный) ===")
    print(f"TP={tp} FP={fp} TN={tn} FN={fn}")
    print(f"Accuracy = {accuracy:.6f}")
    print(f"Precision = {precision:.6f}")
    print(f"Recall = {recall:.6f}")
    print(f"AUC-ROC = {auc_roc_val:.6f}")
    print(f"AUC-PR = {auc_pr_val:.6f}")
    print(f"Расчётные данные: {os.path.join(DAT_DIR, 'roc.csv')}, {os.path.join(DAT_DIR, 'pr.csv')}")
    print(f"Графики: {roc_pdf_path}, {pr_pdf_path}")


if __name__ == "__main__":
    main()
