#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Построение графика зависимости квадрата периода колебаний T² от квадрата расстояния до грузов l².
Только маркеры (без соединяющих прямых). В консоль дополнительно выводится уравнение
прямой наилучшего соответствия (линии регрессии) в человекочитаемом виде.
Сохранение результата в файл 'T2_vs_l2_points_with_eq.png'.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Попытка установить желаемый стиль; при ошибке используем запасной встроенный стиль
try:
    plt.style.use('seaborn-whitegrid')
except Exception:
    try:
        plt.style.use('ggplot')
    except Exception:
        plt.style.use('default')

# по 2 таблице
x_l2 = np.array([0.000, 0.0036, 0.0064, 0.0100, 0.0144, 0.0196, 0.0256])
y_T2 = np.array([6.40, 8.68, 11.58, 14.35, 16.37, 21.96, 23.47])
# по 3 таблице
# x_l2 = np.array([0.0000, 0.0009, 0.0036, 0.0081, 0.0144])
# y_T2 = np.array([6.81,   9.79,   9.79,   12.23,  17.86])

# --- Аппроксимация прямой методом наименьших квадратов ---
coeffs, cov = np.polyfit(x_l2, y_T2, 1, cov=True)
a = coeffs[0]
b = coeffs[1]
sigma_a = np.sqrt(cov[0, 0])
sigma_b = np.sqrt(cov[1, 1])

# Предсказанные значения и статистики
y_pred = a * x_l2 + b
ss_res = np.sum((y_T2 - y_pred) ** 2)
ss_tot = np.sum((y_T2 - np.mean(y_T2)) ** 2)
r_squared = 1 - ss_res / ss_tot

# --- Рисование ---
fig, ax = plt.subplots(figsize=(10, 6.5))

# Только маркеры (без линий)
ax.plot(x_l2, y_T2, linestyle='None', marker='o',
        color='black', markerfacecolor='black',
        markeredgecolor='black', markersize=6,
        label='Эмпирические значения')

# Линия аппроксимации (для визуализации среднего тренда оставляем линию)
x_fit = np.linspace(0, x_l2.max() * 1.05, 300)
y_fit = a * x_fit + b
ax.plot(x_fit, y_fit, color='red', linewidth=2, label='Линия аппроксимации')

# Текстовая рамка с коэффициентами (используем символ ²)
legend_text = (f'Аппроксимация: T² = a·l² + b\n'
               f'a = {a:.4f} ± {sigma_a:.4f}  (с²/м²)\n'
               f'b = {b:.3f} ± {sigma_b:.3f}  (с²)\n'
               f'R² = {r_squared:.4f}')
bbox_props = dict(boxstyle="round,pad=0.6", fc="white", ec="black", lw=1)
ax.text(0.02, 0.95, legend_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=bbox_props)

# Подписи и оформление с символом ²
ax.set_title('График 1. Зависимость квадрата периода колебаний\nот квадрата расстояния до грузов.', fontsize=18, fontweight='bold')
ax.set_xlabel('Квадрат расстояния до грузов l², м²', fontsize=14)
ax.set_ylabel('Квадрат периода колебаний T², с²', fontsize=14)
# ax.set_title('График 2. Зависимость квадрата периода колебаний\n'
#              'от квадрата смещения оси вращения диска от оси симметрии.',
#              fontsize=18, fontweight='bold', pad=12)
# ax.set_xlabel('Квадрат смещения диска l², м²', fontsize=14)
# ax.set_ylabel('Квадрат периода колебаний T², с²', fontsize=14)

# Форматирование оси x для читаемости маленьких значений
def fmt_x(x, pos):
    return f'{x:.3f}'
ax.xaxis.set_major_formatter(FuncFormatter(fmt_x))

ax.tick_params(axis='both', which='major', labelsize=12)
ax.set_xlim(left=0)
ax.set_ylim(bottom=min(y_T2) - 1, top=max(y_T2) + 2)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

plt.tight_layout()
out_fname = 'T2_vs_l2_points_with_eq.png'
plt.savefig(out_fname, dpi=300, bbox_inches='tight')
print('Сохранён файл:', out_fname)
plt.show()

# --- Вывод в консоль ---
print('\nКоэффициенты аппроксимации (линейная регрессия):')
print(f' a = {a:.6f} ± {sigma_a:.6f}  (с²/м²)')
print(f' b = {b:.6f} ± {sigma_b:.6f}  (с²)')
print(f' R² = {r_squared:.6f}')

# --- Дополнительный вывод: уравнение прямой, усредняющей точки ---
# Выводим уравнение в удобочитаемом формате, с округлением для компактности:
print('\nУравнение прямой наилучшего соответствия (линия регрессии):')
print(f' T² = {a:.4f} · l² + {b:.3f}    (единицы: с² и м²)')
# Также вывод с учётом погрешностей коэффициентов:
print(f' С учётом погрешностей: T² = ({a:.4f} ± {sigma_a:.4f}) · l² + ({b:.3f} ± {sigma_b:.3f})')