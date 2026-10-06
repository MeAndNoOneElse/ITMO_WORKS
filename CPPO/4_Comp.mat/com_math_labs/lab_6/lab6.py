import math
import os

try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False

EQUATIONS = {
    1: {
        "name": "y' = y - x²  + 1",
        "f": lambda x, y: y - x ** 2 + 1,
        "exact": lambda x, C: (x + 1) ** 2 + C * math.exp(x),
        # C вычисляется из начального условия
        "exact_C": lambda x0, y0: (y0 - (x0 + 1) ** 2) * math.exp(-x0),
        "exact_str": "y = (x+1)² + C·eˣ",
    },
    2: {
        "name": "y' = x + y",
        "f": lambda x, y: x + y,
        "exact": lambda x, C: -x - 1 + C * math.exp(x),
        "exact_C": lambda x0, y0: (y0 + x0 + 1) * math.exp(-x0),
        "exact_str": "y = -x - 1 + C·eˣ",
    },
    3: {
        "name": "y' = 2y / x",
        "f": lambda x, y: 2 * y / x if x != 0 else 0,
        "exact": lambda x, C: C * x ** 2,
        "exact_C": lambda x0, y0: y0 / x0 ** 2 if x0 != 0 else 0,
        "exact_str": "y = C·x²",
    },
}


#  ЧИСЛЕННЫЕ МЕТОДЫ 

def euler_improved(f, x0, y0, xn, h):
    # Усовершенствованный метод Эйлера #
    xs, ys = [x0], [y0]
    x, y = x0, y0
    steps = round((xn - x0) / h)
    for _ in range(steps):
        k1 = h * f(x, y)
        k2 = h * f(x + h, y + k1)
        y = y + 0.5 * (k1 + k2)
        x = round(x + h, 10)
        xs.append(x)
        ys.append(y)
    return xs, ys


def runge_kutta4(f, x0, y0, xn, h):
    # Метод Рунге-Кутта 4-го порядка
    xs, ys = [x0], [y0]
    x, y = x0, y0
    steps = round((xn - x0) / h)
    for _ in range(steps):
        k1 = h * f(x, y)
        k2 = h * f(x + h / 2, y + k1 / 2)
        k3 = h * f(x + h / 2, y + k2 / 2)
        k4 = h * f(x + h, y + k3)
        y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x = round(x + h, 10)
        xs.append(x)
        ys.append(y)
    return xs, ys


def milne(f, x0, y0, xn, h):
    # Метод Милна (прогноз-коррекция, 4-й порядок).
    # Первые 4 точки (индексы 0..3) берутся методом РК-4.
    # Начиная с i=4 вычисляем y[i]:
    #  Прогноз:    y[i] = y[i-4] + 4h/3*(2f[i-3] - f[i-2] + 2f[i-1])
    # Коррекция:  y[i] = y[i-2] + h/3*(f[i-2] + 4f[i-1] + f_pred)
    steps = round((xn - x0) / h)
    if steps < 4:
        raise ValueError("Для метода Милна нужно не менее 4 шагов")

    # Разгон — первые 4 точки (индексы 0,1,2,3) через РК4
    xs_init, ys_init = runge_kutta4(f, x0, y0, round(x0 + 3 * h, 10), h)
    xs = list(xs_init)  # длина = 4
    ys = list(ys_init)
    fs = [f(xs[i], ys[i]) for i in range(4)]

    # Основной цикл: вычисляем y[4], y[5], ..., y[steps]
    for i in range(4, steps + 1):
        # индексы i-4, i-3, i-2, i-1 уже известны
        y_pred = ys[i - 4] + (4 * h / 3) * (2 * fs[i - 3] - fs[i - 2] + 2 * fs[i - 1])
        x_new = round(x0 + i * h, 10)
        f_pred = f(x_new, y_pred)

        # Коррекция с итерациями
        y_corr = ys[i - 2] + (h / 3) * (fs[i - 2] + 4 * fs[i - 1] + f_pred)
        for _ in range(50):
            f_corr = f(x_new, y_corr)
            y_new = ys[i - 2] + (h / 3) * (fs[i - 2] + 4 * fs[i - 1] + f_corr)
            if abs(y_new - y_corr) < 1e-12:
                y_corr = y_new
                break
            y_corr = y_new

        xs.append(x_new)
        ys.append(y_corr)
        fs.append(f(x_new, y_corr))

    return xs, ys


#  ОЦЕНКА ПОГРЕШНОСТИ
def runge_error(method, f, x0, y0, xn, h, p):
    # Правило Рунге на конце интервала.#
    _, ys_h = method(f, x0, y0, xn, h)
    _, ys_h2 = method(f, x0, y0, xn, h / 2)
    # сравниваем в конечной точке
    R = abs(ys_h[-1] - ys_h2[-1]) / (2 ** p - 1)
    return R


def exact_error(f_exact, xs, ys, C):
    # ε = max|y_exact - y_numerical|#
    errs = [abs(f_exact(x, C) - y) for x, y in zip(xs, ys)]
    return max(errs)


#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ВЫВОДА

def print_table(xs, ys, f_exact=None, C=None, title=""):
    W = 76
    print(f"\n{'' * W}")
    print(f"  {title}")
    print(f"{'' * W}")
    if f_exact:
        print(f"  {'i':>4}  {'x':>10}  {'y_числ':>14}  {'y_точн':>14}  {'|δ|':>12}")
        print(f"  {'' * 4}  {'' * 10}  {'' * 14}  {'' * 14}  {'' * 12}")
        for i, (x, y) in enumerate(zip(xs, ys)):
            yt = f_exact(x, C)
            print(f"  {i:>4}  {x:>10.4f}  {y:>14.8f}  {yt:>14.8f}  {abs(yt - y):>12.2e}")
    else:
        print(f"  {'i':>4}  {'x':>10}  {'y':>14}")
        print(f"  {'' * 4}  {'' * 10}  {'' * 14}")
        for i, (x, y) in enumerate(zip(xs, ys)):
            print(f"  {i:>4}  {x:>10.4f}  {y:>14.8f}")
    print(f"{'' * W}")


def save_plot(eq, xs_methods, ys_methods, labels, colors,
              f_exact, C, filename, title):
    # Строит и сохраняет график.#
    if not MATPLOTLIB:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=13)

    ax1, ax2 = axes

    # Левый: все кривые + точное
    xd = [xs_methods[0][0] + i * (xs_methods[0][-1] - xs_methods[0][0]) / 300
          for i in range(301)]
    yd = [f_exact(x, C) for x in xd]
    ax1.plot(xd, yd, 'k-', linewidth=2.5, label='Точное решение', zorder=5)
    for xs, ys, lbl, clr in zip(xs_methods, ys_methods, labels, colors):
        ax1.plot(xs, ys, marker='o', markersize=3, linestyle='--',
                 color=clr, label=lbl, linewidth=1.4)
    ax1.set_xlabel('x');
    ax1.set_ylabel('y')
    ax1.set_title('Сравнение методов с точным решением')
    ax1.legend(fontsize=9);
    ax1.grid(True, alpha=0.4)

    # Правый: погрешности
    for xs, ys, lbl, clr in zip(xs_methods, ys_methods, labels, colors):
        errs = [abs(f_exact(x, C) - y) for x, y in zip(xs, ys)]
        ax2.semilogy(xs, errs, marker='s', markersize=3,
                     linestyle='-', color=clr, label=lbl, linewidth=1.4)
    ax2.set_xlabel('x');
    ax2.set_ylabel('|ошибка|')
    ax2.set_title('Погрешность (лог. масштаб)')
    ax2.legend(fontsize=9);
    ax2.grid(True, alpha=0.4)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    return filename


#  ВВОД / ВАЛИДАЦИЯ


def input_float(prompt, lo=None, hi=None, nonzero=False):
    while True:
        try:
            v = float(input(prompt))
            if nonzero and v == 0:
                print("  ✗ Значение не должно быть нулём");
                continue
            if lo is not None and v < lo:
                print(f"  ✗ Значение должно быть ≥ {lo}");
                continue
            if hi is not None and v > hi:
                print(f"  ✗ Значение должно быть ≤ {hi}");
                continue
            return v
        except ValueError:
            print("  ✗ Введите число")


def input_int(prompt, choices):
    while True:
        try:
            v = int(input(prompt))
            if v in choices:
                return v
            print(f"  ✗ Выберите из {choices}")
        except ValueError:
            print("  ✗ Введите целое число")


BANNER = "лаба №6 "

MENU = '''
1. Решить задачу Коши       
2. Демонстрационный пример  
3. Тест всех методов (авто) 
4. Справка по методам       
0. Выход                    
'''

HELP_TEXT = ''


def run_solve():
    # Интерактивное решение.#
    print("\n Выбор уравнения ")
    for k, eq in EQUATIONS.items():
        print(f"  {k}. {eq['name']}   (точн. {eq['exact_str']})")
    eq_id = input_int("  Номер уравнения [1-3]: ", list(EQUATIONS.keys()))
    eq = EQUATIONS[eq_id]

    print("\n Начальные условия ")
    x0 = input_float("  x₀ = ", )
    if eq_id == 3:
        x0 = input_float("  x₀ ≠ 0 (деление на x): ", nonzero=True)
    y0 = input_float("  y(x₀) = ")
    xn = input_float("  xₙ (правая граница, > x₀): ", lo=x0 + 1e-9)
    h = input_float("  h (шаг, > 0): ", lo=1e-9)
    eps = input_float("  ε (точность для Рунге): ", lo=1e-15)

    f = eq['f']
    C = eq['exact_C'](x0, y0)
    f_exact = eq['exact']

    print("\n  Вычисление...", flush=True)

    xs_e, ys_e = euler_improved(f, x0, y0, xn, h)
    xs_r, ys_r = runge_kutta4(f, x0, y0, xn, h)
    try:
        xs_m, ys_m = milne(f, x0, y0, xn, h)
        milne_ok = True
    except ValueError as e:
        print(f"\n    Метод Милна: {e}")
        milne_ok = False

    # Таблицы
    print_table(xs_e, ys_e, f_exact, C, "Усовершенствованный метод Эйлера")
    print_table(xs_r, ys_r, f_exact, C, "Метод Рунге-Кутта 4-го порядка")
    if milne_ok:
        print_table(xs_m, ys_m, f_exact, C, "Метод Милна")

    # Погрешности
    R_e = runge_error(euler_improved, f, x0, y0, xn, h, p=2)
    R_r = runge_error(runge_kutta4, f, x0, y0, xn, h, p=4)
    e_e = exact_error(f_exact, xs_e, ys_e, C)
    e_r = exact_error(f_exact, xs_r, ys_r, C)

    print(f"\n{'' * 60}")
    print("  ОЦЕНКА ПОГРЕШНОСТИ")
    print(f"{'' * 60}")
    print(f"  Эйлер улучш.  | Рунге R = {R_e:.2e}  | max|δ| = {e_e:.2e}")
    print(f"  Рунге-Кутта 4 | Рунге R = {R_r:.2e}  | max|δ| = {e_r:.2e}")
    if milne_ok:
        e_m = exact_error(f_exact, xs_m, ys_m, C)
        print(f"  Милна         | ε = max|δ| = {e_m:.2e}")
    print(f"{'' * 60}")

    # График
    if MATPLOTLIB:
        fname = "lab6_plot.png"
        xs_list = [xs_e, xs_r]
        ys_list = [ys_e, ys_r]
        lbls = ["Эйлер улучш.", "Рунге-Кутта 4"]
        clrs = ["#E74C3C", "#3498DB"]
        if milne_ok:
            xs_list.append(xs_m);
            ys_list.append(ys_m)
            lbls.append("Милна");
            clrs.append("#2ECC71")
        save_plot(eq, xs_list, ys_list, lbls, clrs,
                  f_exact, C, fname,
                  f"ЛР6 · {eq['name']}  |  x₀={x0}, y₀={y0}, h={h}")
        print(f"\n   График сохранён: {os.path.abspath(fname)}")
    else:
        print("    matplotlib не найден, график не строится")


def run_demo():
    # Демонстрационный пример с фиксированными данными.#
    print("\n Демонстрационный пример ")
    print("  Уравнение: y' = y - x² + 1,  y(0)=0.5,  [0, 2],  h=0.2")
    eq = EQUATIONS[1]
    f = eq['f']
    x0, y0, xn, h = 0.0, 0.5, 2.0, 0.2
    C = eq['exact_C'](x0, y0)
    f_exact = eq['exact']

    xs_e, ys_e = euler_improved(f, x0, y0, xn, h)
    xs_r, ys_r = runge_kutta4(f, x0, y0, xn, h)
    xs_m, ys_m = milne(f, x0, y0, xn, h)

    print_table(xs_e, ys_e, f_exact, C, "Усовершенствованный метод Эйлера")
    print_table(xs_r, ys_r, f_exact, C, "Метод Рунге-Кутта 4-го порядка")
    print_table(xs_m, ys_m, f_exact, C, "Метод Милна")

    R_e = runge_error(euler_improved, f, x0, y0, xn, h, p=2)
    R_r = runge_error(runge_kutta4, f, x0, y0, xn, h, p=4)
    e_e = exact_error(f_exact, xs_e, ys_e, C)
    e_r = exact_error(f_exact, xs_r, ys_r, C)
    e_m = exact_error(f_exact, xs_m, ys_m, C)

    print(f"\n{'' * 60}")
    print("  ОЦЕНКА ПОГРЕШНОСТИ")
    print(f"{'' * 60}")
    print(f"  Эйлер улучш.  | Рунге R = {R_e:.2e}  | max|δ| = {e_e:.2e}")
    print(f"  Рунге-Кутта 4 | Рунге R = {R_r:.2e}  | max|δ| = {e_r:.2e}")
    print(f"  Милна         | ε = max|δ| = {e_m:.2e}")
    print(f"{'' * 60}")

    if MATPLOTLIB:
        fname = "lab6_demo.png"
        save_plot(eq, [xs_e, xs_r, xs_m], [ys_e, ys_r, ys_m],
                  ["Эйлер улучш.", "Рунге-Кутта 4", "Милна"],
                  ["#E74C3C", "#3498DB", "#2ECC71"],
                  f_exact, C, fname,
                  "Демо · y'=y-x²+1, y(0)=0.5, h=0.2")
        print(f"\n   График сохранён: {os.path.abspath(fname)}")


def run_auto_test():
    # Автотест: три уравнения × три шага × проверка правила Рунге.#
    print("\n Автоматическое тестирование ")
    test_cases = [
        (1, 0.0, 0.5, 2.0),
        (2, 0.0, 1.0, 1.0),
        (3, 1.0, 1.0, 3.0),
    ]
    hs = [0.2, 0.1, 0.05]

    for eq_id, x0, y0, xn in test_cases:
        eq = EQUATIONS[eq_id]
        f = eq['f']
        C = eq['exact_C'](x0, y0)
        print(f"\n {eq['name']}  x₀={x0}, y₀={y0}, xₙ={xn}")
        print(f"    {'h':>6} │ {'Эйлер R':>12} │ {'РК4 R':>12} │ {'Милна ε':>12}")
        for h in hs:
            R_e = runge_error(euler_improved, f, x0, y0, xn, h, p=2)
            R_r = runge_error(runge_kutta4, f, x0, y0, xn, h, p=4)
            try:
                xs_m, ys_m = milne(f, x0, y0, xn, h)
                e_m = exact_error(eq['exact'], xs_m, ys_m, C)
                milne_str = f"{e_m:.2e}"
            except ValueError:
                milne_str = "мало шагов"
            print(f"    {h:>6.3f} │ {R_e:>12.2e} │ {R_r:>12.2e} │ {milne_str:>12}")
        print(f"  {'' * 54}")

    # Некорректные данные
    print("\n   Тест некорректных данных ")
    try:
        euler_improved(EQUATIONS[1]['f'], 0, 0.5, 0.1, 0.2)
        print("  h > (xn-x0): результат получен (0 шагов — норма)")
    except Exception as e:
        print(f"  Исключение: {e}")

    try:
        milne(EQUATIONS[1]['f'], 0, 0.5, 0.5, 0.2)
    except ValueError as e:
        print(f"  Метод Милна (мало шагов):  поймано исключение '{e}'")


def show_help():
    print(HELP_TEXT)


# 
#  ТОЧКА ВХОДА
# 

def main():
    print(BANNER)
    while True:
        try:
            print(MENU)
            choice = input("  Выбор: ").strip()
            if choice == '1':
                run_solve()
            elif choice == '2':
                run_demo()
            elif choice == '3':
                run_auto_test()
            elif choice == '4':
                show_help()
            elif choice == '0':
                print("\n  До свидания!\n")
                break
            else:
                print("  ✗ Неверный выбор")
        except EOFError:
            break


if __name__ == "__main__":
    main()
