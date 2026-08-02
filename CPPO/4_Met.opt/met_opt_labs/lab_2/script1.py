import math


def f(x):
    return x ** 2 - 2 * x + math.exp(-x)


x1 = 1.0
delta_x = 0.25
eps1 = 0.0001
eps2 = 0.0001
iteration = 1

print(f"Начальная точка x1 = {x1}, шаг = {delta_x}\n")

x2 = x1 + delta_x
f1, f2 = f(x1), f(x2)
x3 = x1 + 2 * delta_x if f1 > f2 else x1 - delta_x
f3 = f(x3)

while True:

    pts = sorted([(x1, f1), (x2, f2), (x3, f3)])
    x1, f1 = pts[0]
    x2, f2 = pts[1]
    x3, f3 = pts[2]

    f_min = min(f1, f2, f3)
    x_min = x1 if f_min == f1 else (x2 if f_min == f2 else x3)

    num = (x2 ** 2 - x3 ** 2) * f1 + (x3 ** 2 - x1 ** 2) * f2 + (x1 ** 2 - x2 ** 2) * f3
    den = (x2 - x3) * f1 + (x3 - x1) * f2 + (x1 - x2) * f3

    if den == 0:
        x1 = x_min
        x2 = x1 + delta_x
        f1, f2 = f(x1), f(x2)
        x3 = x1 + 2 * delta_x if f1 > f2 else x1 - delta_x
        f3 = f(x3)
        continue

    x_bar = 0.5 * (num / den)
    f_bar = f(x_bar)

    print(f"Итерация {iteration}: x_bar = {x_bar:.10f}, f(x_bar) = {f_bar:.10f}")

    cond1 = abs((f_min - f_bar) / f_bar) < eps1
    cond2 = abs((x_min - x_bar) / x_bar) < eps2

    if cond1 and cond2:
        print(f"\nУсловия окончания выполнены!")
        print(f"Ответ: x* = {x_bar:.10f}, f(x*) = {f_bar:.10f}")
        break

    if x1 <= x_bar <= x3:

        pts = sorted([(x1, f1), (x2, f2), (x3, f3), (x_bar, f_bar)])

        best_idx = pts.index(min(pts, key=lambda item: item[1]))

        if best_idx == 0:
            pts = pts[0:3]
        elif best_idx == 3:
            pts = pts[1:4]
        else:
            pts = pts[best_idx - 1:best_idx + 2]

        x1, f1 = pts[0]
        x2, f2 = pts[1]
        x3, f3 = pts[2]


    else:

        x1 = x_bar
        x2 = x1 + delta_x
        f1, f2 = f(x1), f(x2)
        x3 = x1 + 2 * delta_x if f1 > f2 else x1 - delta_x
        f3 = f(x3)

    iteration += 1
