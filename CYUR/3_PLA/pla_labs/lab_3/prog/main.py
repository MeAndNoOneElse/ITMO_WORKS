#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №3 — Матрицы в 3D-графике
Практическая линейная алгебра
Студенты: Ануфриев А.С. (465029), Бахуров Н.А. (504862), Раджапов Ф.С. (502544)
Преподаватель: Зарина О.А.

Все преобразования координат выполняются матрицами 4x4 в однородных координатах.
Соглашение: вектор-столбец, p' = M p; композиция "сначала A, потом B" = B @ A.
Камера смотрит вдоль оси +z, ось x направлена вправо, ось y вниз
(вид "снизу": ax.view_init(azim=0, elev=-90)).

Запуск: python main.py (из любой папки). Графики сохраняются в ../graphics,
числовые значения матриц для отчёта — в ../report/matrices.tex.
"""

from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parent.parent
GRAPHICS = ROOT / "graphics"
REPORT = ROOT / "report"
GRAPHICS.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)

# ====================================================================
# Задание 1. Фигуры: вершины (4 x N, однородные координаты) и грани
# ====================================================================
vertices_cube = np.array([
    [-1, 1, 1, -1, -1, 1, 1, -1],
    [-1, -1, 1, 1, -1, -1, 1, 1],
    [-1, -1, -1, -1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
], dtype=float)

faces_cube = [
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [2, 3, 7, 6],
    [3, 0, 4, 7],
    [0, 1, 2, 3],
    [4, 5, 6, 7],
]

# Другая фигура: четырёхугольная пирамида (грани разной длины: 1 квадрат + 4 треугольника)
vertices_pyramid = np.array([
    [-1, 1, 1, -1, 0],
    [-1, -1, 1, 1, 0],
    [-1, -1, -1, -1, 1],
    [1, 1, 1, 1, 1],
], dtype=float)
faces_pyramid = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]

# Треугольная призма (для крыши домика): треугольник в плоскости y-z, вытянут вдоль x
vertices_prism = np.array([
    [-1, -1, -1, 1, 1, 1],
    [-1, 1, 0, -1, 1, 0],
    [0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1],
], dtype=float)
faces_prism = [[0, 1, 2], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]]

CUBE_FACE_COLORS = ["#e41a1c", "#4daf4a", "#ff7f00", "#984ea3", "#377eb8", "#ffd92f"]
PYRAMID_COLORS = ["#377eb8", "#e41a1c", "#4daf4a", "#ff7f00", "#984ea3"]

# Фигура = (вершины, грани, цвет/цвета)
CUBE = (vertices_cube, faces_cube, CUBE_FACE_COLORS)


def draw_shape(ax, vertices, faces, color, alpha=1.0, edge="k", lw=0.6, zorder=None):
    """Рисует многогранник. Деление на 4-ю координату — переход к декартовым координатам."""
    pts = (vertices[:3, :] / vertices[3, :]).T
    polys = [pts[list(f)] for f in faces]
    coll = Poly3DCollection(polys, facecolors=color, edgecolors=edge, linewidths=lw, alpha=alpha)
    if zorder is not None:
        coll.set_zorder(zorder)
    ax.add_collection3d(coll)
    return pts


# ====================================================================
# Матрицы преобразований (все 4x4)
# ====================================================================
I4 = np.eye(4)


def S(sx, sy, sz):
    """Масштабирование по осям."""
    return np.diag([sx, sy, sz, 1.0])


def T(tx, ty, tz):
    """Перемещение (сдвиг) на вектор (tx, ty, tz)."""
    M = np.eye(4)
    M[:3, 3] = [tx, ty, tz]
    return M


def J_matrix(v):
    """Кососимметрическая матрица J = [v/|v|]_x, расширенная до 4x4."""
    x, y, z = np.asarray(v, float) / np.linalg.norm(v)
    return np.array([[0, -z, y, 0],
                     [z, 0, -x, 0],
                     [-y, x, 0, 0],
                     [0, 0, 0, 0]], dtype=float)


def Rv(v, theta):
    """Поворот на угол theta вокруг оси v через начало координат: R = exp(J*theta)."""
    return expm(J_matrix(v) * theta)


def Rv_rodrigues(v, theta):
    """То же по формуле Родрига: R = I + sin(t) J + (1 - cos(t)) J^2 (на блоке 3x3)."""
    J = J_matrix(v)
    R = np.eye(4) + np.sin(theta) * J + (1 - np.cos(theta)) * (J @ J)
    R[3, 3] = 1.0
    return R


def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], float)


def Ry(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], float)


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float)


def R_about_point(v, theta, M):
    """Поворот вокруг оси с направлением v, проходящей через точку M: T(M) R_v T(-M)."""
    M = np.asarray(M, float)
    return T(*M) @ Rv(v, theta) @ T(*(-M))


def axis_angle(R):
    """Ось и угол поворота по матрице (задача 9 из контрольных вопросов)."""
    R3 = R[:3, :3]
    theta = np.arccos(np.clip((np.trace(R3) - 1) / 2, -1, 1))
    w = np.array([R3[2, 1] - R3[1, 2], R3[0, 2] - R3[2, 0], R3[1, 0] - R3[0, 1]])
    return w / np.linalg.norm(w), theta


def perspective(n, f, l, r, b, t):
    """Матрица перспективы для камеры, смотрящей вдоль +z.
    Усечённая пирамида (frustum) [l,r]x[b,t] на плоскости z=n, дальняя плоскость z=f
    отображается в куб [-1,1]^3: z=n -> -1, z=f -> +1."""
    return np.array([
        [2 * n / (r - l), 0, -(r + l) / (r - l), 0],
        [0, 2 * n / (t - b), -(t + b) / (t - b), 0],
        [0, 0, (f + n) / (f - n), -2 * f * n / (f - n)],
        [0, 0, 1, 0],
    ], dtype=float)


def perspective_fov(fov_deg, aspect, n, f):
    t = n * np.tan(np.radians(fov_deg) / 2)
    r = t * aspect
    return perspective(n, f, -r, r, -t, t)


def look_at(c, target, up):
    """Камера в точке c, смотрит на target; ось y камеры направлена "вниз" (против up).
    Возвращает Tc, Rc: C = Tc @ Rc переводит координаты камеры в мировые."""
    c, target, up = (np.asarray(a, float) for a in (c, target, up))
    z = target - c
    z /= np.linalg.norm(z)
    y = -(up - (up @ z) * z)
    y /= np.linalg.norm(y)
    x = np.cross(y, z)
    Rc = np.eye(4)
    Rc[:3, :3] = np.c_[x, y, z]
    return T(*c), Rc


# ====================================================================
# Параметры заданий
# ====================================================================
deg = np.radians

# Задание 2
S1 = S(2, 1, 1.5)
S2 = S(0.5, 2, 2)
S12 = S2 @ S1                       # сначала S1, потом S2

# Задание 3
T1 = T(2, 1, 0)
T2 = T(-1, 0, 2)
T12 = T2 @ T1
TS = T12 @ S12                      # масштабирование, затем перемещение
ST = S12 @ T12                      # перемещение, затем масштабирование

# Задание 4
v1, th1 = np.array([1.0, 2.0, 2.0]), deg(60)
v2, th2 = np.array([2.0, -1.0, 2.0]), deg(45)
R1 = Rv(v1, th1)
R2 = Rv(v2, th2)
R21 = R2 @ R1                       # сначала R1, затем R2
R12 = R1 @ R2                       # сначала R2, затем R1

# Задание 5: вращение вокруг вершины куба
M_vertex = np.array([1.0, 1.0, 1.0])
v5, th5 = np.array([1.0, 1.0, 0.0]), deg(60)
R_vertex = R_about_point(v5, th5, M_vertex)

# Задание 6: сцена из трёх кубиков и камера
cube_cyan = (T(-3, 0, 0) @ S(2, 2, 2) @ vertices_cube, faces_cube, "cyan")
cube_blue = (vertices_cube, faces_cube, "blue")
cube_green = (T(3, 0, 0) @ Rz(deg(45)) @ vertices_cube, faces_cube, "lime")
scene = [cube_cyan, cube_blue, cube_green]

alpha_c, beta_c, dist_c = deg(25), deg(30), 12.0
Rc = Ry(beta_c) @ Rx(alpha_c)
cam_pos = -dist_c * Rc[:3, 2]       # камера смотрит в начало координат с расстояния dist_c
Tc = T(*cam_pos)
C = Tc @ Rc
Cinv = np.linalg.inv(C)

# Задание 7: перспектива
FOV, ASPECT, NEAR, FAR = 60.0, 1.0, 5.0, 25.0
P = perspective_fov(FOV, ASPECT, NEAR, FAR)

# ====================================================================
# Проверки
# ====================================================================
def check(cond, msg):
    assert cond, f"ОШИБКА: {msg}"
    print("OK  ", msg)


def to_cart(V):
    return V[:3] / V[3]


def run_checks():
    # Задание 2-3
    check(np.allclose(S12, np.diag([1, 2, 3, 1])), "S2 S1 = diag(1,2,3,1)")
    check(np.allclose(T12, T(1, 1, 2)), "T2 T1 = T(1,1,2): сдвиги складываются и коммутируют")
    check(np.allclose(T1 @ T2, T2 @ T1), "T1 T2 = T2 T1")
    check(np.allclose(S1 @ S2, S2 @ S1), "S1 S2 = S2 S1")
    t = T12[:3, 3]
    check(np.allclose(TS[:3, :3], S12[:3, :3]) and np.allclose(TS[:3, 3], t), "TS = [[S, t],[0,1]]")
    check(np.allclose(ST[:3, 3], S12[:3, :3] @ t), "ST = [[S, S t],[0,1]]")
    check(not np.allclose(TS, ST), "TS != ST")
    # Задание 4
    for v, th in [(v1, th1), (v2, th2), ([0, 0, 1], 1.0), ([1, 0, 0], 0.3)]:
        check(np.allclose(Rv(v, th), Rv_rodrigues(v, th)), f"exp(J t) совпадает с формулой Родрига, v={list(v)}")
    R3 = R1[:3, :3]
    check(np.allclose(R3.T @ R3, np.eye(3)) and np.isclose(np.linalg.det(R3), 1), "R1 ортогональна, det = 1")
    check(np.allclose(R1 @ np.r_[v1, 1], np.r_[v1, 1]), "R1 v1 = v1 (ось неподвижна)")
    check(np.allclose(Rv([1, 0, 0], 0.7), Rx(0.7)) and np.allclose(Rv([0, 1, 0], 0.7), Ry(0.7))
          and np.allclose(Rv([0, 0, 1], 0.7), Rz(0.7)), "Rv для осей x, y, z = Rx, Ry, Rz")
    check(not np.allclose(R21, R12), "R2 R1 != R1 R2")
    ax21, a21 = axis_angle(R21)
    check(np.allclose(R21 @ np.r_[ax21, 1], np.r_[ax21, 1]), "ось R2 R1 неподвижна (ось найдена по кососимметричной части)")
    ax12, a12 = axis_angle(R12)
    check(np.allclose(R12 @ np.r_[ax12, 1], np.r_[ax12, 1]), "ось R1 R2 неподвижна")
    check(np.isclose(np.trace(R21[:3, :3]), np.trace(R12[:3, :3])), "tr(R2R1) = tr(R1R2): одинаковый угол поворота")
    # Задание 5
    check(np.allclose(R_vertex @ np.r_[M_vertex, 1], np.r_[M_vertex, 1]), "вершина M неподвижна")
    check(np.allclose(R_vertex[:3, :3], Rv(v5, th5)[:3, :3]), "блок 3x3 равен R_v")
    check(np.allclose(R_vertex[:3, 3], M_vertex - Rv(v5, th5)[:3, :3] @ M_vertex), "сдвиг: M - R M")
    check(np.allclose(np.sort(np.abs(np.linalg.eigvals(R_vertex))), 1), "R_vertex подобна R_v: все |λ| = 1")
    # Задание 6
    check(np.allclose(C @ Cinv, I4), "C C^-1 = I")
    check(np.allclose(Cinv, np.linalg.inv(Rc) @ np.linalg.inv(Tc)) and np.allclose(Rc[:3, :3].T, np.linalg.inv(Rc[:3, :3])),
          "C^-1 = Rc^T Tc^-1")
    check(np.allclose(Cinv @ np.r_[cam_pos, 1], [0, 0, 0, 1]), "камера переходит в начало координат")
    check(np.allclose(Cinv @ np.r_[0, 0, 0, 1], [0, 0, dist_c, 1]), "центр сцены уходит на ось z на расстояние d")
    # Задание 7
    allv = np.hstack([Cinv @ V for V, _, _ in scene])
    z = allv[2]
    check(z.min() > NEAR and z.max() < FAR, f"все вершины между плоскостями: z in [{z.min():.2f}, {z.max():.2f}], внутри ({NEAR}, {FAR})")
    ndc = to_cart(P @ allv)
    check(np.abs(ndc).max() <= 1.0, f"после перспективы все вершины в кубе [-1,1]^3 (max |coord| = {np.abs(ndc).max():.3f})")
    check(np.allclose(to_cart(P @ np.r_[0, 0, NEAR, 1]), [0, 0, -1]) and np.allclose(to_cart(P @ np.r_[0, 0, FAR, 1]), [0, 0, 1]),
          "ближняя плоскость -> z=-1, дальняя -> z=+1")
    tt = NEAR * np.tan(np.radians(FOV) / 2)
    check(np.allclose(to_cart(P @ np.r_[tt, tt, NEAR, 1]), [1, 1, -1]), "угол ближней плоскости frustum -> (1,1,-1)")
    check(np.isclose((P @ np.r_[1, 2, 7, 1])[3], 7), "4-я координата после P равна z (перспективное деление)")


# ====================================================================
# Рисование
# ====================================================================
VIEW_STD = dict(elev=30, azim=-37.5)     # стандартный вид из листинга
VIEW_BELOW = dict(elev=-90, azim=0, roll=-90)  # вид "снизу" как на рис. 1 методички (x вправо, y вниз)
GHOST = dict(color="lightgray", alpha=0.18, edge="gray", lw=0.4)


def new_fig(n, size=5.2, rows=1):
    cols = int(np.ceil(n / rows))
    fig = plt.figure(figsize=(size * cols, size * rows))
    axes = [fig.add_subplot(rows, cols, i + 1, projection="3d", proj_type="ortho") for i in range(n)]
    return fig, axes


def finish(ax, pts, title="", view=VIEW_STD, margin=0.12, ticks=True, lim=None):
    """Равные масштабы по осям, пределы по облаку точек pts (N x 3)."""
    pts = np.vstack(pts)
    if lim is None:
        lo, hi = pts.min(0), pts.max(0)
        ctr, half = (lo + hi) / 2, (hi - lo).max() / 2 * (1 + margin)
        lim = [(c - half, c + half) for c in ctr]
    ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1]); ax.set_zlim(*lim[2])
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(**view)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title(title, fontsize=11)
    if ticks:
        ax.tick_params(labelsize=7)
    if abs(view.get("elev", 0)) == 90:      # смотрим вдоль оси z: подписи z не нужны
        ax.set_zticks([])
        ax.set_zlabel("")


def draw_axis(ax, v, M=(0, 0, 0), L=2.6, color="red"):
    """Вектор, коллинеарный оси вращения (со стрелкой) и пунктир вдоль всей оси."""
    v = np.asarray(v, float) / np.linalg.norm(v)
    M = np.asarray(M, float)
    a, b = M - L * v, M + L * v
    ax.plot(*zip(a, b), "--", color=color, lw=1)
    ax.quiver(*M, *v, length=L, color=color, lw=2.2, arrow_length_ratio=0.15)
    return np.array([a, b])


def save(fig, name, dpi=130):
    fig.tight_layout()
    fig.savefig(GRAPHICS / f"{name}.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {GRAPHICS / (name + '.png')}")


def pair(V, M, faces=faces_cube, colors=CUBE_FACE_COLORS, ghost=True):
    """Рисует образ M·V, опционально ghost — исходную фигуру; возвращает точки."""
    pts = []
    return pts


def panel(ax, objs, title, view=VIEW_STD, ghost_objs=(), extra_pts=(), **kw):
    """objs: список (V,faces,color) для рисования; ghost_objs — полупрозрачные исходные фигуры."""
    pts = []
    for V, faces, col in ghost_objs:
        pts.append(draw_shape(ax, V, faces, **{**GHOST, "color": GHOST["color"]}))
    for V, faces, col in objs:
        pts.append(draw_shape(ax, V, faces, col))
    pts += list(extra_pts)
    finish(ax, pts, title, view, **kw)
    return pts


def task1():
    # Результат кода из приложения: синий куб
    fig, (ax,) = new_fig(1, 5.5)
    draw_shape(ax, vertices_cube, faces_cube, "blue", edge="k", lw=0.8)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_box_aspect([1, 1, 1]); ax.view_init(azim=-37.5, elev=30)
    for setter in (ax.set_xticks, ax.set_yticks, ax.set_zticks):
        setter(np.linspace(-1, 1, 5))
    ax.set_title("Куб (vertices_cube, faces_cube)")
    save(fig, "t1_cube")
    # Другая фигура: пирамида
    fig, (ax,) = new_fig(1, 5.5)
    draw_shape(ax, vertices_pyramid, faces_pyramid, PYRAMID_COLORS)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_box_aspect([1, 1, 1]); ax.view_init(azim=-37.5, elev=30)
    for setter in (ax.set_xticks, ax.set_yticks, ax.set_zticks):
        setter(np.linspace(-1, 1, 5))
    ax.set_title("Пирамида (vertices_pyramid, faces_pyramid)")
    save(fig, "t1_pyramid")


def task2():
    mats = [(I4, "Исходный куб"), (S1, "S1 = diag(2, 1, 1.5)"), (S2, "S2 = diag(0.5, 2, 2)"), (S12, "S2·S1 = diag(1, 2, 3)")]
    fig, axes = new_fig(4, 4.6, rows=1)
    allp = []
    for ax, (M, title) in zip(axes, mats):
        allp.append(M @ vertices_cube)
    lim_pts = [to_cart(V).T for V in allp]
    for ax, (M, title) in zip(axes, mats):
        panel(ax, [(M @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], title,
              ghost_objs=[CUBE] if M is not I4 else (), extra_pts=lim_pts)
    save(fig, "t2_scale")


def task3():
    mats = [(T1, "T1 = T(2, 1, 0)"), (T2, "T2 = T(−1, 0, 2)"), (T12, "T2·T1 = T(1, 1, 2)")]
    fig, axes = new_fig(3, 4.6)
    lim = [to_cart(M @ vertices_cube).T for M, _ in mats]
    for ax, (M, title) in zip(axes, mats):
        panel(ax, [(M @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], title, ghost_objs=[CUBE], extra_pts=lim)
    save(fig, "t3_translate")

    mats = [(TS, "TS: сначала масштаб, потом сдвиг"), (ST, "ST: сначала сдвиг, потом масштаб")]
    fig, axes = new_fig(2, 6)
    lim = [to_cart(M @ vertices_cube).T for M, _ in mats] + [to_cart(vertices_cube).T]
    for ax, (M, title) in zip(axes, mats):
        panel(ax, [(M @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], title, ghost_objs=[CUBE], extra_pts=lim)
    save(fig, "t3_TS_ST")


def task4():
    # Две произвольные оси и углы, и их композиции двумя способами
    ax21, a21 = axis_angle(R21)
    ax12, a12 = axis_angle(R12)
    items = [
        (R1, v1, f"R1: v1=(1,2,2), θ1=60°"),
        (R2, v2, f"R2: v2=(2,−1,2), θ2=45°"),
        (R21, ax21, f"R2·R1 (сначала R1): θ≈{np.degrees(a21):.1f}°"),
        (R12, ax12, f"R1·R2 (сначала R2): θ≈{np.degrees(a12):.1f}°"),
    ]
    fig, axes = new_fig(4, 4.6)
    lim = [to_cart(M @ vertices_cube).T for M, _, _ in items] + [np.array([[-2.6] * 3, [2.6] * 3])]
    for ax, (M, v, title) in zip(axes, items):
        draw_axis(ax, v)
        panel(ax, [(M @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], title, ghost_objs=[CUBE], extra_pts=lim)
    save(fig, "t4_rotations")

    # Зависимость от угла: фиксированная ось v1
    angles = [30, 90, 150, 180]
    fig, axes = new_fig(4, 4.6)
    for ax, a in zip(axes, angles):
        draw_axis(ax, v1)
        panel(ax, [(Rv(v1, deg(a)) @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], f"v1=(1,2,2), θ = {a}°",
              ghost_objs=[CUBE], extra_pts=[np.array([[-2.6] * 3, [2.6] * 3])])
    save(fig, "t4_angles")

    # Зависимость от оси: Rx, Ry, Rz и диагональ (1,1,1) при θ = 45°
    axes_list = [([1, 0, 0], "Rx(45°)"), ([0, 1, 0], "Ry(45°)"), ([0, 0, 1], "Rz(45°)"), ([1, 1, 1], "v=(1,1,1), θ=45°")]
    fig, axes = new_fig(4, 4.6)
    for ax, (v, title) in zip(axes, axes_list):
        draw_axis(ax, v)
        panel(ax, [(Rv(v, deg(45)) @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], title,
              ghost_objs=[CUBE], extra_pts=[np.array([[-2.6] * 3, [2.6] * 3])])
    save(fig, "t4_axes")


def task5():
    fig, axes = new_fig(2, 6)
    for ax, view, title in zip(axes, [VIEW_STD, dict(elev=55, azim=-120)],
                               ["Вид 1", "Вид 2"]):
        line = draw_axis(ax, v5, M=M_vertex, L=2.4, color="red")
        ax.scatter(*M_vertex, color="black", s=40, zorder=20)
        ax.text(*(M_vertex + 0.15), "M(1,1,1)", fontsize=9)
        panel(ax, [(R_vertex @ vertices_cube, faces_cube, CUBE_FACE_COLORS)], f"{title}: поворот на 60° вокруг оси через вершину M",
              view=view, ghost_objs=[CUBE], extra_pts=[line, np.array([[-1.2] * 3, [1.2] * 3])])
    save(fig, "t5_vertex_rotation")


def camera_frame(ax, Cmat, size=2.5, label=True):
    """Оси камеры: x — красная, y — зелёная, z (направление взгляда) — синяя."""
    o = Cmat[:3, 3]
    pts = [o]
    for k, col in enumerate(["red", "green", "blue"]):
        d = Cmat[:3, k]
        ax.quiver(*o, *d, length=size, color=col, lw=2, arrow_length_ratio=0.15)
        pts.append(o + size * d)
    ax.scatter(*o, color="black", s=30)
    if label:
        ax.text(*(o + 0.3), "камера", fontsize=9)
    return np.array(pts)


def scene_pts(objs, M=I4):
    return [to_cart(M @ V).T for V, _, _ in objs]


def transformed(objs, M):
    return [(M @ V, f, c) for V, f, c in objs]


def task6():
    # Два вида исходной сцены (рисунки 1-2 методички)
    fig, (ax,) = new_fig(1, 6)
    panel(ax, scene, "Сцена: вид под стандартным углом камеры", view=VIEW_STD)
    save(fig, "t6_scene_standard")
    fig, (ax,) = new_fig(1, 6)
    panel(ax, scene, "Сцена: вид «снизу» (azim=0, elev=−90, roll=−90)", view=VIEW_BELOW)
    save(fig, "t6_scene_below")

    # Камера в мировых координатах и сцена в системе камеры
    fig, (ax,) = new_fig(1, 6.5)
    cp = camera_frame(ax, C, size=3.0)
    panel(ax, scene, "Камера в мировых координатах (матрица C = Tc·Rc)", view=VIEW_STD, extra_pts=[cp])
    save(fig, "t6_camera_world")

    fig, (ax,) = new_fig(1, 6)
    cp = camera_frame(ax, I4, size=3.0)
    panel(ax, transformed(scene, Cinv), "Сцена после C$^{-1}$ (камера в начале координат), вид «снизу»", view=VIEW_BELOW, extra_pts=[cp])
    save(fig, "t6_scene_camera")

    # Тот же результат под стандартным углом: видно, что сцена целиком сдвинута по оси z
    fig, (ax,) = new_fig(1, 6)
    cp = camera_frame(ax, I4, size=3.0)
    panel(ax, transformed(scene, Cinv), "Сцена после C$^{-1}$, стандартный угол", view=VIEW_STD, extra_pts=[cp])
    save(fig, "t6_scene_camera_std")


def frustum_lines(ax, n, f, fov, aspect=1.0, color="gray"):
    """Рёбра усечённой пирамиды видимости в системе камеры."""
    t = np.tan(np.radians(fov) / 2)
    r = t * aspect
    pts = np.array([[sx * r * z, sy * t * z, z] for z in (n, f) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]])
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in edges:
        ax.plot(*zip(pts[a], pts[b]), color=color, lw=0.9)
    o = np.zeros(3)
    for k in range(4, 8):
        ax.plot(*zip(o, pts[k]), color=color, lw=0.6, ls=":")
    return pts


def ndc_cube(ax, color="gray"):
    c = np.array([[sx, sy, sz] for sz in (-1, 1) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]], float)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in edges:
        ax.plot(*zip(c[a], c[b]), color=color, lw=0.9)
    return c


def task7():
    cam_scene = transformed(scene, Cinv)
    persp_scene = transformed(scene, P @ Cinv)

    # 1. Изометрическая (параллельная) камера и перспектива, вид «снизу»
    fig, axes = new_fig(2, 6.2)
    panel(axes[0], cam_scene, "Параллельная проекция (только C$^{-1}$)", view=VIEW_BELOW)
    pc = ndc_cube(axes[1])
    panel(axes[1], persp_scene, "Перспектива (P·C$^{-1}$), координаты после деления на w", view=VIEW_BELOW, extra_pts=[pc])
    save(fig, "t7_ortho_vs_persp")

    # 2. Деформация пространства: frustum -> куб
    fig, axes = new_fig(2, 6.2)
    fr = frustum_lines(axes[0], NEAR, FAR, FOV)
    panel(axes[0], cam_scene, "Система камеры: пирамида видимости (frustum)", view=dict(elev=20, azim=-60), extra_pts=[fr])
    pc = ndc_cube(axes[1])
    panel(axes[1], persp_scene, "После P: frustum стал кубом [−1, 1]³", view=dict(elev=20, azim=-60), extra_pts=[pc])
    save(fig, "t7_frustum_to_cube")

    # 3. Вращение стандартной камеры для изучения деформации
    views = [dict(elev=-90, azim=0), dict(elev=30, azim=-37.5), dict(elev=0, azim=0), dict(elev=0, azim=90)]
    fig, axes = new_fig(4, 4.6)
    pc = ndc_cube(axes[0])
    for ax, view in zip(axes, views):
        ndc_cube(ax)
        panel(ax, persp_scene, f"view_init(elev={view['elev']}, azim={view['azim']})", view=view, extra_pts=[pc])
    save(fig, "t7_views")


# ---------------------------------------------------------------- задание 8
def house():
    wall = (T(0, 0, 1.5) @ S(2.5, 2, 1.5) @ vertices_cube, faces_cube, "#f2d9a0")
    roof = (T(0, 0, 3) @ S(2.8, 2.3, 1.3) @ vertices_prism, faces_prism, "#b5473a")
    chimney = (T(1.5, 0.8, 3.8) @ S(0.3, 0.3, 0.8) @ vertices_cube, faces_cube, "#8c5a3c")
    door = (T(0, -2.05, 0.9) @ S(0.45, 0.06, 0.9) @ vertices_cube, faces_cube, "#5a3825")
    win1 = (T(-1.6, -2.05, 1.9) @ S(0.5, 0.06, 0.45) @ vertices_cube, faces_cube, "#9ed8f5")
    win2 = (T(1.6, -2.05, 1.9) @ S(0.5, 0.06, 0.45) @ vertices_cube, faces_cube, "#9ed8f5")
    shed = (T(5.5, -0.5, 0.75) @ Rz(deg(30)) @ S(1.0, 1.0, 0.75) @ vertices_cube, faces_cube, "#c9a66b")
    shed_roof = (T(5.5, -0.5, 1.5) @ Rz(deg(30)) @ S(1.1, 1.1, 0.5) @ vertices_prism, faces_prism, "#7a8b99")
    return [wall, roof, chimney, door, win1, win2, shed, shed_roof]


GROUND = np.array([[-7, 7, 7, -7], [-5, -5, 5, 5], [0, 0, 0, 0], [1, 1, 1, 1]], dtype=float)


def draw_house(ax, M, title, view, extra=()):
    ax.computed_zorder = False
    pts = [draw_shape(ax, M @ GROUND, [[0, 1, 2, 3]], "#bfe3a5", edge="none", zorder=1)]
    for V, faces, col in house():
        pts.append(draw_shape(ax, M @ V, faces, col, zorder=2))
    finish(ax, pts + list(extra), title, view)


def task8():
    c_h = np.array([-9.0, -13.0, 9.0])
    Tc_h, Rc_h = look_at(c_h, [0.5, 0, 1.5], [0, 0, 1])
    C_h = Tc_h @ Rc_h
    Ci_h = np.linalg.inv(C_h)
    P_h = perspective_fov(60, 1.0, 5, 40)
    # проверка: домик попадает в куб видимости
    allv = np.hstack([Ci_h @ V for V, _, _ in house()] + [Ci_h @ GROUND])
    ndc = to_cart(P_h @ allv)
    assert allv[2].min() > 5 and allv[2].max() < 40 and np.abs(ndc).max() <= 1.0, "домик вне frustum"
    print("OK   домик внутри frustum (max |ndc| = %.3f)" % np.abs(ndc).max())

    fig, axes = new_fig(3, 5.4)
    draw_house(axes[0], I4, "Мировые координаты", dict(elev=25, azim=-50))
    draw_house(axes[1], Ci_h, "Параллельная камера (C$^{-1}$)", VIEW_BELOW)
    pc = ndc_cube(axes[2])
    draw_house(axes[2], P_h @ Ci_h, "Перспектива (P·C$^{-1}$)", VIEW_BELOW, extra=[pc])
    save(fig, "t8_house")
    return C_h, P_h


# ====================================================================
# Экспорт матриц для отчёта
# ====================================================================
def fnum(x, p=4):
    s = f"{x:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def tex_mat(M, p=4):
    rows = r" \\ ".join(" & ".join(fnum(x, p) for x in row) for row in M)
    return r"\begin{pmatrix}" + rows + r"\end{pmatrix}"


def tex_vec(v, p=3):
    return r"\begin{pmatrix}" + r" \\ ".join(fnum(x, p) for x in v) + r"\end{pmatrix}"


def export_matrices(C_h, P_h):
    ax21, a21 = axis_angle(R21)
    ax12, a12 = axis_angle(R12)
    ndc = to_cart(P @ np.hstack([Cinv @ V for V, _, _ in scene]))
    z_cam = np.hstack([Cinv @ V for V, _, _ in scene])[2]
    defs = {
        "MatSa": tex_mat(S1), "MatSb": tex_mat(S2), "MatSab": tex_mat(S12),
        "MatTa": tex_mat(T1), "MatTb": tex_mat(T2), "MatTab": tex_mat(T12),
        "MatTS": tex_mat(TS), "MatST": tex_mat(ST),
        "MatJa": tex_mat(J_matrix(v1)[:3, :3], 4), "MatRa": tex_mat(R1), "MatRb": tex_mat(R2),
        "MatRba": tex_mat(R21), "MatRab": tex_mat(R12),
        "AxisBA": tex_vec(ax21), "AxisAB": tex_vec(ax12),
        "AngleBA": fnum(np.degrees(a21), 2), "AngleAB": fnum(np.degrees(a12), 2),
        "MatRvertex": tex_mat(R_vertex),
        "MatRc": tex_mat(Rc, 4), "MatTc": tex_mat(Tc, 3), "MatC": tex_mat(C, 4), "MatCinv": tex_mat(Cinv, 4),
        "CamPos": tex_vec(cam_pos, 3),
        "MatP": tex_mat(P, 4),
        "ZRange": f"{fnum(z_cam.min(), 2)}\\ldots {fnum(z_cam.max(), 2)}",
        "NDCmax": fnum(np.abs(ndc).max(), 3),
        "MatCh": tex_mat(C_h, 3), "MatPh": tex_mat(P_h, 3),
    }
    lines = ["% Файл создаётся автоматически программой prog/main.py — не править вручную"]
    for k, v in defs.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    (REPORT / "matrices.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved:", REPORT / "matrices.tex")


def main():
    run_checks()
    print()
    task1(); task2(); task3(); task4(); task5(); task6(); task7()
    C_h, P_h = task8()
    export_matrices(C_h, P_h)
    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    print("\nR1 =\n", R1, "\nR2 =\n", R2, "\nR_vertex =\n", R_vertex, "\nC =\n", C, "\nCinv =\n", Cinv, "\nP =\n", P)
    print("\nAll graphics saved to", GRAPHICS)


if __name__ == "__main__":
    main()
