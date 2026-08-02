# -*- coding: utf-8 -*-
"""
Расчётно-графическая работа №1
Описание выборки. Оценивание параметров. Доверительные интервалы.

Вариант: А-1
Данные: RGR1_A-1_X1-X4.csv
"""

import numpy as np
import pandas as pd
import matplotlib

# Используем агрегированный бэкенд без GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm, uniform, expon, t, chi2
import os

# Создаем папку для сохранения графиков
if not os.path.exists('plots'):
    os.makedirs('plots')

# Устанавливаем стиль графиков
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# =========================================================
# ЗАГРУЗКА ДАННЫХ И ПЕРВИЧНЫЙ ОБЗОР
# =========================================================
print("=" * 60)
print("ЗАГРУЗКА ДАННЫХ")
print("=" * 60)

# Загружаем данные из CSV файла
file_path = 'RGR1_A-1_X1-X4.csv'
data = pd.read_csv(file_path)
n_samples = len(data)
print(f"Вариант: А-1")
print(f"Объём выборки: n = {n_samples}")
print(f"Столбцы: {list(data.columns)}")
print("\nПервые 5 строк данных:")
print(data.head())

# =========================================================
# ОСНОВНАЯ ЧАСТЬ: АНАЛИЗ X1, X2, X3
# =========================================================
print("\n\n" + "=" * 60)
print("ОСНОВНАЯ ЧАСТЬ: АНАЛИЗ СТОЛБЦОВ X1, X2, X3")
print("=" * 60)


def analyze_column(col_name, col_data):
    """Выполняет полный анализ для одного столбца данных согласно заданию."""
    print(f"\n\n{'=' * 50}")
    print(f"АНАЛИЗ СТОЛБЦА: {col_name}")
    print('=' * 50)

    n = len(col_data)
    x_mean = np.mean(col_data)
    s2_biased = np.var(col_data, ddof=0)  # Смещённая дисперсия S^2
    s2_unbiased = np.var(col_data, ddof=1)  # Несмещённая дисперсия σ̂^2
    s_biased = np.sqrt(s2_biased)
    s_unbiased = np.sqrt(s2_unbiased)
    median = np.median(col_data)
    q1 = np.percentile(col_data, 25)
    q3 = np.percentile(col_data, 75)
    iqr = q3 - q1
    x_min = np.min(col_data)
    x_max = np.max(col_data)

    print(f"\n--- 4.1. Первичное описание выборки ---")
    print(f"Вариационный ряд (первые 5): {np.sort(col_data)[:5]}")
    print(f"Вариационный ряд (последние 5): {np.sort(col_data)[-5:]}")
    print(f"\nЧисловые характеристики:")
    print(f"  Выборочное среднее (x̄): {x_mean:.3f}")
    print(f"  Смещённая дисперсия (S^2): {s2_biased:.3f}")
    print(f"  Несмещённая дисперсия (σ̂^2): {s2_unbiased:.3f}")
    print(f"  Смещённое ст. отклонение (S): {s_biased:.3f}")
    print(f"  Несмещённое ст. отклонение (σ̂): {s_unbiased:.3f}")
    print(f"  Медиана (me): {median:.3f}")
    print(f"  Квартили (Q1, Q3): ({q1:.3f}, {q3:.3f})")
    print(f"  Межквартильный размах (IQR): {iqr:.3f}")
    print(f"  Минимум, Максимум: ({x_min:.3f}, {x_max:.3f})")

    # --- Построение гистограмм ---
    h_scott = 3.5 * s_unbiased * n ** (-1 / 3)
    k_scott = int(np.ceil((x_max - x_min) / h_scott))
    h_fd = 2 * iqr * n ** (-1 / 3)
    k_fd = max(10, int(np.ceil((x_max - x_min) / h_fd)))
    k_sturges = int(1 + np.floor(np.log2(n)))

    print(f"\nВыбор числа интервалов для гистограммы:")
    print(f"  Скотт: h = {h_scott:.2f}, k = {k_scott}")
    print(f"  Фридман-Диаконис: h = {h_fd:.2f}, k = {k_fd}")
    print(f"  Стерджес: k = {k_sturges}")

    # Визуализация и сохранение в файл
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Анализ распределения {col_name}', fontsize=16, fontweight='bold')

    # 1. Гистограмма (Скотт)
    axes[0, 0].hist(col_data, bins=k_scott, edgecolor='black', alpha=0.7, color='skyblue', density=False)
    axes[0, 0].axvline(x_mean, color='red', linestyle='--', linewidth=2, label=f'Среднее = {x_mean:.2f}')
    axes[0, 0].set_title(f'Гистограмма (правило Скотта, k={k_scott})')
    axes[0, 0].set_xlabel('Значения')
    axes[0, 0].set_ylabel('Частота')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Гистограмма (Фридман-Диаконис)
    axes[0, 1].hist(col_data, bins=k_fd, edgecolor='black', alpha=0.7, color='lightgreen', density=False)
    axes[0, 1].axvline(x_mean, color='red', linestyle='--', linewidth=2, label=f'Среднее = {x_mean:.2f}')
    axes[0, 1].set_title(f'Гистограмма (правило Ф-Д, k={k_fd})')
    axes[0, 1].set_xlabel('Значения')
    axes[0, 1].set_ylabel('Частота')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Гистограмма (Стерджес)
    axes[0, 2].hist(col_data, bins=k_sturges, edgecolor='black', alpha=0.7, color='salmon', density=False)
    axes[0, 2].axvline(x_mean, color='red', linestyle='--', linewidth=2, label=f'Среднее = {x_mean:.2f}')
    axes[0, 2].set_title(f'Гистограмма (правило Стерджеса, k={k_sturges})')
    axes[0, 2].set_xlabel('Значения')
    axes[0, 2].set_ylabel('Частота')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)

    # 4. Эмпирическая функция распределения (ЭФР)
    sorted_data = np.sort(col_data)
    y_ecdf = np.arange(1, n + 1) / n
    axes[1, 0].step(sorted_data, y_ecdf, where='post', linewidth=2)
    axes[1, 0].set_title('Эмпирическая функция распределения (ЭФР)')
    axes[1, 0].set_xlabel('x')
    axes[1, 0].set_ylabel('Fₙ(x)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(y=0.5, color='gray', linestyle=':', label=f'Медиана = {median:.2f}')
    axes[1, 0].axvline(median, color='gray', linestyle=':')
    axes[1, 0].legend()

    # 5. Ящик с усами (Boxplot)
    axes[1, 1].boxplot(col_data, vert=False, patch_artist=True)
    axes[1, 1].set_title('Ящик с усами (Boxplot)')
    axes[1, 1].set_xlabel('Значения')
    axes[1, 1].grid(True, alpha=0.3)

    # 6. Полигон частот (на основе гистограммы по Скотту)
    counts, bin_edges = np.histogram(col_data, bins=k_scott)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    axes[1, 2].plot(bin_centers, counts, 'bo-', linewidth=2, markersize=6)
    axes[1, 2].set_title(f'Полигон частот (по интервалам Скотта)')
    axes[1, 2].set_xlabel('Значения')
    axes[1, 2].set_ylabel('Частота')
    axes[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    # Сохраняем график в файл вместо отображения
    plt.savefig(f'plots/analysis_{col_name}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Графики сохранены в файл: plots/analysis_{col_name}.png")

    # --- 4.2. Предположение о виде закона распределения ---
    print(f"\n--- 4.2. Предположение о виде закона распределения ---")
    print("\nНа основе гистограмм, ЭФР и boxplot необходимо выбрать одну из моделей:")
    print("  1. Нормальное распределение (N a,σ)")
    print("  2. Равномерное распределение (U a,b)")
    print("  3. Экспоненциальное распределение со сдвигом (Exp λ,c)")

    # ВАЖНО: Здесь нужно сделать выбор на основе визуального анализа
    # Для X1: Похоже на нормальное распределение (симметричное, колоколообразное)
    # Для X2: Похоже на равномерное или нормальное? Нужно смотреть
    # Для X3: Может быть экспоненциальное с выбросами

    # Для примера сделаем предположения (в отчете заменить на обоснованные!)
    if col_name == 'X1':
        chosen_model = 'normal'  # Симметричное, похоже на нормальное
    elif col_name == 'X2':
        chosen_model = 'normal'  # Возможно нормальное
    elif col_name == 'X3':
        chosen_model = 'exponential'  # Есть большие выбросы, возможно экспоненциальное
    else:
        chosen_model = 'normal'

    print(f"\n>>> ПРЕДПОЛОЖЕНИЕ ДЛЯ {col_name}: {chosen_model}")

    params = {}
    params['model'] = chosen_model
    params['mean'] = x_mean
    params['s2_biased'] = s2_biased
    params['s2_unbiased'] = s2_unbiased
    params['s_biased'] = s_biased
    params['s_unbiased'] = s_unbiased
    params['min'] = x_min
    params['max'] = x_max
    params['n'] = n
    params['col_data'] = col_data
    params['q1'] = q1
    params['q3'] = q3
    params['iqr'] = iqr

    # --- 4.3. Оценивание параметров: ММ и ММП ---
    print(f"\n--- 4.3. Оценивание параметров: Метод моментов (ММ) и Метод максимального правдоподобия (ММП) ---")

    mm_estimates = {}
    mle_estimates = {}

    if chosen_model == 'normal':
        mm_estimates['a'] = x_mean
        mm_estimates['σ^2'] = s2_biased
        mle_estimates['a'] = x_mean
        mle_estimates['σ^2'] = s2_biased
        print(f"  ММ: â = {mm_estimates['a']:.3f}, σ̂²_MM = {mm_estimates['σ^2']:.3f}")
        print(f"  ММП: â = {mle_estimates['a']:.3f}, σ̂²_MLE = {mle_estimates['σ^2']:.3f}")
        print("  Оценки совпадают.")

    elif chosen_model == 'uniform':
        mm_estimates['a'] = x_mean - np.sqrt(3 * s2_biased)
        mm_estimates['b'] = x_mean + np.sqrt(3 * s2_biased)
        mle_estimates['a'] = x_min
        mle_estimates['b'] = x_max
        print(f"  ММ: â = {mm_estimates['a']:.3f}, b̂ = {mm_estimates['b']:.3f}")
        print(f"  ММП: â = {mle_estimates['a']:.3f}, b̂ = {mle_estimates['b']:.3f}")

    elif chosen_model == 'exponential':
        mm_estimates['λ'] = 1.0 / s_biased
        mm_estimates['c'] = x_mean - 1.0 / mm_estimates['λ']
        mle_estimates['c'] = x_min
        mle_estimates['λ'] = 1.0 / (x_mean - mle_estimates['c'])
        print(f"  ММ: λ̂ = {mm_estimates['λ']:.4f}, ĉ = {mm_estimates['c']:.3f}")
        print(f"  ММП: λ̂ = {mle_estimates['λ']:.4f}, ĉ = {mle_estimates['c']:.3f}")

    params['mm'] = mm_estimates
    params['mle'] = mle_estimates

    # --- 4.4. Оценивание параметрической вероятности ---
    print(f"\n--- 4.4. Оценивание вероятности P(X > x0) ---")
    x0 = x_mean + s_unbiased
    print(f"Выбран порог x0 = x̄ + σ̂ = {x_mean:.2f} + {s_unbiased:.2f} = {x0:.2f}")

    emp_prob = np.sum(col_data > x0) / n
    print(f"  Эмпирическая оценка: P(X > x0) = {emp_prob:.4f}")

    theo_prob = 0
    if chosen_model == 'normal':
        theo_prob = 1 - norm.cdf(x0, loc=mle_estimates['a'], scale=np.sqrt(mle_estimates['σ^2']))
    elif chosen_model == 'uniform':
        a_hat, b_hat = mle_estimates['a'], mle_estimates['b']
        if x0 >= b_hat:
            theo_prob = 0
        elif x0 < a_hat:
            theo_prob = 1
        else:
            theo_prob = (b_hat - x0) / (b_hat - a_hat)
    elif chosen_model == 'exponential':
        c_hat, lambda_hat = mle_estimates['c'], mle_estimates['λ']
        theo_prob = np.exp(-lambda_hat * (x0 - c_hat)) if x0 >= c_hat else 1.0

    print(f"  Параметрическая оценка (по ММП): P(X > x0) = {theo_prob:.4f}")

    # --- 4.5. Оценка моментов по сгруппированной выборке ---
    print(f"\n--- 4.5. Оценка моментов по сгруппированной выборке ---")
    counts_g, bin_edges_g = np.histogram(col_data, bins=k_scott)
    bin_centers_g = (bin_edges_g[:-1] + bin_edges_g[1:]) / 2

    x_g = np.sum(counts_g * bin_centers_g) / n
    s2_g = np.sum(counts_g * (bin_centers_g - x_g) ** 2) / (n - 1)

    print(f"  Оценка среднего по сгрупп. данным (x̄_g): {x_g:.3f}")
    print(f"  Оценка дисперсии по сгрупп. данным (σ̂²_g): {s2_g:.3f}")
    print(f"  Сравнение с исходными: x̄ = {x_mean:.3f}, σ̂² = {s2_unbiased:.3f}")

    # --- 4.6. Доверительные интервалы ---
    print(f"\n--- 4.6. Доверительные интервалы (1-α = 0.95) ---")
    alpha = 0.05
    z_crit = norm.ppf(1 - alpha / 2)
    t_crit = t.ppf(1 - alpha / 2, df=n - 1)

    asim_lower = x_mean - z_crit * s_unbiased / np.sqrt(n)
    asim_upper = x_mean + z_crit * s_unbiased / np.sqrt(n)
    print(f"  Асимптотический ДИ для EX: ({asim_lower:.3f}, {asim_upper:.3f})")

    if chosen_model == 'normal':
        exact_mean_lower = x_mean - t_crit * s_unbiased / np.sqrt(n)
        exact_mean_upper = x_mean + t_crit * s_unbiased / np.sqrt(n)
        print(f"  Точный ДИ для a (норм. распр.): ({exact_mean_lower:.3f}, {exact_mean_upper:.3f})")

        chi2_lower = chi2.ppf(alpha / 2, df=n - 1)
        chi2_upper = chi2.ppf(1 - alpha / 2, df=n - 1)
        var_lower = (n - 1) * s2_unbiased / chi2_upper
        var_upper = (n - 1) * s2_unbiased / chi2_lower
        print(f"  Точный ДИ для σ² (норм. распр.): ({var_lower:.3f}, {var_upper:.3f})")

    print("\n  Интерпретация доверительных интервалов:")
    print("  Доверительный интервал — это случайный интервал, построенный по выборке, который с заданной")
    print("  вероятностью (уровнем доверия) накрывает истинное значение параметра.")

    # --- 4.7. Итоговый вывод для столбца ---
    print(f"\n--- 4.7. Итоговый вывод по столбцу {col_name} ---")
    print(f"  Для столбца {col_name} выбрано {chosen_model.upper()} распределение.")
    if chosen_model == 'normal':
        print(f"  Параметры (ММП/ММ): a = {mle_estimates['a']:.3f}, σ² = {mle_estimates['σ^2']:.3f}.")
    elif chosen_model == 'uniform':
        print(f"  Параметры (ММП): a = {mle_estimates['a']:.3f}, b = {mle_estimates['b']:.3f}.")
    elif chosen_model == 'exponential':
        print(f"  Параметры (ММП): c = {mle_estimates['c']:.3f}, λ = {mle_estimates['λ']:.4f}.")

    return params


# Анализируем каждый столбец
results = {}
for col in ['X1', 'X2', 'X3']:
    results[col] = analyze_column(col, data[col].values)

# =========================================================
# БОНУС: АНАЛИЗ X4 (Бимодальность и кластеризация)
# =========================================================
print("\n\n" + "=" * 60)
print("БОНУС: АНАЛИЗ СТОЛБЦА X4 (неоднородность и кластеризация)")
print("=" * 60)

x4 = data['X4'].values
n_x4 = len(x4)

# --- 1. Первичный анализ и гистограмма ---
print("\n--- 1. Описание формы распределения X4 ---")
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.hist(x4, bins=30, edgecolor='black', alpha=0.7, color='purple')
plt.axvline(np.mean(x4), color='red', linestyle='--', linewidth=2, label=f'Среднее = {np.mean(x4):.2f}')
plt.axvline(np.median(x4), color='green', linestyle=':', linewidth=2, label=f'Медиана = {np.median(x4):.2f}')
plt.title('Гистограмма X4')
plt.xlabel('Значения')
plt.ylabel('Частота')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
sorted_x4 = np.sort(x4)
y_ecdf_x4 = np.arange(1, n_x4 + 1) / n_x4
plt.step(sorted_x4, y_ecdf_x4, where='post', linewidth=2)
plt.title('ЭФР X4')
plt.xlabel('x')
plt.ylabel('Fₙ(x)')
plt.grid(True, alpha=0.3)

plt.suptitle('Бонусный анализ X4', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('plots/analysis_X4.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Графики X4 сохранены в файл: plots/analysis_X4.png")

print("\nНа гистограмме X4 наблюдается бимодальность (два пика).")
print("Это указывает на то, что данные являются смесью двух распределений.")

# --- 2. Разделение на кластеры ---
print("\n--- 2. Разделение выборки на два кластера ---")

# Определяем порог разделения по гистограмме
threshold = 70
cluster1 = x4[x4 <= threshold]
cluster2 = x4[x4 > threshold]

print(f"Используем порог = {threshold} для разделения.")
print(f"Кластер 1 (≤{threshold}): размер = {len(cluster1)}")
print(f"Кластер 2 (>{threshold}): размер = {len(cluster2)}")

print("\nСравнение характеристик подвыборок:")
print(f"  Кластер 1: среднее = {np.mean(cluster1):.2f}, дисперсия = {np.var(cluster1, ddof=1):.2f}")
print(f"  Кластер 2: среднее = {np.mean(cluster2):.2f}, дисперсия = {np.var(cluster2, ddof=1):.2f}")

# Визуализация кластеров
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.hist(cluster1, bins=15, alpha=0.7, label='Кластер 1', color='blue', edgecolor='black')
plt.hist(cluster2, bins=15, alpha=0.7, label='Кластер 2', color='orange', edgecolor='black')
plt.axvline(threshold, color='red', linestyle='--', linewidth=2, label=f'Порог = {threshold}')
plt.title('Гистограмма двух кластеров')
plt.xlabel('Значения X4')
plt.ylabel('Частота')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.boxplot([cluster1, cluster2], labels=['Кластер 1', 'Кластер 2'], patch_artist=True)
plt.title('Ящики с усами для кластеров')
plt.ylabel('Значения X4')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/clusters_X4.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Графики кластеров сохранены в файл: plots/clusters_X4.png")

# --- 3. Вывод о несостоятельности общего среднего ---
print("\n--- 3. Почему 'общее среднее' плохо описывает смесь? ---")
print(f"Общее среднее для X4 = {np.mean(x4):.2f}")
print("Это значение попадает в область между двумя пиками и не представляет")
print("ни один из кластеров адекватно.")
print("Для первого кластера среднее около 45, для второго — около 100.")
print("Использование общего среднего вводит в заблуждение, т.к. данные неоднородны.")

print("\n" + "=" * 60)
print("АНАЛИЗ ЗАВЕРШЕН")
print(f"Все графики сохранены в папку: {os.path.abspath('plots')}")
print("=" * 60)