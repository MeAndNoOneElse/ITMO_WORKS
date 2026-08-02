"""
Лабораторная работа №4
Аппроксимация функции методом наименьших квадратов
Вариант 2: y = 15x / (x^4 + 2), x in [0, 4], h = 0.4
"""

import math
import sys


#  Вспомогательные функции: СЛАУ методом Гаусса


def gauss_solve(A, b):
    """Решение системы Ax = b методом Гаусса с выбором ведущего элемента."""
    n = len(b)
    # Расширенная матрица
    M = [[A[i][j] for j in range(n)] + [b[i]] for i in range(n)]

    for col in range(n):
        # Выбор ведущего элемента
        max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[max_row] = M[max_row], M[col]

        if abs(M[col][col]) < 1e-15:
            raise ValueError("Матрица вырождена или близка к вырожденной")

        for row in range(col + 1, n):
            factor = M[row][col] / M[col][col]
            for j in range(col, n + 1):
                M[row][j] -= factor * M[col][j]

    # Обратный ход
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = M[i][n]
        for j in range(i + 1, n):
            x[i] -= M[i][j] * x[j]
        x[i] /= M[i][i]
    return x



#  Методы аппроксимации МНК


def lsq_polynomial(xs, ys, degree):
    """
    МНК-аппроксимация полиномом степени degree.
    Возвращает коэффициенты [a0, a1, ..., a_m] (от меньшей степени к большей).
    """
    n = len(xs)
    m = degree
    # Формируем систему (m+1) x (m+1)
    A = [[0.0] * (m + 1) for _ in range(m + 1)]
    b = [0.0] * (m + 1)

    for i in range(m + 1):
        for j in range(m + 1):
            A[i][j] = sum(xs[k] ** (i + j) for k in range(n))
        b[i] = sum(ys[k] * xs[k] ** i for k in range(n))

    return gauss_solve(A, b)


def poly_eval(coeffs, x):
    return sum(coeffs[i] * x ** i for i in range(len(coeffs)))


def lsq_exponential(xs, ys):
    """
    МНК для phi(x) = a * e^(bx).
    Линеаризация: ln(y) = ln(a) + b*x => Y = A + Bx.
    """
    filtered = [(x, y) for x, y in zip(xs, ys) if y > 0]
    if len(filtered) < 2:
        raise ValueError("Недостаточно точек с y > 0 для экспоненциальной аппроксимации")
    xs_f = [p[0] for p in filtered]
    ys_f = [math.log(p[1]) for p in filtered]
    coeffs = lsq_polynomial(xs_f, ys_f, 1)
    A, B = coeffs[0], coeffs[1]
    a = math.exp(A)
    b = B
    return a, b


def lsq_power(xs, ys):
    """
    МНК для phi(x) = a * x^b.
    Линеаризация: ln(y) = ln(a) + b*ln(x) => Y = A + B*X.

    """
    filtered = [(x, y) for x, y in zip(xs, ys) if x > 0 and y > 0]
    if len(filtered) < 2:
        raise ValueError("Недостаточно точек с x>0 и y>0 для степенной аппроксимации")
    xs_f = [math.log(p[0]) for p in filtered]
    ys_f = [math.log(p[1]) for p in filtered]
    coeffs = lsq_polynomial(xs_f, ys_f, 1)
    A, B = coeffs[0], coeffs[1]
    a = math.exp(A)
    b = B
    return a, b


def lsq_logarithmic(xs, ys):
    """
    МНК для phi(x) = a * ln(x) + b.
    Линеаризация: X = ln(x), Y = y => Y = aX + b.
    
    """
    filtered = [(x, y) for x, y in zip(xs, ys) if x > 0]
    if len(filtered) < 2:
        raise ValueError("Недостаточно точек с x>0 для логарифмической аппроксимации")
    xs_f = [math.log(p[0]) for p in filtered]
    ys_f = [p[1] for p in filtered]
    coeffs = lsq_polynomial(xs_f, ys_f, 1)
    b, a = coeffs[0], coeffs[1]
    return a, b



#  Метрики качества


def compute_metrics(xs, ys, phi_vals):
    """Вычисляет S, delta, R^2."""
    n = len(xs)
    eps = [phi_vals[i] - ys[i] for i in range(n)]
    S = sum(e ** 2 for e in eps)
    delta = math.sqrt(S / n)

    phi_mean = sum(phi_vals) / n
    ss_res = sum((ys[i] - phi_vals[i]) ** 2 for i in range(n))
    ss_tot = sum((ys[i] - phi_mean) ** 2 for i in range(n))
    R2 = 1 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0
    return S, delta, R2, eps


def pearson_r(xs, ys):
    """Коэффициент корреляции Пирсона."""
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    den = math.sqrt(
        sum((xs[i] - x_mean) ** 2 for i in range(n)) *
        sum((ys[i] - y_mean) ** 2 for i in range(n))
    )
    return num / den if den > 1e-15 else 0.0


def r2_description(R2):
    if R2 >= 0.95:
        return "высокая точность"
    elif R2 >= 0.75:
        return "удовлетворительная аппроксимация"
    elif R2 >= 0.50:
        return "слабая аппроксимация"
    else:
        return "точность недостаточна, модель требует изменения"



#  Графики


def try_import_matplotlib():
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        return plt
    except Exception:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            return plt
        except Exception:
            return None


def plot_approximations(xs, ys, results, title="Аппроксимирующие функции"):
    plt = try_import_matplotlib()
    if plt is None:
        print("[Matplotlib недоступен, пропуск графика]")
        return

    x_dense = [xs[0] + (xs[-1] - xs[0]) * i / 500 for i in range(501)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xs, ys, color='black', zorder=5, s=60, label='Исходные данные')

    for name, phi_func, color, linestyle in results:
        y_dense = []
        for x in x_dense:
            try:
                y_dense.append(phi_func(x))
            except Exception:
                y_dense.append(float('nan'))
        ax.plot(x_dense, y_dense, color=color, linestyle=linestyle, label=name, linewidth=1.8)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    fname = title.replace(' ', '_').replace('/', '_') + '.png'
    plt.savefig(fname, dpi=120)
    print(f"  [График сохранён: {fname}]")
    try:
        plt.show()
    except Exception:
        pass
    plt.close()



#  Вывод таблицы


def print_table(xs, ys, phi_vals, eps):
    print(f"\n{'i':>4} {'x_i':>8} {'y_i':>12} {'phi(x_i)':>12} {'eps_i':>12}")
    print("-" * 52)
    for i in range(len(xs)):
        print(f"{i:>4} {xs[i]:>8.4f} {ys[i]:>12.6f} {phi_vals[i]:>12.6f} {eps[i]:>12.6f}")


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)



#  Режимы


def mode_input_data():
    """Ввод и просмотр таблицы данных."""
    print_header("ТАБЛИЦА ИСХОДНЫХ ДАННЫХ")
    xs, ys = get_data()
    print(f"\n{'i':>4} {'x_i':>10} {'y_i':>14}")
    print("-" * 32)
    for i, (x, y) in enumerate(zip(xs, ys)):
        print(f"{i:>4} {x:>10.6f} {y:>14.6f}")
    print(f"\nКоличество точек: {len(xs)}")
    return xs, ys


def mode_linear(xs, ys):
    """Линейная аппроксимация."""
    print_header("ЛИНЕЙНАЯ АППРОКСИМАЦИЯ  phi(x) = a*x + b")

    coeffs = lsq_polynomial(xs, ys, 1)
    b_c, a_c = coeffs[0], coeffs[1]
    phi_vals = [poly_eval(coeffs, x) for x in xs]
    S, delta, R2, eps = compute_metrics(xs, ys, phi_vals)
    r = pearson_r(xs, ys)

    print(f"\nКоэффициенты: a = {a_c:.6f},  b = {b_c:.6f}")
    print(f"Формула:  phi(x) = {a_c:.4f}*x + ({b_c:.4f})")
    print(f"\nКоэффициент корреляции Пирсона: r = {r:.6f}")
    if abs(r) < 0.3:
        corr = "слабая"
    elif abs(r) < 0.5:
        corr = "умеренная"
    elif abs(r) < 0.7:
        corr = "заметная"
    elif abs(r) < 0.9:
        corr = "высокая"
    else:
        corr = "весьма высокая"
    print(f"  => Линейная связь: {corr}")
    print(f"\nМера отклонения:         S     = {S:.6f}")
    print(f"Среднекв. отклонение:    delta = {delta:.6f}")
    print(f"Коэф. детерминации:      R^2   = {R2:.6f}  ({r2_description(R2)})")

    print_table(xs, ys, phi_vals, eps)

    results = [("Линейная", lambda x, c=coeffs: poly_eval(c, x), 'blue', '-')]
    plot_approximations(xs, ys, results, "Линейная аппроксимация")
    return S, delta, R2, "Линейная", lambda x, c=coeffs: poly_eval(c, x)


def mode_polynomial(xs, ys, degree):
    """Полиномиальная аппроксимация степени degree."""
    print_header(f"ПОЛИНОМИАЛЬНАЯ АППРОКСИМАЦИЯ (степень {degree})")

    coeffs = lsq_polynomial(xs, ys, degree)
    phi_vals = [poly_eval(coeffs, x) for x in xs]
    S, delta, R2, eps = compute_metrics(xs, ys, phi_vals)

    terms = []
    for i, c in enumerate(coeffs):
        if i == 0:
            terms.append(f"{c:.4f}")
        elif i == 1:
            terms.append(f"({c:.4f})*x")
        else:
            terms.append(f"({c:.4f})*x^{i}")
    formula = " + ".join(terms)
    print(f"\nКоэффициенты: " + ", ".join(f"a{i}={c:.6f}" for i, c in enumerate(coeffs)))
    print(f"Формула:  phi(x) = {formula}")
    print(f"\nМера отклонения:         S     = {S:.6f}")
    print(f"Среднекв. отклонение:    delta = {delta:.6f}")
    print(f"Коэф. детерминации:      R^2   = {R2:.6f}  ({r2_description(R2)})")

    print_table(xs, ys, phi_vals, eps)

    lbl = f"Полином {degree}-й степени"
    results = [(lbl, lambda x, c=coeffs: poly_eval(c, x), 'green', '-')]
    plot_approximations(xs, ys, results, f"Полиномиальная аппроксимация (степень {degree})")
    return S, delta, R2, lbl, lambda x, c=coeffs: poly_eval(c, x)


def mode_exponential(xs, ys):
    """Экспоненциальная аппроксимация."""
    print_header("ЭКСПОНЕНЦИАЛЬНАЯ АППРОКСИМАЦИЯ  phi(x) = a * e^(b*x)")
    try:
        a, b = lsq_exponential(xs, ys)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None

    phi_vals = [a * math.exp(b * x) for x in xs]
    S, delta, R2, eps = compute_metrics(xs, ys, phi_vals)

    print(f"\nКоэффициенты: a = {a:.6f},  b = {b:.6f}")
    print(f"Формула:  phi(x) = {a:.4f} * e^({b:.4f}*x)")
    print(f"\nМера отклонения:         S     = {S:.6f}")
    print(f"Среднекв. отклонение:    delta = {delta:.6f}")
    print(f"Коэф. детерминации:      R^2   = {R2:.6f}  ({r2_description(R2)})")

    print_table(xs, ys, phi_vals, eps)

    results = [("Экспоненциальная", lambda x, a=a, b=b: a * math.exp(b * x), 'red', '--')]
    plot_approximations(xs, ys, results, "Экспоненциальная аппроксимация")
    return S, delta, R2, "Экспоненциальная", lambda x, a=a, b=b: a * math.exp(b * x)


def mode_logarithmic(xs, ys):
    """Логарифмическая аппроксимация."""
    print_header("ЛОГАРИФМИЧЕСКАЯ АППРОКСИМАЦИЯ  phi(x) = a*ln(x) + b")
    try:
        a, b = lsq_logarithmic(xs, ys)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None

    phi_vals = [a * math.log(x) + b if x > 0 else float('nan') for x in xs]
    valid = [(i, xs[i], ys[i], phi_vals[i]) for i in range(len(xs)) if not math.isnan(phi_vals[i])]
    xs_v = [p[1] for p in valid]
    ys_v = [p[2] for p in valid]
    phi_v = [p[3] for p in valid]
    S, delta, R2, eps = compute_metrics(xs_v, ys_v, phi_v)

    print(f"\nКоэффициенты: a = {a:.6f},  b = {b:.6f}")
    print(f"Формула:  phi(x) = {a:.4f}*ln(x) + ({b:.4f})")
    print(f"\nМера отклонения:         S     = {S:.6f}")
    print(f"Среднекв. отклонение:    delta = {delta:.6f}")
    print(f"Коэф. детерминации:      R^2   = {R2:.6f}  ({r2_description(R2)})")

    eps_full = [phi_vals[i] - ys[i] if not math.isnan(phi_vals[i]) else float('nan') for i in range(len(xs))]
    print_table(xs, ys, phi_vals, eps_full)

    results = [("Логарифмическая", lambda x, a=a, b=b: a * math.log(x) + b if x > 0 else float('nan'), 'purple', '-.')]
    plot_approximations(xs, ys, results, "Логарифмическая аппроксимация")
    return S, delta, R2, "Логарифмическая", lambda x, a=a, b=b: a * math.log(x) + b if x > 0 else float('nan')


def mode_power(xs, ys):
    """Степенная аппроксимация."""
    print_header("СТЕПЕННАЯ АППРОКСИМАЦИЯ  phi(x) = a * x^b")
    try:
        a, b = lsq_power(xs, ys)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None

    phi_vals = [a * x ** b if x > 0 else float('nan') for x in xs]
    valid = [(xs[i], ys[i], phi_vals[i]) for i in range(len(xs)) if not math.isnan(phi_vals[i])]
    xs_v = [p[0] for p in valid]
    ys_v = [p[1] for p in valid]
    phi_v = [p[2] for p in valid]
    S, delta, R2, eps = compute_metrics(xs_v, ys_v, phi_v)

    print(f"\nКоэффициенты: a = {a:.6f},  b = {b:.6f}")
    print(f"Формула:  phi(x) = {a:.4f} * x^({b:.4f})")
    print(f"\nМера отклонения:         S     = {S:.6f}")
    print(f"Среднекв. отклонение:    delta = {delta:.6f}")
    print(f"Коэф. детерминации:      R^2   = {R2:.6f}  ({r2_description(R2)})")

    eps_full = [phi_vals[i] - ys[i] if not math.isnan(phi_vals[i]) else float('nan') for i in range(len(xs))]
    print_table(xs, ys, phi_vals, eps_full)

    results = [("Степенная", lambda x, a=a, b=b: a * x ** b if x > 0 else float('nan'), 'orange', ':')]
    plot_approximations(xs, ys, results, "Степенная аппроксимация")
    return S, delta, R2, "Степенная", lambda x, a=a, b=b: a * x ** b if x > 0 else float('nan')


def mode_compare_all(xs, ys):
    """Сравнение всех методов и выбор наилучшего."""
    print_header("СРАВНЕНИЕ ВСЕХ АППРОКСИМИРУЮЩИХ ФУНКЦИЙ")

    all_results = []

    def try_add(res):
        if res is not None:
            all_results.append(res)

    # Собираем без вывода графиков отдельно — запускаем напрямую
    try:
        c = lsq_polynomial(xs, ys, 1)
        pv = [poly_eval(c, x) for x in xs]
        S, d, R2, eps = compute_metrics(xs, ys, pv)
        all_results.append((S, d, R2, "Линейная", lambda x, c=c: poly_eval(c, x)))
    except Exception as e:
        print(f"Линейная: ошибка — {e}")

    for deg in [2, 3]:
        try:
            c = lsq_polynomial(xs, ys, deg)
            pv = [poly_eval(c, x) for x in xs]
            S, d, R2, eps = compute_metrics(xs, ys, pv)
            all_results.append((S, d, R2, f"Полином {deg}-й ст.", lambda x, c=c: poly_eval(c, x)))
        except Exception as e:
            print(f"Полином {deg}: ошибка — {e}")

    try:
        a, b = lsq_exponential(xs, ys)
        pv = [a * math.exp(b * x) for x in xs]
        S, d, R2, eps = compute_metrics(xs, ys, pv)
        all_results.append((S, d, R2, "Экспоненциальная", lambda x, a=a, b=b: a * math.exp(b * x)))
    except Exception as e:
        print(f"Экспоненциальная: ошибка — {e}")

    try:
        a, b = lsq_logarithmic(xs, ys)
        valid = [(xs[i], ys[i]) for i in range(len(xs)) if xs[i] > 0]
        xs_v = [p[0] for p in valid]; ys_v = [p[1] for p in valid]
        pv = [a * math.log(x) + b for x in xs_v]
        S, d, R2, eps = compute_metrics(xs_v, ys_v, pv)
        all_results.append((S, d, R2, "Логарифмическая", lambda x, a=a, b=b: a * math.log(x) + b if x > 0 else float('nan')))
    except Exception as e:
        print(f"Логарифмическая: ошибка — {e}")

    try:
        a, b = lsq_power(xs, ys)
        valid = [(xs[i], ys[i]) for i in range(len(xs)) if xs[i] > 0]
        xs_v = [p[0] for p in valid]; ys_v = [p[1] for p in valid]
        pv = [a * x ** b for x in xs_v]
        S, d, R2, eps = compute_metrics(xs_v, ys_v, pv)
        all_results.append((S, d, R2, "Степенная", lambda x, a=a, b=b: a * x ** b if x > 0 else float('nan')))
    except Exception as e:
        print(f"Степенная: ошибка — {e}")

    if not all_results:
        print("Нет успешных аппроксимаций.")
        return

    print(f"\n{'Функция':<22} {'S':>12} {'delta':>12} {'R^2':>10} {'Качество'}")
    print("-" * 75)
    for S, d, R2, name, _ in all_results:
        print(f"{name:<22} {S:>12.6f} {d:>12.6f} {R2:>10.6f}  {r2_description(R2)}")

    best = min(all_results, key=lambda t: t[1])
    print(f"\n>>> НАИЛУЧШАЯ АППРОКСИМАЦИЯ: {best[3]}  (delta = {best[1]:.6f})")

    # Общий график
    colors = ['blue', 'green', 'darkgreen', 'red', 'purple', 'orange']
    styles = ['-', '-', '--', '--', '-.', ':']
    plot_data = []
    for idx, (S, d, R2, name, fn) in enumerate(all_results):
        plot_data.append((name, fn, colors[idx % len(colors)], styles[idx % len(styles)]))
    plot_approximations(xs, ys, plot_data, "Сравнение всех аппроксимаций")



#  Ввод данных


_xs_cache = None
_ys_cache = None


def get_data():
    global _xs_cache, _ys_cache
    if _xs_cache is not None:
        return _xs_cache, _ys_cache
    return load_default_data()


def load_default_data():
    """Вариант 2: y = 15x/(x^4+2), x in [0,4], h=0.4"""
    xs = [round(0.4 * i, 10) for i in range(11)]
    ys = [15 * x / (x ** 4 + 2) for x in xs]
    return xs, ys


def input_manual():
    """Ручной ввод точек."""
    print("\nВведите количество точек (от 8 до 12):")
    while True:
        try:
            n = int(input("> ").strip())
            if 8 <= n <= 12:
                break
            print("Нужно от 8 до 12 точек.")
        except ValueError:
            print("Введите целое число.")

    xs, ys = [], []
    print("Введите пары x_i y_i (через пробел):")
    for i in range(n):
        while True:
            try:
                parts = input(f"  точка {i}: ").strip().split()
                x, y = float(parts[0]), float(parts[1])
                xs.append(x)
                ys.append(y)
                break
            except (ValueError, IndexError):
                print("  Неверный ввод, повторите.")
    return xs, ys


def input_from_file():
    """Ввод из файла."""
    fname = input("Имя файла: ").strip()
    try:
        xs, ys = [], []
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    xs.append(float(parts[0]))
                    ys.append(float(parts[1]))
        if len(xs) < 2:
            print("В файле недостаточно данных.")
            return None, None
        print(f"Загружено {len(xs)} точек.")
        return xs, ys
    except FileNotFoundError:
        print(f"Файл '{fname}' не найден.")
        return None, None
    except ValueError as e:
        print(f"Ошибка разбора файла: {e}")
        return None, None



#  Главное меню


def main():
    global _xs_cache, _ys_cache

    _xs_cache, _ys_cache = load_default_data()

    while True:
        print("\n" + "=" * 60)
        print("  ЛАБ. РАБОТА №4 — Аппроксимация МНК")
        print(f"  Текущий набор данных: {len(_xs_cache)} точек")
        print("=" * 60)
        print("  1. Просмотр исходных данных")
        print("  2. Линейная аппроксимация")
        print("  3. Квадратичная аппроксимация (полином 2-й ст.)")
        print("  4. Полином 3-й степени")
        print("  5. Экспоненциальная аппроксимация")
        print("  6. Логарифмическая аппроксимация")
        print("  7. Степенная аппроксимация")
        print("  8. Сравнение всех методов")
        print("  ─────────────────────────────────────────────")
        print("  9. Загрузить данные: вариант 2 (по умолчанию)")
        print(" 10. Ввести данные вручную")
        print(" 11. Загрузить данные из файла")
        print("  0. Выход")
        print()

        choice = input("Выберите действие: ").strip()

        xs, ys = _xs_cache, _ys_cache

        if choice == '0':
            print("Выход.")
            sys.exit(0)
        elif choice == '1':
            mode_input_data()
        elif choice == '2':
            mode_linear(xs, ys)
        elif choice == '3':
            mode_polynomial(xs, ys, 2)
        elif choice == '4':
            mode_polynomial(xs, ys, 3)
        elif choice == '5':
            mode_exponential(xs, ys)
        elif choice == '6':
            mode_logarithmic(xs, ys)
        elif choice == '7':
            mode_power(xs, ys)
        elif choice == '8':
            mode_compare_all(xs, ys)
        elif choice == '9':
            _xs_cache, _ys_cache = load_default_data()
            print("Загружены данные варианта 2.")
        elif choice == '10':
            result = input_manual()
            if result[0] is not None:
                _xs_cache, _ys_cache = result
        elif choice == '11':
            result = input_from_file()
            if result[0] is not None:
                _xs_cache, _ys_cache = result
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == '__main__':
    main()