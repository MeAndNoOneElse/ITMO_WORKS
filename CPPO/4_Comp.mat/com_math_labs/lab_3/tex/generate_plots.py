#!/usr/bin/env python3
"""Генерация графиков для отчёта"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Безголовый бэкенд
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

# Установка шрифта для русского текста
rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def f(x):
    """Вариант 2: f(x) = -3x³ - 5x² + 4x - 2"""
    return -3*x**3 - 5*x**2 + 4*x - 2

# ─────────────────────────────────────────────────────────
# График 1: Общий вид функции
# ─────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(-3.5, -0.5, 1000)
y = f(x)

ax.plot(x, y, 'b-', linewidth=2.5, label='$f(x) = -3x^3 - 5x^2 + 4x - 2$')
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)

# Отметить пределы интегрирования
ax.fill_between(x, 0, y, alpha=0.2, color='green', label='Интегрируемая область')
ax.axvline(x=-3, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='a = -3')
ax.axvline(x=-1, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='b = -1')

ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('f(x)', fontsize=12)
ax.set_title('График функции и область интегрирования', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.set_xlim(-3.5, -0.5)

plt.tight_layout()
plt.savefig('plot_function.png', dpi=300, bbox_inches='tight')
print("✓ Сохранён график: plot_function.png")
plt.close()

# ─────────────────────────────────────────────────────────
# График 2: Метод средних прямоугольников (n=6)
# ─────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(11, 6))

a, b = -3, -1
n = 6
h = (b - a) / n
x_nodes = np.array([a + i*h for i in range(n + 1)])
y_nodes = f(x_nodes)

# Нарисовать функцию
x = np.linspace(a, b, 1000)
y = f(x)
ax.plot(x, y, 'b-', linewidth=2.5, label='$f(x)$')

# Нарисовать прямоугольники средних точек
for i in range(n):
    x_mid = a + (i + 0.5) * h
    y_mid = f(x_mid)
    
    ax.add_patch(mpatches.Rectangle(
        (a + i*h, 0), h, y_mid,
        fill=True, facecolor='lightgreen', edgecolor='darkgreen',
        linewidth=1.5, alpha=0.6
    ))
    
    # Точка в середине
    ax.plot(x_mid, y_mid, 'go', markersize=8)

# Узлы
ax.plot(x_nodes, y_nodes, 'ro', markersize=8, label='Узлы квадратуры')

ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('f(x)', fontsize=12)
ax.set_title('Метод средних прямоугольников (n=6)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig('plot_middle_rect.png', dpi=300, bbox_inches='tight')
print("✓ Сохранён график: plot_middle_rect.png")
plt.close()

# ─────────────────────────────────────────────────────────
# График 3: Метод трапеций (n=6)
# ─────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(11, 6))

a, b = -3, -1
n = 6
h = (b - a) / n
x_nodes = np.array([a + i*h for i in range(n + 1)])
y_nodes = f(x_nodes)

# Нарисовать функцию
x = np.linspace(a, b, 1000)
y = f(x)
ax.plot(x, y, 'b-', linewidth=2.5, label='$f(x)$')

# Нарисовать трапеции
for i in range(n):
    x_left = a + i*h
    x_right = a + (i+1)*h
    y_left = f(x_left)
    y_right = f(x_right)
    
    # Трапеция
    vertices = np.array([
        [x_left, 0],
        [x_left, y_left],
        [x_right, y_right],
        [x_right, 0]
    ])
    
    ax.add_patch(mpatches.Polygon(
        vertices,
        fill=True, facecolor='lightyellow', edgecolor='orange',
        linewidth=1.5, alpha=0.6
    ))

# Узлы
ax.plot(x_nodes, y_nodes, 'ro', markersize=8, label='Узлы квадратуры')
# Соединить узлы линиями (верх трапеций)
ax.plot(x_nodes, y_nodes, 'r-', linewidth=1.5, alpha=0.5)

ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('f(x)', fontsize=12)
ax.set_title('Метод трапеций (n=6)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig('plot_trapezoid.png', dpi=300, bbox_inches='tight')
print("✓ Сохранён график: plot_trapezoid.png")
plt.close()

# ─────────────────────────────────────────────────────────
# График 4: Метод Симпсона (n=6)
# ─────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(11, 6))

a, b = -3, -1
n = 6
h = (b - a) / n
x_nodes = np.array([a + i*h for i in range(n + 1)])
y_nodes = f(x_nodes)

# Нарисовать функцию
x = np.linspace(a, b, 1000)
y = f(x)
ax.plot(x, y, 'b-', linewidth=2.5, label='$f(x)$', zorder=3)

# Нарисовать параболы для Симпсона
colors = ['lightblue', 'lightcyan', 'lightblue']
for i in range(0, n, 2):
    x_left = a + i*h
    x_right = a + (i+2)*h
    x_mid = a + (i+1)*h
    
    # Три точки для параболы
    x_parab = np.linspace(x_left, x_right, 100)
    
    # Парабола через три точки
    y_left = f(x_left)
    y_mid = f(x_mid)
    y_right = f(x_right)
    
    # Интерполяция парабола Лагранжа
    y_parab = (y_left * (x_parab - x_mid) * (x_parab - x_right) / ((x_left - x_mid) * (x_left - x_right)) +
               y_mid * (x_parab - x_left) * (x_parab - x_right) / ((x_mid - x_left) * (x_mid - x_right)) +
               y_right * (x_parab - x_left) * (x_parab - x_mid) / ((x_right - x_left) * (x_right - x_mid)))
    
    # Заполнить область под параболой
    ax.fill_between(x_parab, 0, y_parab, alpha=0.5, color=colors[i//2], edgecolor='navy', linewidth=1)
    # Нарисовать саму параболу
    ax.plot(x_parab, y_parab, 'r-', linewidth=2, alpha=0.7)

# Узлы квадратуры
ax.plot(x_nodes, y_nodes, 'go', markersize=10, label='Узлы квадратуры', zorder=4)

ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('f(x)', fontsize=12)
ax.set_title('Метод Симпсона (параболы, n=6)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig('plot_simpson.png', dpi=300, bbox_inches='tight')
print("✓ Сохранён график: plot_simpson.png")
plt.close()

# ─────────────────────────────────────────────────────────
# График 5: Сравнение методов
# ─────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

a, b = -3, -1
n = 6
h = (b - a) / n
x_nodes = np.array([a + i*h for i in range(n + 1)])
y_nodes = f(x_nodes)
x = np.linspace(a, b, 1000)
y = f(x)

methods = [
    ('Левые прямоугольники', 0, 0),
    ('Правые прямоугольники', 0, 1),
    ('Средние прямоугольники', 1, 0),
    ('Трапеции', 1, 1)
]

for method_name, row, col in methods:
    ax = axes[row, col]
    
    ax.plot(x, y, 'b-', linewidth=2.5)
    
    if method_name == 'Левые прямоугольники':
        for i in range(n):
            x_left = a + i*h
            y_left = f(x_left)
            ax.add_patch(mpatches.Rectangle(
                (x_left, 0), h, y_left,
                fill=True, facecolor='lightcoral', edgecolor='darkred',
                linewidth=1, alpha=0.6
            ))
    
    elif method_name == 'Правые прямоугольники':
        for i in range(n):
            x_right = a + (i+1)*h
            y_right = f(x_right)
            ax.add_patch(mpatches.Rectangle(
                (a + i*h, 0), h, y_right,
                fill=True, facecolor='lightblue', edgecolor='darkblue',
                linewidth=1, alpha=0.6
            ))
    
    elif method_name == 'Средние прямоугольники':
        for i in range(n):
            x_mid = a + (i + 0.5) * h
            y_mid = f(x_mid)
            ax.add_patch(mpatches.Rectangle(
                (a + i*h, 0), h, y_mid,
                fill=True, facecolor='lightgreen', edgecolor='darkgreen',
                linewidth=1, alpha=0.6
            ))
    
    elif method_name == 'Трапеции':
        for i in range(n):
            x_left = a + i*h
            x_right = a + (i+1)*h
            y_left = f(x_left)
            y_right = f(x_right)
            vertices = np.array([
                [x_left, 0], [x_left, y_left],
                [x_right, y_right], [x_right, 0]
            ])
            ax.add_patch(mpatches.Polygon(
                vertices, fill=True, facecolor='lightyellow',
                edgecolor='orange', linewidth=1, alpha=0.6
            ))
    
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x', fontsize=10)
    ax.set_ylabel('f(x)', fontsize=10)
    ax.set_title(method_name, fontsize=11, fontweight='bold')

plt.suptitle('Сравнение методов численного интегрирования (n=6)', 
             fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('plot_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Сохранён график: plot_comparison.png")
plt.close()

print("\n✅ Все графики успешно созданы!")
