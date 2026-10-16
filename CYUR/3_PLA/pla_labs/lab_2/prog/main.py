#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №2 — 2D-преобразования
Практическая линейная алгебра
Студенты: Ануфриев А.С. (465029), Бахуров Н.А. (504862), Раджапов Ф.С. (502544)
Преподаватель: Зарина О.А.
Параметры: a=3, b=4, c=2, d=5

Запуск: python main.py (из любой папки).
Графики сохраняются в ../graphics относительно этого файла.
Перед построением все матрицы проверяются численно (assert).
"""

from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- параметры
a, b, c, d = 3, 4, 2, 5

GRAPHICS = Path(__file__).resolve().parent.parent / "graphics"
GRAPHICS.mkdir(parents=True, exist_ok=True)

# Многоугольник (5 вершин, порядок обхода сохраняется)
polygon = np.array([
    [0.5, 1.0],
    [-1.5, 0.5],
    [-1.0, -1.5],
    [1.5, -0.8],
    [2.0, 1.0],
])

# ------------------------------------------------- общие классы матриц
def rot(deg):
    """Поворот на deg градусов против часовой стрелки."""
    t = np.radians(deg)
    return np.array([[np.cos(t), -np.sin(t)],
                     [np.sin(t), np.cos(t)]])


def reflection(k):
    """Отражение относительно прямой y = kx."""
    return np.array([[1 - k**2, 2 * k],
                     [2 * k, k**2 - 1]]) / (1 + k**2)


def projection(k):
    """Ортогональная проекция на прямую y = kx."""
    return np.array([[1, k],
                     [k, k**2]]) / (1 + k**2)


I2 = np.eye(2)

# ------------------------------------------------------- матрицы пунктов
M1 = reflection(a)                         # п.1: отражение y = 3x
M2 = projection(b)                         # п.2: проекция на y = 4x
M3 = rot(10 * c)                           # п.3: поворот на 20°
M4 = -I2                                   # п.4: центральная симметрия
M5 = rot(-10 * d) @ M1                     # п.5: сначала M1, потом поворот на 50° по часовой

# Направляющие векторы прямых y = ax и y = bx образуют столбцы P
P = np.array([[1.0, 1.0],
              [a, b]])
M6 = P @ np.diag([1.0, 2.0])               # п.6: e1 -> (1,a), e2 -> 2*(1,b)
M7 = np.linalg.inv(P)                      # п.7: (1,a) -> e1, (1,b) -> e2
M8 = P @ np.array([[0.0, 1.0], [1.0, 0.0]]) @ np.linalg.inv(P)  # п.8: меняет прямые местами

M9 = np.array([[1.0, -1.0],
               [1.0, 1.0]])                # п.9: sqrt(c)*R(45°), det = c = 2, круг -> круг
M10 = rot(30) @ np.diag([1.0, d]) @ rot(30).T  # п.10: симметричная, собств. числа 1 и d
M11 = np.array([[3.0, 1.0], [1.0, 1.0]])   # п.11
M12 = np.array([[2.0, 1.0], [0.0, 2.0]])   # п.12: жорданова клетка
M13 = rot(90)                              # п.13: поворот на 90°
M14 = 2 * I2                               # п.14: скалярная матрица

A15, B15 = M3, M1                          # п.15: поворот и отражение
A16 = M1                                   # п.16: отражение
B16 = np.array([[-1.0, 3.0], [3.0, 7.0]])  # п.16: B = 3I + 5A (собств. числа 8 и -2)

# ------------------------------------------------------------- проверки
def check(cond, msg):
    assert cond, f"ОШИБКА: {msg}"
    print("OK  ", msg)


def collinear(u, v):
    return abs(u[0] * v[1] - u[1] * v[0]) < 1e-9


def run_checks():
    S = lambda M: np.allclose(M, M.T)
    Orth = lambda M: np.allclose(M.T @ M, I2)
    det = np.linalg.det

    check(S(M1) and np.allclose(M1 @ M1, I2) and np.isclose(det(M1), -1), "п.1: M1 симметрична, M1^2=I, det=-1")
    check(np.allclose(M1 @ [1, a], [1, a]) and np.allclose(M1 @ [a, -1], [-a, 1]), "п.1: (1,a)->+, (a,-1)->- ")
    check(np.allclose(M2 @ M2, M2) and S(M2) and abs(det(M2)) < 1e-12, "п.2: M2 симметрична, идемпотентна, det=0")
    check(np.allclose(M2 @ [1, b], [1, b]) and np.allclose(M2 @ [b, -1], 0), "п.2: образ y=bx, ядро (b,-1)")
    check(Orth(M3) and np.isclose(det(M3), 1), "п.3: M3 ортогональна, det=1")
    check(np.allclose(M4 @ [3, -2], [-3, 2]), "п.4: M4 (x,y)->(-x,-y)")
    check(Orth(M5) and S(M5) and np.allclose(M5 @ M5, I2) and np.isclose(det(M5), -1),
          "п.5: M5 ортогональна, симметрична, M5^2=I, det=-1 (это снова отражение)")
    check(np.allclose(M6, [[1, 2], [3, 8]]) and np.isclose(det(M6), 2), "п.6: M6=[[1,2],[3,8]], det=2")
    check(collinear(M6 @ [1, 0], [1, a]) and collinear(M6 @ [0, 1], [1, b]), "п.6: y=0->y=ax, x=0->y=bx")
    check(np.allclose(M7, [[4, -1], [-3, 1]]), "п.7: M7=[[4,-1],[-3,1]]")
    check(abs((M7 @ [1, a])[1]) < 1e-9 and abs((M7 @ [1, b])[0]) < 1e-9, "п.7: y=ax->y=0, y=bx->x=0")
    check(np.allclose(M8, [[1, 0], [7, -1]]), "п.8: M8=[[1,0],[7,-1]]")
    check(collinear(M8 @ [1, a], [1, b]) and collinear(M8 @ [1, b], [1, a]), "п.8: прямые y=ax и y=bx меняются местами")
    check(np.allclose(M8 @ [2, 7], [2, 7]) and np.allclose(M8 @ [0, 1], [0, -1]), "п.8: собств. векторы (2,7) λ=1, (0,1) λ=-1")
    check(np.allclose(M9.T @ M9, c * I2) and np.isclose(det(M9), c) and not np.allclose(M9, np.diag(np.diag(M9))),
          "п.9: M9^T M9 = cI (круг->круг), det=c, матрица недиагональна")
    ev10 = np.sort(np.linalg.eigvalsh(M10))
    check(np.isclose(det(M10), d) and np.allclose(ev10, [1, d]) and S(M10) and abs(M10[0, 1]) > 1e-9,
          "п.10: det=d, собств. числа {1,d}, недиагональна (эллипс, не круг)")
    w11, V11 = np.linalg.eigh(M11)
    check(abs(V11[:, 0] @ V11[:, 1]) < 1e-12 and all(abs(v[1]) > 1e-9 and abs(v[0] - v[1]) > 1e-9 for v in V11.T),
          "п.11: собств. векторы ортогональны и не лежат на y=0, y=x")
    check(np.allclose(w11, [2 - np.sqrt(2), 2 + np.sqrt(2)]), "п.11: λ = 2 ± √2")
    check(np.linalg.matrix_rank(M12 - 2 * I2) == 1 and np.allclose(np.linalg.eigvals(M12), [2, 2]),
          "п.12: λ=2 (alg=2), rank(M-2I)=1 -> geom=1")
    check(np.abs(np.linalg.eigvals(M13).imag).min() > 0.5, "п.13: вещественных собственных значений нет")
    check(all(np.allclose(M14 @ v, 2 * v) for v in np.random.default_rng(0).normal(size=(5, 2))),
          "п.14: M14 v = 2 v для любого v")
    check(not np.allclose(A15 @ B15, B15 @ A15), "п.15: AB != BA")
    check(np.allclose(A16 @ B16, B16 @ A16), "п.16: AB = BA")
    check(np.allclose(B16, 3 * I2 + 5 * A16) and np.isclose(det(B16), -16)
          and np.allclose(np.sort(np.linalg.eigvalsh(B16)), [-2, 8]), "п.16: B = 3I + 5A, собств. числа 8 и -2")
    # площади: |det| — коэффициент изменения площади
    def area(p):
        x, y = p[:, 0], p[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    S0 = area(polygon)
    for name, M in [("M6", M6), ("M9", M9), ("M10", M10)]:
        check(np.isclose(area(polygon @ M.T), abs(det(M)) * S0), f"{name}: площадь образа = |det|·площадь")


# ----------------------------------------------------------- рисование
BLUE, RED, GREEN = "tab:blue", "tab:red", "tab:green"
EIG_COLORS = ["tab:green", "tab:orange", "tab:purple", "tab:brown"]
R_UNIT = 1 / np.sqrt(np.pi)  # радиус круга единичной площади


def apply(M, pts):
    return pts @ M.T


def closed(pts):
    return np.vstack([pts, pts[:1]])


def line(v, label, color, ls="--"):
    return dict(v=np.asarray(v, float), label=label, color=color, ls=ls)


def eig_lines(M):
    """Прямые вещественных собственных векторов (если они есть)."""
    w, V = np.linalg.eig(M)
    if np.abs(w.imag).max() > 1e-9:
        return []
    w, V = w.real, V.real
    res = []
    for k in range(2):
        v = V[:, k]
        if any(collinear(v, l["v"]) for l in res):
            continue
        res.append(line(v, f"собств. прямая, λ = {w[k]:.3g}", EIG_COLORS[len(res)]))
    return res


def any_lines(lam):
    """Для M = λI любая прямая через начало — собственная: рисуем несколько."""
    res = []
    for k, ang in enumerate([0, 45, 90, 135]):
        t = np.radians(ang)
        lab = f"любая прямая — собственная (λ = {lam:g})" if k == 0 else None
        res.append(line([np.cos(t), np.sin(t)], lab, EIG_COLORS[k]))
    return res


def draw_poly(ax, pts, color, label=None, ls="-", fill=True):
    p = closed(pts)
    if fill:
        ax.fill(p[:, 0], p[:, 1], facecolor=color, edgecolor="none", alpha=0.35, zorder=2)
    ax.plot(p[:, 0], p[:, 1], ls, color=color, lw=1.6, marker="o", ms=3, label=label, zorder=3)


def circle_pts(M=None):
    t = np.linspace(0, 2 * np.pi, 300)
    pts = R_UNIT * np.c_[np.cos(t), np.sin(t)]
    return pts if M is None else apply(M, pts)


def draw_panel(ax, M, title, lines=(), circle=False, lim=None, image=True,
               image_label="Образ", image_color=RED):
    pts = polygon
    img = apply(M, polygon)
    arrays = [pts]
    draw_poly(ax, pts, BLUE, "Исходный многоугольник")
    if image:
        draw_poly(ax, img, image_color, image_label)
        arrays.append(img)
    if circle:
        c0, c1 = circle_pts(), circle_pts(M)
        ax.plot(c0[:, 0], c0[:, 1], ":", color="navy", lw=2, label="Круг площади 1", zorder=4)
        ax.plot(c1[:, 0], c1[:, 1], ":", color="darkred", lw=2, label=f"Образ круга (площадь {abs(np.linalg.det(M)):.3g})", zorder=4)
        arrays += [c0, c1]
    for l in lines:
        ax.axline((0, 0), tuple(l["v"]), color=l["color"], ls=l.get("ls", "--"), lw=1.3, label=l["label"], zorder=1)
    if lim is None:
        lim = 1.2 * max(np.abs(np.vstack(arrays)).max(), 1.0)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=7, loc="best")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(GRAPHICS / f"{name}.png", dpi=150)
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (name + '.png')}")


def plot_single(M, title, fname, lines=None, circle=False, **kw):
    fig, ax = plt.subplots(figsize=(7, 7))
    draw_panel(ax, M, title, eig_lines(M) if lines is None else lines, circle=circle, **kw)
    save(fig, fname)


def plot_pair(A, B, title, fname, names, third_label, same):
    """Сетка 2x3: исходный, A, B, AB, BA и наложение AB и BA."""
    AB, BA = A @ B, B @ A
    pts_all = np.vstack([polygon] + [apply(M, polygon) for M in (A, B, AB, BA)])
    lim = 1.2 * np.abs(pts_all).max()
    fig, axes = plt.subplots(2, 3, figsize=(16, 10.5))
    ax = axes.flatten()
    draw_panel(ax[0], I2, "Исходный многоугольник", lim=lim, image=False)
    draw_panel(ax[1], A, f"A = {names[0]}", eig_lines(A), lim=lim, image_label="A·P")
    draw_panel(ax[2], B, f"B = {names[1]}", eig_lines(B), lim=lim, image_label="B·P")
    draw_panel(ax[3], AB, "AB (сначала B, затем A)", eig_lines(AB), lim=lim, image_label="AB·P")
    draw_panel(ax[4], BA, "BA (сначала A, затем B)", eig_lines(BA), lim=lim, image_label="BA·P", image_color=GREEN)
    # наложение
    draw_poly(ax[5], polygon, BLUE, "Исходный", fill=False)
    draw_poly(ax[5], apply(AB, polygon), RED, "AB")
    draw_poly(ax[5], apply(BA, polygon), GREEN, "BA", ls="--" if same else "-", fill=not same)
    ax[5].set_xlim(-lim, lim); ax[5].set_ylim(-lim, lim); ax[5].set_aspect("equal")
    ax[5].axhline(0, color="black", lw=0.5); ax[5].axvline(0, color="black", lw=0.5)
    ax[5].grid(True, alpha=0.3); ax[5].legend(fontsize=7, loc="best")
    ax[5].set_title(third_label, fontsize=11)
    fig.suptitle(title, fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(GRAPHICS / f"{fname}.png", dpi=130)
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (fname + '.png')}")


def main():
    run_checks()
    print()

    plot_single(I2, "Исходный многоугольник", "p0_polygon", lines=[], image=False)
    plot_single(M1, f"Пункт 1. Отражение относительно y={a}x", "p1_reflection_y3x")
    plot_single(M2, f"Пункт 2. Проекция на прямую y={b}x", "p2_projection_y4x")
    plot_single(M3, f"Пункт 3. Поворот на {10*c}° против часовой", "p3_rotation_20deg")
    plot_single(M4, "Пункт 4. Центральная симметрия", "p4_central_symmetry", lines=any_lines(-1))
    plot_single(M5, f"Пункт 5. Отражение y={a}x, затем поворот на {10*d}° по часовой",
                "p5_reflect_then_rotate_50cw")
    plot_single(M6, f"Пункт 6. y=0 → y={a}x, x=0 → y={b}x", "p6_map_y0_to_y3x", lines=[
        line([1, 0], "прообраз: y=0", "tab:blue", ":"),
        line([0, 1], "прообраз: x=0", "tab:cyan", ":"),
        line([1, a], f"образ: y={a}x", "tab:red", "--"),
        line([1, b], f"образ: y={b}x", "tab:orange", "--"),
    ])
    plot_single(M7, f"Пункт 7. y={a}x → y=0, y={b}x → x=0", "p7_map_y3x_to_y0", lines=[
        line([1, a], f"прообраз: y={a}x", "tab:blue", ":"),
        line([1, b], f"прообраз: y={b}x", "tab:cyan", ":"),
        line([1, 0], "образ: y=0", "tab:red", "--"),
        line([0, 1], "образ: x=0", "tab:orange", "--"),
    ])
    plot_single(M8, f"Пункт 8. Меняет местами y={a}x и y={b}x", "p8_swap_lines",
                lines=eig_lines(M8) + [line([1, a], f"y={a}x", "gray", ":"), line([1, b], f"y={b}x", "black", ":")])
    plot_single(M9, "Пункт 9. Недиагональная матрица: круг площади 1 → круг площади 2",
                "p9_nondiagonal_circle_2", circle=True)
    plot_single(M10, "Пункт 10. Недиагональная матрица: круг площади 1 → эллипс площади 5",
                "p10_nondiagonal_noncircle_5", circle=True)
    plot_single(M11, "Пункт 11. Перпендикулярные собственные векторы", "p11_perpendicular_eigenvectors")
    plot_single(M12, "Пункт 12. Один собственный вектор (жорданова клетка)", "p12_no_two_eigenvectors")
    plot_single(M13, "Пункт 13. Поворот на 90°: вещественных собственных векторов нет", "p13_no_real_eigenvectors")
    plot_single(M14, "Пункт 14. M = 2I: любой вектор собственный", "p14_any_vector_eigen", lines=any_lines(2))

    plot_pair(A15, B15, f"Пункт 15. AB ≠ BA (A — поворот на {10*c}°, B — отражение y={a}x)", "p15_AB_BA_composition",
              (f"поворот {10*c}°", f"отражение y={a}x"), "AB и BA не совпадают", same=False)
    plot_pair(A16, B16, f"Пункт 16. AB = BA (A — отражение y={a}x, B = 3I + 5A)", "p16_AB_eq_BA",
              (f"отражение y={a}x", "[[-1,3],[3,7]]"), "AB и BA совпадают", same=True)

    # --- справочные числа для отчёта
    np.set_printoptions(precision=4, suppress=True)
    print("\nM5 =\n", M5, "\nM10 =\n", M10, "\nA15·B15 (AB) =\n", A15 @ B15, "\nB15·A15 (BA) =\n", B15 @ A15,
          "\nA16·B16 =\n", A16 @ B16)
    print("\nAll graphics saved to", GRAPHICS)


if __name__ == "__main__":
    main()
