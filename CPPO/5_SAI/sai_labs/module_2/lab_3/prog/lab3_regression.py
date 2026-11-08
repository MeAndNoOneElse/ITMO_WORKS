#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Линейная регрессия МНК на датасете жилья Калифорнии (лабораторная работа 3).

Реализация без сторонних библиотек кроме NumPy/Pandas:
загрузка данных, статистика, предобработка, деление на выборки,
три модели МНК, коэффициент детерминации R^2, графики.
"""

import os
import csv

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # неинтерактивный бэкенд (рисуем в файл, не показываем окно)
import matplotlib.pyplot as plt  # noqa: E402

# Пути к файлам (относительно корня проекта, где лежит этот скрипт)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(BASE, "data", "california_housing_train.csv")
STAT_CSV = os.path.join(BASE, "data", "statistics.csv")
GRAPHICS = os.path.join(BASE, "graphics")
DAT_DIR = os.path.join(BASE, "prog", "dat")
os.makedirs(GRAPHICS, exist_ok=True)
os.makedirs(DAT_DIR, exist_ok=True)

TARGET = "median_house_value"       # целевая переменная (медианная стоимость дома)
TEST_SIZE = 0.2                     # доля тестовой выборки (20 %)
RANDOM_STATE = 42                   # зерно генератора случайных чисел для воспроизводимости


def load_data(path):
    """Загружает датасет из CSV-файла в DataFrame pandas."""
    df = pd.read_csv(path)
    return df


def describe(df):
    """Считает описательную статистику: count, mean, std, min, квантили, max."""
    stats = df.describe(include="all").loc[
        ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    ]
    stats.to_csv(STAT_CSV)  # сохраняем статистику в CSV для отчёта
    return stats


def preprocess(df):
    """
    Предобработка данных:
    1. Проверка пропущенных значений.
    2. Кодирование категориальных признаков (в исходном датасете их нет — все числовые).
    3. Нормировка (стандартизация) числовых признаков: (x - mean) / std.
    Целевая переменная не нормируется.
    """
    report = {}
    report["missing_total"] = int(df.isna().sum().sum())           # всего пропусков во всей таблице
    report["missing_by_col"] = df.isna().sum().to_dict()           # пропусков по каждому столбцу

    # Категориальных признаков в исходном датасете нет (все столбцы числовые).
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    report["categorical_cols"] = categorical_cols
    report["categorical_encoded"] = []
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        report["categorical_encoded"] = categorical_cols

    # Нормировка признаков (standardization), целевая не нормируется.
    feature_cols = [c for c in df.columns if c != TARGET]
    means = df[feature_cols].mean()
    stds = df[feature_cols].std().replace(0, 1.0)                   # защита от деления на ноль
    df[feature_cols] = (df[feature_cols] - means) / stds
    report["feature_means"] = means.to_dict()
    report["feature_stds"] = stds.to_dict()
    return df, report


def train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE):
    """Перемешивает данные и делит на обучающую (80 %) и тестовую (20 %) выборки."""
    df_shuffled = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    n_test = int(round(len(df_shuffled) * test_size))
    test = df_shuffled.iloc[:n_test]
    train = df_shuffled.iloc[n_test:]
    return train, test


def ols_fit(X, y):
    """
    Метод наименьших квадратов (МНК): B = (X^T X)^{-1} X^T y.
    Первый столбец X должен быть добавлен отдельно (единицы для свободного члена)
    — это делается внутри через np.column_stack.
    """
    X_aug = np.column_stack([np.ones(len(X)), X])   # добавляем столбец единиц (свободный член)
    XtX = X_aug.T @ X_aug                            # матрица X^T X
    XtX_inv = np.linalg.inv(XtX)                     # обратная матрица (X^T X)^{-1}
    B = XtX_inv @ X_aug.T @ y                        # вектор коэффициентов B
    return B


def ols_predict(X, B):
    """Предсказание значений y по найденным коэффициентам B."""
    X_aug = np.column_stack([np.ones(len(X)), X])
    return X_aug @ B


def r2_score(y_true, y_pred):
    """
    Коэффициент детерминации R^2 = 1 - SS_res / SS_tot.
    Показывает, какую долю дисперсии целевой переменной объясняет модель.
    """
    ss_res = float(np.sum((y_true - y_pred) ** 2))   # сумма квадратов остатков
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))  # общая сумма квадратов отклонений
    return 1.0 - ss_res / ss_tot if ss_tot != 0 else float("nan")


def xy_arrays(df, feature_cols):
    """Преобразует выбранные признаки и целевую переменную в массивы NumPy."""
    X = df[feature_cols].to_numpy(dtype=float)
    y = df[TARGET].to_numpy(dtype=float)
    return X, y


def save_dat(name, x, y, xlabel, ylabel):
    """Сохраняет пары x,y в текстовый файл .dat для построения графиков."""
    path = os.path.join(DAT_DIR, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([xlabel, ylabel])
        for xi, yi in zip(x, y):
            w.writerow([f"{xi:.10g}", f"{yi:.10g}"])
    return path


def plot_hist(values, out_path, title, xlabel, ylabel):
    """Рисует гистограмму распределения и сохраняет в PDF."""
    plt.figure(figsize=(6, 4))
    plt.hist(values, bins=40, color="#4C78A8", edgecolor="black", alpha=0.85)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_scatter(x, y, out_path, title, xlabel, ylabel):
    """Рисует диаграмму рассеяния и сохраняет в PDF."""
    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, s=8, alpha=0.5, color="#4C78A8", edgecolors="none")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_actual_vs_predicted(y_true, y_pred, out_path, title, r2):
    """
    Рисет диаграмму 'фактические против предсказанных' значений.
    Красная диагональ — идеальное совпадение (y = x).
    """
    plt.figure(figsize=(6, 4))
    plt.scatter(y_true, y_pred, s=8, alpha=0.6, color="#E45756", edgecolors="none")
    lo = min(float(np.min(y_true)), float(np.min(y_pred)))
    hi = max(float(np.max(y_true)), float(np.max(y_pred)))
    plt.plot([lo, hi], [lo, hi], color="black", linestyle="--", linewidth=1, label="идеал")
    plt.title(f"{title}  (R^2 = {r2:.4f})")
    plt.xlabel("фактическая стоимость, тыс. долл.")
    plt.ylabel("предсказанная стоимость, тыс. долл.")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    # 1. Загрузка исходных данных
    df = load_data(DATA_CSV)
    print("Загружено строк:", len(df), "столбцов:", list(df.columns))

    # 2. Описательная статистика (сохраняется в data/statistics.csv)
    stats = describe(df)
    print("\nСтатистика по датасету:\n", stats)

    # 3. Предобработка (пропуски, категориальные, нормировка)
    df_prep, prep_report = preprocess(df.copy())
    print("\nОтчёт предобработки:", prep_report)

    # 4. Деление на обучающую и тестовую выборки (80/20)
    train, test = train_test_split(df_prep)
    print(f"\nРазделение: train={len(train)}, test={len(test)}")

    # 5. Три модели с разными наборами признаков + бонусный синтетический признак
    feature_sets = {
        "Модель 1": ["median_income"],
        "Модель 2": ["median_income", "housing_median_age"],
        "Модель 3": ["median_income", "total_rooms", "households", "rooms_per_household"],
    }

    # Бонус: создаём синтетический признак rooms_per_household = total_rooms / households
    for part in (train, test):
        part["rooms_per_household"] = part["total_rooms"] / part["households"]

    results = {}
    for name, feats in feature_sets.items():
        X_tr, y_tr = xy_arrays(train, feats)
        X_te, y_te = xy_arrays(test, feats)

        # Подбор коэффициентов МНК на обучении
        B = ols_fit(X_tr, y_tr)
        # Предсказание на тесте
        y_pred = ols_predict(X_te, B)
        # Качество модели — R^2 на тесте
        r2 = r2_score(y_te, y_pred)

        results[name] = {"features": feats, "coef": B, "r2": r2,
                         "y_true": y_te, "y_pred": y_pred}
        print(f"\n{name}: признаки={feats}")
        print(f"  коэффициенты (свободный член + признаки): {np.round(B, 6)}")
        print(f"  R^2 на тесте = {r2:.6f}")

    # 6. Сохранение графиков и исходных данных для них
    y_all = df[TARGET].to_numpy(dtype=float)

    # Гистограмма целевой переменной
    save_dat("target_hist.dat", y_all, np.zeros_like(y_all),
             "median_house_value (тыс. долл.)", "частота")
    plot_hist(y_all, os.path.join(GRAPHICS, "target_hist.pdf"),
              "Распределение стоимости жилья", "median_house_value (тыс. долл.)", "Частота")

    # Диаграмма рассеяния цена vs доход
    income = df["median_income"].to_numpy(dtype=float)
    save_dat("price_vs_income.dat", income, y_all,
             "median_income", "median_house_value")
    plot_scatter(income, y_all, os.path.join(GRAPHICS, "price_vs_income.pdf"),
                 "Цена жилья vs доход населения",
                 "median_income (ед. дохода)", "median_house_value (тыс. долл.)")

    # Графики фактические vs предсказанные для каждой модели
    for name, res in results.items():
        safe = name.split()[1]
        save_dat(f"pred_{safe}.dat", res["y_true"], res["y_pred"],
                 "y_true", "y_pred")
        plot_actual_vs_predicted(res["y_true"], res["y_pred"],
                                 os.path.join(GRAPHICS, f"pred_{safe}.pdf"),
                                 f"Предсказания {name}", res["r2"])

    # 7. Сводка результатов в CSV (для таблицы в отчёте)
    summary_path = os.path.join(DAT_DIR, "summary.csv")
    with open(summary_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["модель", "признаки", "R^2"])
        for name, res in results.items():
            w.writerow([name, "; ".join(res["features"]), f"{res['r2']:.6f}"])
    print("\nГрафики и данные сохранены в", GRAPHICS, "и", DAT_DIR)


if __name__ == "__main__":
    main()
