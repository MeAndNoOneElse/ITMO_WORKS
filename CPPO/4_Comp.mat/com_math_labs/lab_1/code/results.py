from solver import mat_vec_mul, vec_sub, vec_norm
from table_widget import ReportTab


def _fmt_cell(v, n):
    """Форматирует число для ячейки таблицы."""
    if n <= 9:
        return f"{v:.6f}"
    if n <= 15:
        return f"{v:.4f}"
    return f"{v:.3f}"


def _col_headers(n):
    return [f"x{j+1}" for j in range(n)] + ["b"]


def _matrix_to_tab(tab, matrix, n, kind="data"):
    """Рисует расширенную матрицу [A|b]"""
    tab.add_matrix_row(_col_headers(n), kind="col_hdr")
    for row in matrix:
        cells = [_fmt_cell(row[j], n) for j in range(n)] + [_fmt_cell(row[n], n)]
        tab.add_matrix_row(cells, kind=kind)


#  ВКЛАДКА «РЕШЕНИЕ»

def display_solution(tab: ReportTab, A, b, n, x, det, aug):
    tab.set_n(n)
    tab.clear()
    tab.begin_batch()

    tab.add_heading("РЕЗУЛЬТАТЫ РЕШЕНИЯ")
    tab.add_separator()

    tab.add_heading("Треугольная матрица (расширенная):", level=2)
    _matrix_to_tab(tab, aug, n)

    tab.add_separator(height=1)
    tab.add_kv_row("Определитель:", f"{det:.10f}", val_color="#ffcc02")

    tab.add_separator(height=1)
    tab.add_heading("Вектор неизвестных X:", level=2)
    for i, val in enumerate(x):
        tab.add_kv_row(f"  x{i+1}", f"{val:.10f}")

    Ax = mat_vec_mul(A, x)
    r  = vec_sub(Ax, b)
    tab.add_separator(height=1)
    tab.add_heading("Вектор невязки  r = A·x − b:", level=2)
    for i, val in enumerate(r):
        tab.add_kv_row(f"  r{i+1}", f"{val:.2e}", val_color="#c8e6c9")
    tab.add_kv_row("  ‖r‖ =", f"{vec_norm(r):.2e}", val_color="#c8e6c9")

    tab.end_batch()


#   «ПРЯМОЙ ХОД»

def display_forward(tab: ReportTab, forward_steps):
    # Определяем n: initial всегда имеет полную матрицу
    first_matrix = forward_steps[0][2] if forward_steps else None
    n = len(first_matrix[0]) - 1 if first_matrix else 1
    tab.set_n(n)
    tab.clear()
    tab.begin_batch()

    full_view = (n <= 9)

    tab.add_heading("ПРЯМОЙ ХОД  —  приведение к верхней треугольной форме")
    tab.add_separator()

    if not full_view:
        tab.add_info(
            f"ℹ  Матрица {n}×{n}: компактный режим — "
            f"показывается только изменённая строка на каждом шаге."
        )

    for kind, description, matrix in forward_steps:
        if kind == "initial":
            tab.add_text_line(f"▸ {description}", color="#69f0ae", bold=True)
            _matrix_to_tab(tab, matrix, n)

        elif kind == "swap":
            tab.add_separator(color="#1a3a5c", height=1)
            tab.add_text_line(f"🔀 {description}", color="#80d8ff", bold=True)
            if matrix is not None:
                _matrix_to_tab(tab, matrix, n, kind="data")

        elif kind == "pivot":
            tab.add_separator(color="#2d6a32", height=1)
            tab.add_text_line(f"▸ {description}", color="#ffcc02", bold=True)

        elif kind == "eliminate":
            tab.add_text_line(f"  ↳ {description}", color="#a5d6a7")

        elif kind == "result":
            tab.add_text_line(f"    {description}", color="#c8e6c9")
            if matrix is not None:
                if full_view:
                    _matrix_to_tab(tab, matrix, n, kind="data")
                elif isinstance(matrix, tuple) and matrix[0] == "row":
                    # ("row", j, row_data) — только одна строка
                    _, row_idx, row_data = matrix
                    values = [_fmt_cell(row_data[j], n) for j in range(n)] + \
                             [_fmt_cell(row_data[n], n)]
                    tab.add_compact_row(f"R{row_idx+1}:", values, kind="data")
                else:
                    # Полная матрица (не должна быть при n>9, но на всякий случай)
                    changed_rows = _find_changed_rows(description, n)
                    _add_changed_rows(tab, matrix, n, changed_rows)

        elif kind == "final":
            tab.add_separator()
            tab.add_text_line(f"✔ {description}", color="#00e676", bold=True)
            if matrix is not None:
                _matrix_to_tab(tab, matrix, n)

    tab.end_batch()


def _find_changed_rows(description: str, n: int) -> list:
    """
    Пытается определить номер изменённой строки из текста описания.
    Возвращает список индексов (0-based) изменившихся строк.
    """
    import re
    # Описание вида: "Результат после исключения x{i} из строки {j}"
    m = re.search(r'строки\s+(\d+)', description)
    if m:
        j = int(m.group(1)) - 1   # 0-based
        if 0 <= j < n:
            return [j]
    return list(range(n))   # не распознали — показываем все


def _add_changed_rows(tab, matrix, n, changed_rows):
    """Выводит только указанные строки матрицы в компактном виде."""
    for i in changed_rows:
        if i >= len(matrix):
            continue
        row = matrix[i]
        values = [_fmt_cell(row[j], n) for j in range(n)] + [_fmt_cell(row[n], n)]
        tab.add_compact_row(f"R{i+1}:", values, kind="data")


#   «ОБРАТНЫЙ ХОД»

def display_backward(tab: ReportTab, backward_steps, aug, n):
    tab.set_n(n)
    tab.clear()
    tab.begin_batch()

    full_formula = (n <= 9)

    tab.add_heading("ОБРАТНЫЙ ХОД  —  нахождение вектора неизвестных")
    tab.add_separator()

    tab.add_heading("Треугольная матрица (для обратного хода):", level=2)
    _matrix_to_tab(tab, aug, n)

    tab.add_separator()
    tab.add_text_line("Порядок вычисления: снизу вверх", color="#81c784", bold=True)
    tab.add_separator(height=1)

    if not full_formula:
        tab.add_info(
            f"ℹ  Матрица {n}×{n}: компактный режим — "
            f"показан результат каждого шага."
        )

    for idx, (row_i, val, formula, numeric, _) in enumerate(backward_steps):
        step_num = len(backward_steps) - idx
        if full_formula:
            tab.add_formula_row(
                step_label=f"Шаг {step_num}",
                formula=formula,
                numeric=numeric,
                result=f"x{row_i+1} = {val:.10f}"
            )
        else:
            tab.add_compact_row(
                row_label=f"#{step_num}",
                values=[f"x{row_i+1}", f"{val:.10f}",
                        f"a[{row_i+1},{row_i+1}]={aug[row_i][row_i]:.4f}"],
                kind="answer",
                label_color="#ffcc02"
            )

    tab.add_separator()
    tab.add_heading("ИТОГ: вектор неизвестных X", level=2)
    ordered = sorted(backward_steps, key=lambda t: t[0])
    tab.add_matrix_row(["Переменная", "Значение"], kind="col_hdr")
    for row_i, val, _, _, _ in ordered:
        tab.add_matrix_row([f"x{row_i+1}", f"{val:.10f}"], kind="answer")

    tab.end_batch()


def display_comparison(tab: ReportTab, A, b, n, x_gauss, det_gauss):
    import numpy as _np
    A_np   = _np.array(A)
    b_np   = _np.array(b)
    x_np   = _np.linalg.solve(A_np, b_np)
    det_np = _np.linalg.det(A_np)

    tab.set_n(3)
    tab.clear()
    tab.begin_batch()

    tab.add_heading("СРАВНЕНИЕ С NUMPY")
    tab.add_separator()

    tab.add_matrix_row(["Переменная", "Метод Гаусса", "NumPy", "|Δ|"], kind="col_hdr")

    max_diff = 0.0
    for i in range(n):
        diff = abs(x_gauss[i] - x_np[i])
        max_diff = max(max_diff, diff)
        tab.add_matrix_row(
            [f"x{i+1}", f"{x_gauss[i]:.8f}", f"{x_np[i]:.8f}", f"{diff:.2e}"],
            kind="data"
        )

    tab.add_separator()
    tab.add_kv_row("Макс. разность:",        f"{max_diff:.2e}")
    tab.add_kv_row("Определитель (Гаусс):",  f"{det_gauss:.10f}")
    tab.add_kv_row("Определитель (NumPy):",  f"{det_np:.10f}")
    tab.add_kv_row("Δ определителей:",       f"{abs(det_gauss - det_np):.2e}")

    tab.add_separator()
    tab.add_heading("АНАЛИЗ РАЗЛИЧИЙ", level=2)
    for line in [
        "1. ПОГРЕШНОСТИ ОКРУГЛЕНИЯ:",
        "   В методе Гаусса происходит накопление погрешностей при",
        "   последовательных арифметических операциях.",
        "   NumPy использует LUP-разложение с выбором главного элемента.",
        "",
        "2. РАЗЛИЧИЯ В АЛГОРИТМАХ:",
        "   Реализованный метод — схема с частичным выбором ведущего элемента (partial pivoting).",
        "   NumPy использует LUP-разложение с аналогичным выбором главного элемента.",
        "",
        "3. МАШИННАЯ ТОЧНОСТЬ:",
        "   Все вычисления — двойная точность (~15–16 знаков).",
        "   Погрешность порядка 10⁻¹⁵ считается приемлемой.",
    ]:
        tab.add_text_line(line, color="#c8e6c9")

    tab.add_separator(height=1)
    if max_diff > 1e-10:
        tab.add_text_line("⚠  ВНИМАНИЕ: разность решений превышает 10⁻¹⁰",
                          color="#ff8a65", bold=True)
        tab.add_text_line("   Это может указывать на плохую обусловленность матрицы.",
                          color="#ff8a65")
    else:
        tab.add_text_line("✔  Решения хорошо согласуются (разность < 10⁻¹⁰)",
                          color="#00e676", bold=True)

    tab.end_batch()
