#!/usr/bin/env python3
"""Реализация метода k-ближайших соседей (k-NN) без сторонних библиотек,
кроме NumPy и Pandas, на датасете о вине.

Этапы:
1. Загрузка данных и описательная статистика.
2. Предобработка: проверка пропусков, кодирование категориальных признаков,
   масштабирование (стандартизация).
3. Разделение на обучающую и тестовую выборки (80/20, fixed seed).
4. Реализация k-NN на NumPy (евклидово расстояние, голосование по Classes).
5. Две модели: M1 — случайный набор признаков; M2 — фиксированный набор.
6. Оценка при k = 3, 5, 10, 15; матрицы ошибок.
7. Сохранение статистики и данных для графиков в data/ и graphics/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (регистрация 3D projection)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GRAPHICS_DIR = os.path.join(PROJECT_ROOT, "graphics")
CSV_PATH = os.path.join(DATA_DIR, "WineDataset.csv")
STAT_PATH = os.path.join(DATA_DIR, "statistics.csv")

RANDOM_STATE = 42
TEST_SIZE = 0.2
K_VALUES = [3, 5, 10, 15]
N_FEATURES_MODEL1 = 5  # размер случайного набора признаков для Модели 1
FIXED_FEATURES_MODEL2 = [  # фиксированный набор признаков для Модели 2
    "Alcohol", "Malic Acid", "Ash", "Alcalinity of ash",
    "Magnesium", "Total phenols",
]


def load_data(path):
    df = pd.read_csv(path)
    return df


def descriptive_statistics(df, feature_cols):
    stats = df[feature_cols].describe(
        percentiles=[0.25, 0.5, 0.75]
    ).transpose()
    stats = stats[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    stats.columns = ["count", "mean", "std", "min", "q25", "q50", "q75", "max"]
    return stats


def preprocess(df, feature_cols, target_col):
    """Проверка пропусков, кодирование категориальных признаков, стандартизация."""
    df = df.copy()
    report = {}

    # 1. Проверка пропусков
    missing = df[feature_cols].isnull().sum().sum()
    report["missing_values"] = int(missing)

    # 2. Кодирование категориальных признаков (если есть)
    categorical_cols = []
    for col in feature_cols:
        if df[col].dtype == object or str(df[col].dtype) == "category":
            categorical_cols.append(col)
            df[col] = pd.factorize(df[col])[0]
    report["categorical_columns"] = categorical_cols
    report["categorical_encoded"] = len(categorical_cols) > 0

    # 3. Масштабирование: стандартизация признаков (целевую не масштабируем)
    means = df[feature_cols].mean()
    stds = df[feature_cols].std()
    stds = stds.replace(0, 1.0)  # защита от деления на ноль
    X = ((df[feature_cols] - means) / stds).values
    y = df[target_col].values

    return X, y, means, stds, report


def train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE):
    rng = np.random.RandomState(random_state)
    n = X.shape[0]
    indices = rng.permutation(n)
    n_test = int(round(n * test_size))
    test_idx = indices[:n_test]
    train_idx = indices[n_test:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx], train_idx, test_idx


class KNNClassifier:
    """k-ближайших соседей, реализация на NumPy (евклидово расстояние)."""

    def __init__(self, k=3):
        self.k = k
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        self.X_train = np.asarray(X, dtype=float)
        self.y_train = np.asarray(y)

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        # парные евклидовые расстояния через матричную формулу
        # ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a·b
        a2 = np.sum(X ** 2, axis=1, keepdims=True)
        b2 = np.sum(self.X_train ** 2, axis=1, keepdims=True).T
        ab = X @ self.X_train.T
        dists = np.sqrt(np.maximum(a2 + b2 - 2 * ab, 0.0))
        k_nearest = np.argsort(dists, axis=1)[:, : self.k]
        k_labels = self.y_train[k_nearest]
        # голосование: наиболее вероятный класс среди k соседей
        predictions = np.array([
            np.bincount(row.astype(int)).argmax() for row in k_labels
        ])
        return predictions


def confusion_matrix(y_true, y_pred, classes):
    n = len(classes)
    cm = np.zeros((n, n), dtype=int)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    for t, p in zip(y_true, y_pred):
        cm[class_to_idx[t], class_to_idx[p]] += 1
    return cm


def accuracy(y_true, y_pred):
    return float(np.mean(y_true == y_pred))


def plot_statistics(df, feature_cols, stats):
    """Графики описательной статистики: гистограммы признаков и средние."""
    os.makedirs(GRAPHICS_DIR, exist_ok=True)

    n = len(feature_cols)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(14, 3 * rows))
    axes = np.atleast_2d(axes)
    for i, col in enumerate(feature_cols):
        r, c = divmod(i, cols)
        axes[r, c].hist(df[col].dropna(), bins=20, color="#4C78A8", edgecolor="white")
        axes[r, c].set_title(col, fontsize=9)
        axes[r, c].tick_params(labelsize=7)
    for i in range(n, rows * cols):
        r, c = divmod(i, cols)
        axes[r, c].axis("off")
    fig.suptitle("Распределение признаков датасета о вине", fontsize=11)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(os.path.join(GRAPHICS_DIR, "feature_histograms.pdf"))
    plt.close(fig)

    # средние значения признаков (бар-чарт)
    fig, ax = plt.subplots(figsize=(10, 4))
    means = stats["mean"]
    ax.bar(range(len(means)), means.values, color="#4C78A8", edgecolor="white")
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Среднее значение")
    ax.set_title("Средние значения признаков")
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPHICS_DIR, "feature_means.pdf"))
    plt.close(fig)


def plot_3d(df, feature_cols):
    """3D-визуализация первых трёх признаков, окрашенная по классам."""
    os.makedirs(GRAPHICS_DIR, exist_ok=True)
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    c1, c2, c3 = feature_cols[:3]
    for cls in sorted(df["Wine"].unique()):
        mask = df["Wine"] == cls
        ax.scatter(df.loc[mask, c1], df.loc[mask, c2], df.loc[mask, c3],
                   label=f"Класс {cls}", s=30, alpha=0.7)
    ax.set_xlabel(c1)
    ax.set_ylabel(c2)
    ax.set_zlabel(c3)
    ax.set_title("3D-визуализация признаков (первые три)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPHICS_DIR, "visualization_3d.pdf"))
    plt.close(fig)


def plot_confusion_matrix(cm, classes, title, path):
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set(xticks=np.arange(len(classes)), yticks=np.arange(len(classes)),
           xticklabels=classes, yticklabels=classes,
           ylabel="Истинный класс", xlabel="Предсказанный класс",
           title=title)
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontsize=10)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    df = load_data(CSV_PATH)
    print(f"Записей: {len(df)}, признаков: {df.shape[1]}")

    target_col = "Wine"
    feature_cols = [c for c in df.columns if c != target_col]
    print(f"Признаки ({len(feature_cols)}): {feature_cols}")
    print(f"Классы: {sorted(df[target_col].unique())}")

    # описательная статистика
    stats = descriptive_statistics(df, feature_cols)
    stats.to_csv(STAT_PATH)
    print("\nОписательная статистика сохранена в", STAT_PATH)
    print(stats.round(3).to_string())

    # предобработка
    X, y, means, stds, prep_report = preprocess(df, feature_cols, target_col)
    print("\nПредобработка:")
    print(f"  Пропущенных значений: {prep_report['missing_values']}")
    print(f"  Категориальных признаков: {prep_report['categorical_columns']}")

    # разделение
    X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(X, y)
    print(f"  Обучающая выборка: {X_train.shape[0]}, тестовая: {X_test.shape[0]}")

    classes = sorted(df[target_col].unique())

    # графики статистики и 3D-визуализация (по исходным, не масштабированным данным)
    plot_statistics(df, feature_cols, stats)
    plot_3d(df, feature_cols)
    print("Графики статистики и 3D-визуализация сохранены в", GRAPHICS_DIR)

    # ---- Модель 1: случайный набор признаков ----
    rng = np.random.RandomState(RANDOM_STATE)
    rand_features = rng.choice(feature_cols, size=N_FEATURES_MODEL1, replace=False)
    rand_features = sorted(rand_features.tolist())
    print(f"\nМодель 1 (случайные признаки): {rand_features}")

    idx1 = [feature_cols.index(f) for f in rand_features]
    X_tr1, X_te1 = X_train[:, idx1], X_test[:, idx1]
    results1 = []
    for k in K_VALUES:
        clf = KNNClassifier(k=k)
        clf.fit(X_tr1, y_train)
        y_pred = clf.predict(X_te1)
        acc = accuracy(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred, classes)
        results1.append((k, acc, cm))
        print(f"  k={k}: accuracy={acc:.4f}")
        print(f"  матрица ошибок:\n{cm}")

    # ---- Модель 2: фиксированный набор признаков ----
    print(f"\nМодель 2 (фиксированные признаки): {FIXED_FEATURES_MODEL2}")
    idx2 = [feature_cols.index(f) for f in FIXED_FEATURES_MODEL2]
    X_tr2, X_te2 = X_train[:, idx2], X_test[:, idx2]
    results2 = []
    for k in K_VALUES:
        clf = KNNClassifier(k=k)
        clf.fit(X_tr2, y_train)
        y_pred = clf.predict(X_te2)
        acc = accuracy(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred, classes)
        results2.append((k, acc, cm))
        print(f"  k={k}: accuracy={acc:.4f}")
        print(f"  матрица ошибок:\n{cm}")

    # матрицы ошибок для наилучшего k по каждой модели (k=10 для примера, можно выбрать лучшее)
    best_k1 = max(results1, key=lambda t: t[1])[0]
    best_k2 = max(results2, key=lambda t: t[1])[0]
    cm1 = dict((k, cm) for k, _, cm in results1)[best_k1]
    cm2 = dict((k, cm) for k, _, cm in results2)[best_k2]
    plot_confusion_matrix(cm1, classes,
                          f"Модель 1 (случайные признаки), k={best_k1}",
                          os.path.join(GRAPHICS_DIR, "confusion_model1.pdf"))
    plot_confusion_matrix(cm2, classes,
                          f"Модель 2 (фиксированные признаки), k={best_k2}",
                          os.path.join(GRAPHICS_DIR, "confusion_model2.pdf"))
    print(f"\nМатрицы ошибок (k={best_k1}, k={best_k2}) сохранены в {GRAPHICS_DIR}")

    # сохранить сводку метрик
    summary = {
        "model": [], "k": [], "accuracy": []
    }
    for k, acc, _ in results1:
        summary["model"].append("M1_random"); summary["k"].append(k); summary["accuracy"].append(round(acc, 4))
    for k, acc, _ in results2:
        summary["model"].append("M2_fixed"); summary["k"].append(k); summary["accuracy"].append(round(acc, 4))
    pd.DataFrame(summary).to_csv(os.path.join(DATA_DIR, "metrics_summary.csv"), index=False)
    print("Сводка метрик сохранена в data/metrics_summary.csv")


if __name__ == "__main__":
    main()
