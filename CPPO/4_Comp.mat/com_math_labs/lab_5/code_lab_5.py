import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import os
import json

# ─────────────────────────── утилиты ──────────────────────────────────────────

def build_finite_diff_table(y: np.ndarray) -> np.ndarray:
    # Строит таблицу конечных разностей
    n = len(y)
    d = np.zeros((n, n))
    d[:, 0] = y.copy()
    for j in range(1, n):
        for i in range(n - j):
            d[i, j] = d[i + 1, j - 1] - d[i, j - 1]
    return d


def build_divided_diff_table(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    # Строит таблицу разделённых разностей.
    n = len(x)
    d = np.zeros((n, n))
    d[:, 0] = y.copy()
    for j in range(1, n):
        for i in range(n - j):
            d[i, j] = (d[i + 1, j - 1] - d[i, j - 1]) / (x[i + j] - x[i])
    return d


def print_finite_diff_table(x: np.ndarray, y: np.ndarray, d: np.ndarray) -> None:
    n = len(x)
    cols = ["xi", "yi"] + [f"Δ^{k}yi" for k in range(1, n)]
    widths = [6, 10] + [11] * (n - 1)
    header = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
    print(header)
    print("─" * len(header))
    for i in range(n):
        row = f"{x[i]:<6.3f}  {y[i]:<10.5f}"
        for j in range(1, n):
            if i + j <= n - 1:
                row += f"  {d[i,j]:<11.6f}"
            else:
                row += "  " + " " * 11
        print(row)


def print_divided_diff_table(x: np.ndarray, y: np.ndarray, d: np.ndarray) -> None:
    n = len(x)
    cols = ["xi", "f(xi)"] + [f"f[{k}-й]" for k in range(1, n)]
    widths = [6, 10] + [14] * (n - 1)
    header = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
    print(header)
    print("─" * len(header))
    for i in range(n):
        row = f"{x[i]:<6.3f}  {y[i]:<10.5f}"
        for j in range(1, n):
            if i + j <= n - 1:
                row += f"  {d[i,j]:<14.7f}"
            else:
                row += "  " + " " * 14
        print(row)


# ─────────────────────────── методы интерполяции ──────────────────────────────

def lagrange(x: np.ndarray, y: np.ndarray, X: float) -> float:
    #Интерполяционный многочлен Лагранжа.#
    n = len(x)
    result = 0.0
    for i in range(n):
        li = 1.0
        for j in range(n):
            if i != j:
                li *= (X - x[j]) / (x[i] - x[j])
        result += y[i] * li
    return result


def newton_forward(x: np.ndarray, d: np.ndarray, X: float) -> float:
    #1-я формула Ньютона (вперёд), равноотстоящие узлы.#
    h = x[1] - x[0]
    n = len(x)
    t = (X - x[0]) / h
    result = d[0, 0]
    coeff = 1.0
    for k in range(1, n):
        coeff *= (t - (k - 1)) / k
        result += coeff * d[0, k]
    return result


def newton_backward(x: np.ndarray, d: np.ndarray, X: float) -> float:
    #2-я формула Ньютона (назад), равноотстоящие узлы.#
    h = x[1] - x[0]
    n = len(x)
    t = (X - x[-1]) / h
    result = d[n - 1, 0]
    coeff = 1.0
    for k in range(1, n):
        # coefficients use d[n-1-k, k], indices from bottom
        coeff *= (t + (k - 1)) / k
        result += coeff * d[n - 1 - k, k]
    return result


def newton_divided(x: np.ndarray, d: np.ndarray, X: float) -> float:
    #Многочлен Ньютона с разделёнными разностями.#
    n = len(x)
    result = d[0, 0]
    prod = 1.0
    for k in range(1, n):
        prod *= (X - x[k - 1])
        result += d[0, k] * prod
    return result


def gauss_forward(x: np.ndarray, d: np.ndarray, X: float, i0: int) -> float:
    #1-я формула Гаусса (x > a), центр в узле i0.#
    h = x[1] - x[0]
    t = (X - x[i0]) / h
    # P = y0 + t*Δy0 + t(t-1)/2! * Δ²y_{-1} + (t+1)t(t-1)/3! * Δ³y_{-1} + ...
    result = d[i0, 0]
    result += t * d[i0, 1]
    result += t * (t - 1) / 2 * d[i0 - 1, 2]
    result += (t + 1) * t * (t - 1) / 6 * d[i0 - 1, 3]
    if i0 - 2 >= 0:
        result += (t + 1) * t * (t - 1) * (t - 2) / 24 * d[i0 - 2, 4]
    if i0 - 2 >= 0:
        result += (t + 2) * (t + 1) * t * (t - 1) * (t - 2) / 120 * d[i0 - 2, 5]
    return result


def gauss_backward(x: np.ndarray, d: np.ndarray, X: float, i0: int) -> float:
    #2-я формула Гаусса (x < a), центр в узле i0.#
    h = x[1] - x[0]
    t = (X - x[i0]) / h
    # P = y0 + t*Δy_{-1} + t(t+1)/2! * Δ²y_{-1} + (t+1)t(t-1)/3! * Δ³y_{-2} + ...
    result = d[i0, 0]
    result += t * d[i0 - 1, 1]
    result += t * (t + 1) / 2 * d[i0 - 1, 2]
    result += (t + 1) * t * (t - 1) / 6 * d[i0 - 2, 3]
    if i0 - 2 >= 0:
        result += (t + 2) * (t + 1) * t * (t - 1) / 24 * d[i0 - 2, 4]
    return result


def stirling(x: np.ndarray, d: np.ndarray, X: float, i0: int) -> float:
    #Формула Стирлинга (|t| <= 0.25).#
    h = x[1] - x[0]
    t = (X - x[i0]) / h

    result = d[i0, 0]
    result += t * (d[i0 - 1, 1] + d[i0, 1]) / 2
    result += t ** 2 / 2 * d[i0 - 1, 2]
    result += t * (t ** 2 - 1) / 6 * (d[i0 - 2, 3] + d[i0 - 1, 3]) / 2
    if i0 - 2 >= 0:
        result += t ** 2 * (t ** 2 - 1) / 24 * d[i0 - 2, 4]
    return result


def bessel(x: np.ndarray, d: np.ndarray, X: float, i0: int) -> float:
    #Формула Бесселя (0.25 <= |t| <= 0.75).#
    h = x[1] - x[0]
    t = (X - x[i0]) / h
    result = (d[i0, 0] + d[i0 + 1, 0]) / 2
    result += (t - 0.5) * d[i0, 1]
    result += t * (t - 1) / 2 * (d[i0 - 1, 2] + d[i0, 2]) / 2
    result += (t - 0.5) * t * (t - 1) / 6 * d[i0 - 1, 3]
    if i0 - 2 >= 0:
        result += t * (t - 1) * (t + 1) * (t - 2) / 24 * (d[i0 - 2, 4] + d[i0 - 1, 4]) / 2
    return result


# ───────────────────────── автоматический выбор метода ────────────────────────

def choose_newton_method(x: np.ndarray, X: float) -> str:
    mid = (x[0] + x[-1]) / 2
    return "forward" if X <= mid else "backward"


def choose_gauss_method(x: np.ndarray, X: float) -> tuple:

    #Выбирает узел a так, чтобы |t| = |X-a|/h был минимальным,
    #при этом нужно иметь достаточно узлов с обеих сторон.#
    h = x[1] - x[0]
    n = len(x)
    best_idx = 2
    best_abs_t = float('inf')
    for i in range(2, n - 2):
        t = (X - x[i]) / h
        if abs(t) < best_abs_t:
            best_abs_t = abs(t)
            best_idx = i
    t = (X - x[best_idx]) / h
    direction = "forward" if t >= 0 else "backward"
    return best_idx, direction


# ─────────────────────────── чтение данных ────────────────────────────────────

VARIANT2_X = np.array([0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80])
VARIANT2_Y = np.array([1.5320, 2.5356, 3.5406, 4.5462, 5.5504, 6.5559, 7.5594])

BUILTIN_FUNCTIONS = {
    "1": ("sin(x)", np.sin),
    "2": ("cos(x)", np.cos),
    "3": ("exp(x)", np.exp),
    "4": ("ln(x+1)", lambda t: np.log(t + 1)),
    "5": ("x^2 + 2x", lambda t: t ** 2 + 2 * t),
}


def input_from_keyboard() -> tuple:
    print("\nВведите количество узлов интерполяции:")
    n = int(input("> ").strip())
    x_vals = []
    y_vals = []
    print("Введите пары (xi yi) через пробел:")
    for i in range(n):
        parts = input(f"  x[{i}] y[{i}]: ").strip().split()
        x_vals.append(float(parts[0]))
        y_vals.append(float(parts[1]))
    return np.array(x_vals), np.array(y_vals)


def input_from_file() -> tuple:
    print("\nВведите путь к файлу (JSON: {\"x\":[...], \"y\":[...]} или два столбца):")
    path = input("> ").strip()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")
    with open(path) as f:
        content = f.read().strip()
    if content.startswith("{"):
        data = json.loads(content)
        return np.array(data["x"]), np.array(data["y"])
    else:
        rows = [line.split() for line in content.splitlines() if line.strip()]
        x_vals = [float(r[0]) for r in rows]
        y_vals = [float(r[1]) for r in rows]
        return np.array(x_vals), np.array(y_vals)


def input_from_function() -> tuple:
    print("\nДоступные функции:")
    for k, (name, _) in BUILTIN_FUNCTIONS.items():
        print(f"  {k}. {name}")
    choice = input("Выберите функцию: ").strip()
    if choice not in BUILTIN_FUNCTIONS:
        raise ValueError("Неверный выбор функции")
    fname, func = BUILTIN_FUNCTIONS[choice]
    a = float(input("Начало интервала a: ").strip())
    b = float(input("Конец интервала b: ").strip())
    n = int(input("Число точек n (>=4): ").strip())
    x_vals = np.linspace(a, b, n)
    y_vals = func(x_vals)
    print(f"Функция: {fname} на [{a}, {b}], {n} точек")
    return x_vals, y_vals


# ──────────────────────────── графики ─────────────────────────────────────────

def plot_results(x: np.ndarray, y: np.ndarray, X_vals: list[float],
                 results: dict, title: str, filename: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x_dense = np.linspace(x[0], x[-1], 400)

    # Left: all interpolation curves
    ax = axes[0]
    ax.plot(x, y, 'ko', markersize=7, label='Узлы интерполяции', zorder=5)

    colors = ['#E74C3C', '#2980B9', '#27AE60', '#8E44AD', '#F39C12', '#16A085']
    ci = 0
    for method_name, method_func in results["methods"].items():
        y_dense = np.array([method_func(xi) for xi in x_dense])
        ax.plot(x_dense, y_dense, color=colors[ci % len(colors)],
                linewidth=1.8, label=method_name)
        ci += 1

    for X in X_vals:
        ax.axvline(X, color='gray', linestyle='--', linewidth=0.8)

    ax.set_title("Кривые интерполяции")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Right: comparison bar chart
    ax2 = axes[1]
    method_names = list(results["values"].keys())
    x_groups = list(results["values"][method_names[0]].keys())
    bar_width = 0.8 / len(method_names)
    x_pos = np.arange(len(x_groups))

    for i, mname in enumerate(method_names):
        vals = [results["values"][mname][xk] for xk in x_groups]
        ax2.bar(x_pos + i * bar_width, vals, bar_width, label=mname,
                color=colors[i % len(colors)], alpha=0.8)

    ax2.set_xticks(x_pos + bar_width * (len(method_names) - 1) / 2)
    ax2.set_xticklabels([f"X={xk}" for xk in x_groups])
    ax2.set_title("Сравнение значений методов")
    ax2.set_ylabel("f(X)")
    ax2.legend(fontsize=8)
    ax2.grid(True, axis='y', alpha=0.3)

    fig.suptitle(title, fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n[График сохранён: {filename}]")


def plot_finite_diff(x: np.ndarray, d: np.ndarray, filename: str) -> None:
    #Тепловая карта таблицы конечных разностей.#
    n = len(x)
    mask = np.full((n, n), np.nan)
    for i in range(n):
        for j in range(n - i):
            mask[i, j] = d[i, j]

    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(mask, aspect='auto', cmap='coolwarm')
    plt.colorbar(im, ax=ax, label='Значение разности')
    ax.set_xticks(range(n))
    ax.set_xticklabels([f"Δ^{k}" for k in range(n)], fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"x={xi:.2f}" for xi in x], fontsize=9)
    ax.set_title("Таблица конечных разностей (тепловая карта)")
    for i in range(n):
        for j in range(n - i):
            ax.text(j, i, f"{d[i,j]:.4f}", ha='center', va='center',
                    fontsize=7, color='white' if abs(d[i, j]) > 2 else 'black')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[График сохранён: {filename}]")


# ──────────────────────────── основная логика ─────────────────────────────────

def run_interpolation(x: np.ndarray, y: np.ndarray, X_list: list[float],
                      methods_to_use: list[str], output_dir: str = ".") -> None:
    n = len(x)
    h_uniform = x[1] - x[0] if n > 1 else 1.0
    is_uniform = np.allclose(np.diff(x), h_uniform)

    print("\n" + "═" * 60)
    print("ТАБЛИЦА КОНЕЧНЫХ РАЗНОСТЕЙ (равноотстоящие)")
    print("═" * 60)
    d_fin = build_finite_diff_table(y)
    print_finite_diff_table(x, y, d_fin)

    print("\n" + "═" * 60)
    print("ТАБЛИЦА РАЗДЕЛЁННЫХ РАЗНОСТЕЙ")
    print("═" * 60)
    d_div = build_divided_diff_table(x, y)
    print_divided_diff_table(x, y, d_div)

    print("\n" + "═" * 60)
    print("РЕЗУЛЬТАТЫ ИНТЕРПОЛЯЦИИ")
    print("═" * 60)

    method_funcs = {}
    value_table = {}  # method -> {X -> value}

    for X in X_list:
        print(f"\n--- X = {X} ---")

        # Выбор методов и расчёт
        vals = {}

        # Lagrange
        if "lagrange" in methods_to_use:
            v = lagrange(x, y, X)
            vals["Лагранж"] = v
            print(f"  Лагранж:          {v:.8f}")

        # Newton divided differences
        if "newton_divided" in methods_to_use:
            v = newton_divided(x, d_div, X)
            vals["Ньютон (разд.)"] = v
            print(f"  Ньютон разд.:     {v:.8f}")

        # Newton finite differences — choose forward/backward
        if "newton_finite" in methods_to_use and is_uniform:
            direction = choose_newton_method(x, X)
            if direction == "forward":
                v = newton_forward(x, d_fin, X)
                vals[f"Ньютон вперёд"] = v
                t = (X - x[0]) / h_uniform
                print(f"  Ньютон вперёд (t={t:.4f}): {v:.8f}")
            else:
                v = newton_backward(x, d_fin, X)
                vals[f"Ньютон назад"] = v
                t = (X - x[-1]) / h_uniform
                print(f"  Ньютон назад (t={t:.4f}): {v:.8f}")

        # Gauss
        if "gauss" in methods_to_use and is_uniform:
            idx, direction = choose_gauss_method(x, X)
            h = h_uniform
            t = (X - x[idx]) / h
            if direction == "forward":
                v = gauss_forward(x, d_fin, X, idx)
                vals["Гаусс вперёд"] = v
                print(f"  Гаусс вперёд (a=x[{idx}]={x[idx]:.2f}, t={t:.4f}): {v:.8f}")
            else:
                v = gauss_backward(x, d_fin, X, idx)
                vals["Гаусс назад"] = v
                print(f"  Гаусс назад (a=x[{idx}]={x[idx]:.2f}, t={t:.4f}): {v:.8f}")

        # Stirling (bonus)
        if "stirling" in methods_to_use and is_uniform:
            idx, _ = choose_gauss_method(x, X)
            t = (X - x[idx]) / h_uniform
            if abs(t) <= 0.25:
                v = stirling(x, d_fin, X, idx)
                vals["Стирлинг"] = v
                print(f"  Стирлинг (|t|={abs(t):.4f}<=0.25): {v:.8f}")
            else:
                print(f"  Стирлинг: |t|={abs(t):.4f} > 0.25, пропущен")

        # Bessel (bonus)
        if "bessel" in methods_to_use and is_uniform:
            idx, _ = choose_gauss_method(x, X)
            t = (X - x[idx]) / h_uniform
            if 0.25 <= abs(t) <= 0.75 and idx + 1 < n:
                v = bessel(x, d_fin, X, idx)
                vals["Бессель"] = v
                print(f"  Бессель (|t|={abs(t):.4f} in [0.25,0.75]): {v:.8f}")
            else:
                print(f"  Бессель: |t|={abs(t):.4f} вне [0.25,0.75], пропущен")

        for mname, val in vals.items():
            if mname not in value_table:
                value_table[mname] = {}
            value_table[mname][X] = val

    # Build callable wrappers for plotting
    if "lagrange" in methods_to_use:
        method_funcs["Лагранж"] = lambda xi: lagrange(x, y, xi)

    if "newton_finite" in methods_to_use and is_uniform:
        def _nf(xi):
            d = choose_newton_method(x, xi)
            if d == "forward":
                return newton_forward(x, d_fin, xi)
            else:
                return newton_backward(x, d_fin, xi)
        method_funcs["Ньютон (кон. разн.)"] = _nf

    if "newton_divided" in methods_to_use:
        method_funcs["Ньютон (разд.)"] = lambda xi: newton_divided(x, d_div, xi)

    if "gauss" in methods_to_use and is_uniform:
        def _gauss(xi):
            idx, direction = choose_gauss_method(x, xi)
            if direction == "forward":
                return gauss_forward(x, d_fin, xi, idx)
            else:
                return gauss_backward(x, d_fin, xi, idx)
        method_funcs["Гаусс"] = _gauss

    # Comparison table
    print("\n" + "═" * 60)
    print("СВОДНАЯ ТАБЛИЦА СРАВНЕНИЯ")
    print("═" * 60)
    all_methods = list(value_table.keys())
    header = f"{'Метод':<22}" + "".join(f"  X={xv:<9.4f}" for xv in X_list)
    print(header)
    print("─" * len(header))
    for mname in all_methods:
        row = f"{mname:<22}"
        for X in X_list:
            row += f"  {value_table[mname].get(X, float('nan')):<11.8f}"
        print(row)

    # Save plots
    fname_curves = os.path.join(output_dir, "interpolation_curves.png")
    plot_results(x, y, X_list,
                 {"methods": method_funcs, "values": value_table},
                 "Интерполяция функции (Вариант 2)", fname_curves)

    fname_heat = os.path.join(output_dir, "finite_diff_heatmap.png")
    plot_finite_diff(x, d_fin, fname_heat)


# ──────────────────────────── меню ────────────────────────────────────────────

METHODS_MENU = {
    "1": "lagrange",
    "2": "newton_divided",
    "3": "newton_finite",
    "4": "gauss",
    "5": "stirling",
    "6": "bessel",
}
METHODS_LABEL = {
    "lagrange": "Многочлен Лагранжа",
    "newton_divided": "Ньютон (разделённые разности)",
    "newton_finite": "Ньютон (конечные разности, 1-я и 2-я формулы)",
    "gauss": "Гаусс (1-я и 2-я формулы)",
    "stirling": "Стирлинг",
    "bessel": "Бессель",
}


def select_methods() -> list[str]:
    print("\nДоступные методы:")
    for k, v in METHODS_MENU.items():
        print(f"  {k}. {METHODS_LABEL[v]}")
    print("  0. Все методы")
    choice = input("Выберите метод(ы) через пробел [0 — все]: ").strip()
    if choice == "0" or choice == "":
        return list(METHODS_MENU.values())
    selected = []
    for c in choice.split():
        if c in METHODS_MENU:
            selected.append(METHODS_MENU[c])
    return selected if selected else list(METHODS_MENU.values())


def main() -> None:
    print("╔════════════════════════════════════════════════════╗")
    print("║     Лабораторная работа №5: Интерполяция          ║")
    print("║     Вариант 2 — Таблица 1.2                       ║")
    print("╚════════════════════════════════════════════════════╝")

    # Output directory
    out_dir = "lab5_output"
    os.makedirs(out_dir, exist_ok=True)

    while True:
        print("\n" + "─" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("─" * 50)
        print("  1. Данные варианта 2 (Таблица 1.2, X1=0.502, X2=0.645)")
        print("  2. Ввести данные с клавиатуры")
        print("  3. Загрузить данные из файла")
        print("  4. Генерировать данные из встроенной функции")
        print("  0. Выход")
        choice = input("\nВыбор: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        try:
            if choice == "1":
                x_data = VARIANT2_X.copy()
                y_data = VARIANT2_Y.copy()
                X_query = [0.502, 0.645]
                print(f"\nИспользуются данные варианта 2.")
                print(f"X1 = 0.502, X2 = 0.645")

            elif choice == "2":
                x_data, y_data = input_from_keyboard()
                X_query = []
                print("Введите значения X для интерполяции (через пробел):")
                X_query = [float(v) for v in input("> ").strip().split()]

            elif choice == "3":
                x_data, y_data = input_from_file()
                print("Введите значения X для интерполяции (через пробел):")
                X_query = [float(v) for v in input("> ").strip().split()]

            elif choice == "4":
                x_data, y_data = input_from_function()
                print("Введите значения X для интерполяции (через пробел):")
                X_query = [float(v) for v in input("> ").strip().split()]

            else:
                print("Неверный выбор.")
                continue

            # Validate
            if len(x_data) < 3:
                print("Ошибка: нужно минимум 3 узла.")
                continue
            if not X_query:
                print("Ошибка: не задан X для интерполяции.")
                continue
            for X in X_query:
                if X < x_data[0] or X > x_data[-1]:
                    print(f"Предупреждение: X={X} выходит за пределы [{x_data[0]}, {x_data[-1]}] (экстраполяция)!")

            methods = select_methods()
            print(f"\nВыбранные методы: {', '.join(METHODS_LABEL[m] for m in methods)}")

            run_interpolation(x_data, y_data, X_query, methods, output_dir=out_dir)

        except (ValueError, IndexError, FileNotFoundError, KeyError) as e:
            print(f"\n[Ошибка]: {e}")
        except Exception as e:
            print(f"\n[Неожиданная ошибка]: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
