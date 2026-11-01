#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №4 — Динамические системы
Практическая линейная алгебра
Студенты: Ануфриев А.С. (465029), Бахуров Н.А. (504862), Раджапов Ф.С. (502544)
Преподаватель: Зарина О.А.

Непрерывные системы  x'(t) = A x(t):      x(t) = exp(A t) x(0)
Дискретные системы   x(k+1) = A x(k):     x(k) = A^k x(0)

Все матрицы строятся как A = P M P^{-1}, где M — простая "модель" (диагональ,
жорданова клетка, блок поворота), а P — матрица из выбранных векторов.
Перед построением графиков все свойства проверяются численно (assert).

Запуск: python main.py (из любой папки). Графики сохраняются в ../graphics,
числа для отчёта — в ../report/matrices.tex.
"""

from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent.parent
GRAPHICS = ROOT / "graphics"
REPORT = ROOT / "report"
GRAPHICS.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)

I2 = np.eye(2)
RMAX = 12.0                       # траектории обрываются, когда |x| > RMAX
COLORS = ["tab:red", "tab:blue", "tab:green", "tab:orange", "tab:purple"]


# ====================================================================
# Общие инструменты
# ====================================================================
def jordan(lam):
    """Жорданова клетка 2x2."""
    return np.array([[lam, 1.0], [0.0, lam]])


def rot_block(alpha, beta):
    """Вещественный блок для пары alpha ± i beta: [[a, b], [-b, a]].
    Если A = P blk P^{-1}, то A (p1 + i p2) = (alpha + i beta)(p1 + i p2)."""
    return np.array([[alpha, beta], [-beta, alpha]])


def similar(M, P):
    return P @ M @ np.linalg.inv(P)


def is_defective(A):
    """True, если у A кратное собственное число с геометрической кратностью меньше алгебраической."""
    w = np.linalg.eigvals(A)
    if abs(w[0] - w[1]) > 1e-6:
        return False
    return np.linalg.matrix_rank(A - w[0].real * I2, tol=1e-7) == 1


def classify_cont(A):
    """Устойчивость непрерывной системы по собственным числам."""
    w = np.linalg.eigvals(A)
    m = w.real.max()
    if m < -1e-9:
        return "асимптотически устойчива"
    if m > 1e-9:
        return "неустойчива"
    # граница: Re = 0; устойчива, если нет жордановых клеток на мнимой оси
    return "неустойчива" if is_defective(A) else "устойчива, но не асимптотически"


def classify_disc(A):
    """Устойчивость дискретной системы по собственным числам."""
    w = np.linalg.eigvals(A)
    m = np.abs(w).max()
    if m < 1 - 1e-9:
        return "асимптотически устойчива"
    if m > 1 + 1e-9:
        return "неустойчива"
    return "неустойчива" if is_defective(A) else "устойчива, но не асимптотически"


def cont_traj(A, x0, t):
    return np.array([expm(A * ti) @ x0 for ti in t])


def disc_traj(A, x0, K):
    x = np.zeros((K + 1, 2))
    x[0] = x0
    for k in range(K):
        x[k + 1] = A @ x[k]
    return x


def collinear(u, v, tol=1e-9):
    return abs(u[0] * v[1] - u[1] * v[0]) < tol * max(1.0, np.linalg.norm(u) * np.linalg.norm(v))


def cut(t, x):
    """Обрывает траекторию в момент выхода за RMAX."""
    n = np.linalg.norm(x, axis=1)
    idx = np.where(n > RMAX)[0]
    if len(idx):
        return t[:idx[0]], x[:idx[0]]
    return t, x


def fvec(x):
    return "(" + ", ".join(f"{c:g}" for c in x) + ")"


# ====================================================================
# Задание 1. Непрерывные системы
# ====================================================================
v1 = np.array([2.0, 3.0])         # два неколлинеарных вектора вне осей координат
v2 = np.array([1.0, 2.0])
Pc = np.column_stack([v1, v2])    # det = 1
G = [np.array([-2.0, 1.0]), np.array([1.0, -3.0]), np.array([-3.0, -2.0])]   # "случайные" начальные условия

CONT = {
    1: dict(A=similar(np.diag([-1.0, -3.0]), Pc), ics=[v1, v2] + G,
            title="Пункт 1. λ = −1, −3 (устойчивый узел)", T=5, portrait="устойчивый узел"),
    2: dict(A=similar(jordan(1.0), Pc), ics=[v1, -v1, v2, G[0], G[1]],
            title="Пункт 2. λ = 1 (двукратное), жорданова клетка", T=2.4, portrait="неустойчивый вырожденный узел"),
    3: dict(A=similar(np.diag([-2.0, 1.0]), Pc), ics=[v1, v2] + G,
            title="Пункт 3. λ = −2, 1 (седло)", T=3, portrait="седло"),
    4: dict(A=similar(rot_block(-1.0, 2.0), Pc), ics=[v1, v2] + G,
            title="Пункт 4. λ = −1 ± 2i (устойчивый фокус)", T=6, portrait="устойчивый фокус"),
    5: dict(A=similar(rot_block(1.0, 2.0), Pc), ics=[v1, v2] + G,
            title="Пункт 5. λ = 1 ± 2i (неустойчивый фокус)", T=2.6, portrait="неустойчивый фокус"),
    6: dict(A=similar(rot_block(0.0, 2.0), Pc), ics=[v1, v2] + G,
            title="Пункт 6. λ = ±2i (центр)", T=10, portrait="центр"),
}

# ====================================================================
# Задание 2. Дискретные системы
# ====================================================================
Pd = np.array([[1.0, 1.0], [1.0, 2.0]])      # det = 1; не диагональная, не скалярная
cc, dd = 0.8, 1.2                            # 0 < c < 1,  d > 1
s2 = 1 / np.sqrt(2)
N = np.array([[0.0, 1.0], [0.0, 0.0]])


def polar_block(r, phi_deg):
    phi = np.radians(phi_deg)
    return rot_block(r * np.cos(phi), r * np.sin(phi))


DISC = {
    1: dict(core=jordan(-1.0), lam="λ = −1 (двукратное)"),
    2: dict(core=polar_block(1.0, 135), lam="λ = −1/√2 ± i/√2"),
    3: dict(core=polar_block(1.0, 90), lam="λ = ±i"),
    4: dict(core=polar_block(1.0, 45), lam="λ = 1/√2 ± i/√2"),
    5: dict(core=jordan(1.0), lam="λ = 1 (двукратное)"),
    6: dict(core=jordan(-cc), lam=f"λ = −c = −{cc} (двукратное)"),
    7: dict(core=polar_block(cc, 90), lam=f"λ = ±{cc}i"),
    8: dict(core=jordan(cc), lam=f"λ = c = {cc} (двукратное)"),
    9: dict(core=jordan(-dd), lam=f"λ = −d = −{dd} (двукратное)"),
    10: dict(core=polar_block(dd, 90), lam=f"λ = ±{dd}i"),
    11: dict(core=jordan(dd), lam=f"λ = d = {dd} (двукратное)"),
    12: dict(core=N, lam="λ = 0 (двукратное)"),
}
for k, d in DISC.items():
    d["A"] = similar(d["core"], Pd)
    d["eig"] = np.linalg.eigvals(d["A"])
DISC_X0 = [np.array([2.0, 1.0]), np.array([-1.0, 2.0]), np.array([1.5, -1.0])]
KSTEPS = 25

# ====================================================================
# Задание 3. Осциллятор x1' = x2, x2' = a x1 + b x2
# ====================================================================
OSC = {
    1: dict(a=-4.0, b=0.0, T=10, title="Случай 1. a < 0, b = 0 (центр)"),
    2: dict(a=-4.0, b=-0.6, T=10, title="Случай 2. a < 0, b < 0 (устойчивый фокус)"),
    3: dict(a=4.0, b=0.0, T=2.0, title="Случай 3. a > 0, b = 0 (седло)"),
    4: dict(a=4.0, b=-1.0, T=2.2, title="Случай 4. a > 0, b < 0 (седло)"),
}
for d in OSC.values():
    d["A"] = np.array([[0.0, 1.0], [d["a"], d["b"]]])
OSC_X0 = [np.array([1.0, 0.0]), np.array([0.0, 2.0]), np.array([-1.5, 1.0]), np.array([2.0, -1.0])]


# ====================================================================
# Проверки
# ====================================================================
def check(cond, msg):
    assert cond, f"ОШИБКА: {msg}"
    print("OK  ", msg)


def run_checks():
    t = np.linspace(0, 3, 31)
    # --- задание 1
    A = CONT[1]["A"]
    check(np.allclose(A, [[5, -4], [12, -9]]), "п.1: A = [[5,-4],[12,-9]]")
    check(classify_cont(A) == "асимптотически устойчива", "п.1: асимптотически устойчива")
    check(all(collinear(x, v1) for x in cont_traj(A, v1, t)) and all(collinear(x, v2) for x in cont_traj(A, v2, t)),
          "п.1: x(0)=v1 -> x(t) в Span{v1}; x(0)=v2 -> x(t) в Span{v2}")
    A = CONT[2]["A"]
    check(classify_cont(A) == "неустойчива" and is_defective(A), "п.2: неустойчива, нет двух неколлинеарных собственных векторов")
    check(np.allclose(A @ v1, v1) and np.allclose((A - I2) @ v2, v1), "п.2: v1 — собственный, v2 — обобщённый")
    A = CONT[3]["A"]
    check(classify_cont(A) == "неустойчива", "п.3: неустойчива")
    check(np.allclose(expm(A * 3) @ v1, np.exp(-6) * v1, rtol=1e-6, atol=1e-12) and np.allclose(A @ v1, -2 * v1), "п.3: x(0)=v1 -> x(t) = e^{-2t} v1 -> 0")
    for k, (al, be) in {4: (-1.0, 2.0), 5: (1.0, 2.0), 6: (0.0, 2.0)}.items():
        A = CONT[k]["A"]
        check(np.allclose(A @ (v1 + 1j * v2), (al + 1j * be) * (v1 + 1j * v2)) and np.allclose(A @ (v1 - 1j * v2), (al - 1j * be) * (v1 - 1j * v2)),
              f"п.{k}: собственные векторы v1 ± i v2, λ = {al} ± {be}i")
    check(classify_cont(CONT[4]["A"]) == "асимптотически устойчива", "п.4: асимптотически устойчива")
    check(classify_cont(CONT[5]["A"]) == "неустойчива", "п.5: неустойчива")
    check(classify_cont(CONT[6]["A"]) == "устойчива, но не асимптотически", "п.6: устойчива, но не асимптотически")
    # exp(At) совпадает с численным интегрированием
    for k in (3, 5):
        A = CONT[k]["A"]
        sol = solve_ivp(lambda tt, x: A @ x, [0, 1.5], G[0], rtol=1e-10, atol=1e-12)
        check(np.allclose(sol.y[:, -1], expm(A * 1.5) @ G[0], atol=1e-6), f"п.{k}: exp(At) x0 совпадает с solve_ivp")

    # --- задание 2
    expected = {1: "неустойчива", 2: "устойчива, но не асимптотически", 3: "устойчива, но не асимптотически",
                4: "устойчива, но не асимптотически", 5: "неустойчива", 6: "асимптотически устойчива",
                7: "асимптотически устойчива", 8: "асимптотически устойчива", 9: "неустойчива",
                10: "неустойчива", 11: "неустойчива", 12: "асимптотически устойчива"}
    target = {1: [-1, -1], 2: [-s2 + 1j * s2, -s2 - 1j * s2], 3: [1j, -1j], 4: [s2 + 1j * s2, s2 - 1j * s2], 5: [1, 1],
              6: [-cc, -cc], 7: [1j * cc, -1j * cc], 8: [cc, cc], 9: [-dd, -dd], 10: [1j * dd, -1j * dd], 11: [dd, dd], 12: [0, 0]}
    for k, d in DISC.items():
        A = d["A"]
        w = np.sort_complex(np.linalg.eigvals(A))
        check(np.allclose(w, np.sort_complex(np.array(target[k], dtype=complex)), atol=1e-6), f"дискр. п.{k}: {d['lam']}")
        check(not np.allclose(A, np.diag(np.diag(A))) and not (abs(A[0, 0] - A[1, 1]) < 1e-12 and abs(A[1, 0]) < 1e-12),
              f"дискр. п.{k}: A не диагональна и не жорданова клетка")
        check(classify_disc(A) == expected[k], f"дискр. п.{k}: {expected[k]}")
        x = disc_traj(A, DISC_X0[0], 6)
        check(np.allclose(x[6], np.linalg.matrix_power(A, 6) @ DISC_X0[0]), f"дискр. п.{k}: x(k) = A^k x(0)")
    check(np.allclose(np.linalg.matrix_power(DISC[12]["A"], 2), 0), "дискр. п.12: A^2 = 0 (нильпотентная матрица)")
    p1 = Pd[:, 0]
    check(np.allclose(DISC[1]["A"] @ p1, -p1) and np.allclose(DISC[5]["A"] @ p1, p1), "дискр. п.1, 5: p1 — собственный вектор")

    # --- задание 3
    exp3 = {1: "устойчива, но не асимптотически", 2: "асимптотически устойчива", 3: "неустойчива", 4: "неустойчива"}
    for k, d in OSC.items():
        check(classify_cont(d["A"]) == exp3[k], f"осциллятор, случай {k}: {exp3[k]}")
    for k in (3, 4):
        w, V = np.linalg.eig(OSC[k]["A"])
        j = np.argmin(w.real)
        check(w.real.min() < 0 < w.real.max() and np.allclose(expm(OSC[k]["A"] * 2) @ V[:, j].real, np.exp(2 * w[j].real) * V[:, j].real, rtol=1e-6),
              f"осциллятор, случай {k}: седло, устойчивое направление — собственный вектор с λ<0")


# ====================================================================
# Графики
# ====================================================================
def save(fig, name, dpi=130):
    fig.tight_layout()
    fig.savefig(GRAPHICS / f"{name}.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (name + '.png')}")


def eig_directions(A):
    """Вещественные собственные направления (если есть)."""
    w, V = np.linalg.eig(A)
    if np.abs(w.imag).max() > 1e-9:
        return []
    res = []
    for k in range(2):
        v = V[:, k].real
        if any(collinear(v / np.linalg.norm(v), u[1] / np.linalg.norm(u[1]), 1e-6) for u in res):
            continue
        res.append((w[k].real, v))
    return res


def phase_axes(ax, trajs, A, title, show_eig=True):
    allp = np.vstack([x for _, x in trajs])
    lim = 1.2 * max(np.abs(allp).max(), 1.0)
    if show_eig:
        for k, (lam, v) in enumerate(eig_directions(A)):
            ax.axline((0, 0), tuple(v), color="gray", ls="--", lw=1, label=f"собств. прямая, λ={lam:g}")
    for (c, x), col in zip(trajs, COLORS):
        pass
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color="k", lw=0.4)
    ax.axvline(0, color="k", lw=0.4)
    ax.grid(alpha=0.3)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title(title, fontsize=10)


def plot_cont(A, ics, T, name, title, labels=None, npts=900):
    t = np.linspace(0, T, npts)
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
    trajs = []
    for i, (x0, col) in enumerate(zip(ics, COLORS)):
        tt, x = cut(t, cont_traj(A, x0, t))
        lab = f"x(0)=({x0[0]:g}, {x0[1]:g})"
        axs[0].plot(tt, x[:, 0], color=col, lw=1.6, label=lab)
        axs[1].plot(tt, x[:, 1], color=col, lw=1.6, label=lab)
        trajs.append((col, x))
    phase_axes(axs[2], trajs, A, "Фазовые траектории $x_2(x_1)$")
    for (col, x) in trajs:
        axs[2].plot(x[:, 0], x[:, 1], color=col, lw=1.6)
        axs[2].plot(x[0, 0], x[0, 1], "o", color=col, ms=5)
        i = max(1, len(x) // 4)
        if len(x) > i + 1:
            axs[2].annotate("", xy=x[i + 1], xytext=x[i], arrowprops=dict(arrowstyle="->", color=col, lw=1.6))
    if axs[2].get_legend_handles_labels()[0]:
        axs[2].legend(fontsize=7, loc="upper right")
    ymax = 1.2 * max(max(np.abs(x).max() for _, x in trajs), 1.0)
    for ax, nm in zip(axs[:2], ("$x_1(t)$", "$x_2(t)$")):
        ax.set_xlabel("t")
        ax.set_title(nm, fontsize=10)
        ax.set_ylim(-ymax, ymax)
        ax.grid(alpha=0.3)
        ax.axhline(0, color="k", lw=0.4)
    axs[0].legend(fontsize=7, loc="best")
    fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(GRAPHICS / f"{name}.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (name + '.png')}")


def plot_disc(A, x0s, K, name, title, eigs, labels_ic=True):
    k = np.arange(K + 1)
    fig, axs = plt.subplots(1, 4, figsize=(18, 4.2), gridspec_kw=dict(width_ratios=[1, 1, 1, 0.9]))
    allx = []
    for x0, col in zip(x0s, COLORS):
        x = disc_traj(A, x0, K)
        allx.append(x)
        lab = f"x(0)=({x0[0]:g}, {x0[1]:g})"
        axs[0].plot(k, x[:, 0], "o-", color=col, ms=3, lw=1, label=lab)
        axs[1].plot(k, x[:, 1], "o-", color=col, ms=3, lw=1, label=lab)
        axs[2].plot(x[:, 0], x[:, 1], "o-", color=col, ms=3, lw=0.8)
        axs[2].plot(x[0, 0], x[0, 1], "s", color=col, ms=7, mfc="none")
    allx = np.vstack(allx)
    lim = 1.15 * max(np.abs(allx).max(), 1e-3)
    axs[2].set_xlim(-lim, lim); axs[2].set_ylim(-lim, lim); axs[2].set_aspect("equal")
    axs[2].set_xlabel("$x_1$"); axs[2].set_ylabel("$x_2$"); axs[2].set_title("Фазовые кривые $x_2(x_1)$", fontsize=10)
    for ax, nm in zip(axs[:2], ("$x_1(k)$", "$x_2(k)$")):
        ax.set_xlabel("k"); ax.set_title(nm, fontsize=10)
        ax.set_ylim(-lim, lim)
    axs[0].legend(fontsize=7)
    for ax in axs[:3]:
        ax.grid(alpha=0.3)
        ax.axhline(0, color="k", lw=0.4)
    axs[2].axvline(0, color="k", lw=0.4)
    # собственные числа на комплексной плоскости
    th = np.linspace(0, 2 * np.pi, 400)
    axs[3].plot(np.cos(th), np.sin(th), "--", color="gray", lw=1)
    axs[3].plot(eigs.real, eigs.imag, "o", color="tab:red", ms=8)
    axs[3].set_xlim(-1.6, 1.6); axs[3].set_ylim(-1.6, 1.6); axs[3].set_aspect("equal")
    axs[3].axhline(0, color="k", lw=0.4); axs[3].axvline(0, color="k", lw=0.4)
    axs[3].set_xlabel("Re λ"); axs[3].set_ylabel("Im λ")
    axs[3].set_title("Собственные числа", fontsize=10); axs[3].grid(alpha=0.3)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(GRAPHICS / f"{name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (name + '.png')}")


def task1():
    for k, d in CONT.items():
        plot_cont(d["A"], d["ics"], d["T"], f"c{k}_system", d["title"])
    # устойчивые траектории неустойчивой системы п.3 (седло): x(0) на Span{v1}
    plot_cont(CONT[3]["A"], [v1, -v1, 0.5 * v1], 4, "c3_stable_only",
              "Пункт 3. Устойчивые траектории: $x(0)\\in$ Span{v1} (сходятся к нулю)")


def task2():
    for k, d in DISC.items():
        plot_disc(d["A"], DISC_X0, KSTEPS, f"d{k}_system", f"Дискретная система, пункт {k}: {d['lam']}", d["eig"])
    # ограниченные траектории неустойчивых систем 1 и 5 (x(0) — собственный вектор)
    p1 = Pd[:, 0]
    for k in (1, 5):
        plot_disc(DISC[k]["A"], [p1, -p1], KSTEPS, f"d{k}_stable_only",
                  f"Пункт {k}. Устойчивые траектории: $x(0)$ — собственный вектор $p_1$", DISC[k]["eig"])
    # все собственные числа на одной плоскости
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), "--", color="gray", lw=1, label="|λ| = 1")
    groups = {"|λ|=1": ("tab:blue", range(1, 6)), f"|λ|=c={cc}": ("tab:green", (6, 7, 8)),
              f"|λ|=d={dd}": ("tab:red", (9, 10, 11)), "λ=0": ("k", (12,))}
    for name, (col, ks) in groups.items():
        first = True
        for k in ks:
            for z in np.unique(np.round(DISC[k]["eig"], 9)):
                ax.plot(z.real, z.imag, "o", color=col, ms=8, label=name if first else None)
                first = False
                ax.annotate(str(k), (z.real, z.imag), textcoords="offset points", xytext=(6, 6), fontsize=10, color=col)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect("equal")
    ax.axhline(0, color="k", lw=0.5); ax.axvline(0, color="k", lw=0.5); ax.grid(alpha=0.3)
    ax.set_xlabel("Re λ"); ax.set_ylabel("Im λ"); ax.legend(loc="lower right", fontsize=9)
    ax.set_title("Собственные числа дискретных систем (номера — пункты задания 2)")
    save(fig, "d_eigenvalues")


def task3():
    for k, d in OSC.items():
        plot_cont(d["A"], OSC_X0, d["T"], f"o{k}_system", d["title"] + f"  (a = {d['a']:g}, b = {d['b']:g})")
    for k in (3, 4):
        w, V = np.linalg.eig(OSC[k]["A"])
        vs = V[:, np.argmin(w.real)].real
        vs = vs / abs(vs[0])
        plot_cont(OSC[k]["A"], [vs, -vs, 0.5 * vs], 4, f"o{k}_stable_only",
                  f"Случай {k}. Устойчивые траектории: $x(0)\\in$ Span{{(1, {vs[1]:.4g})}} (сходятся к нулю)")


# ====================================================================
# Экспорт для отчёта
# ====================================================================
def fnum(x, p=4):
    s = f"{x:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def tex_mat(M, p=4):
    rows = r" \\ ".join(" & ".join(fnum(x, p) for x in row) for row in M)
    return r"\begin{pmatrix}" + rows + r"\end{pmatrix}"


def tex_c(z, p=4):
    z = complex(z)
    if abs(z.imag) < 1e-12:
        return fnum(z.real, p)
    re = "" if abs(z.real) < 1e-12 else fnum(z.real, p)
    im = fnum(abs(z.imag), p)
    sign = "-" if z.imag < 0 else "+"
    if re == "":
        return ("-" if z.imag < 0 else "") + im + "i"
    return f"{re}{sign}{im}i"


def export():
    defs = {"MatPc": tex_mat(Pc), "MatPcinv": tex_mat(np.linalg.inv(Pc)),
            "MatPd": tex_mat(Pd), "MatPdinv": tex_mat(np.linalg.inv(Pd))}
    for k, d in CONT.items():
        defs["MatC" + "ABCDEF"[k - 1]] = tex_mat(d["A"])
    letters = "ABCDEFGHIJKL"
    for k, d in DISC.items():
        defs["MatD" + letters[k - 1]] = tex_mat(d["A"])
        defs["EigD" + letters[k - 1]] = ", ".join(tex_c(z) for z in np.unique(np.round(d["eig"], 9)))
    for k, d in OSC.items():
        defs["MatO" + "ABCD"[k - 1]] = tex_mat(d["A"])
        w, V = np.linalg.eig(d["A"])
        order = np.argsort(-w.imag if np.abs(w.imag).max() > 1e-9 else -w.real)
        defs["EigO" + "ABCD"[k - 1]] = ",\\ ".join(tex_c(w[i]) for i in order)
        defs["VecO" + "ABCD"[k - 1]] = ",\\ ".join(
            "(1,\\ " + tex_c(w[i]) + ")^T" for i in order)
    lines = ["% Файл создаётся автоматически программой prog/main.py — не править вручную"]
    for key, val in defs.items():
        lines.append(f"\\newcommand{{\\{key}}}{{{val}}}")
    (REPORT / "matrices.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved:", REPORT / "matrices.tex")


def main():
    run_checks()
    print()
    task1()
    task2()
    task3()
    export()
    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    for k, d in CONT.items():
        print(f"\nA(непр. {k}) =\n", d["A"], "\nλ =", np.linalg.eigvals(d["A"]))
    print("\nAll graphics saved to", GRAPHICS)


if __name__ == "__main__":
    main()
