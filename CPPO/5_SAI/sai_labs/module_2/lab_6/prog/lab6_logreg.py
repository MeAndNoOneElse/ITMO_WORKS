# Лабораторная 6. Логистическая регрессия — расчёты на Python (NumPy/Pandas)
# Источник данных: train.csv из папки lab_6/data

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = '/home/eter-core/ITMO_WORKS/CPPO/5_SAI/sai_labs/module_2/lab_6'
DATA_DIR = os.path.join(BASE, 'data')
GRAPHICS_DIR = os.path.join(BASE, 'graphics')
TASK_DATA = os.path.join(BASE, 'data', 'train.csv')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GRAPHICS_DIR, exist_ok=True)

# 1. Загрузка датасета
df = pd.read_csv(TASK_DATA)
print(f"Загружено записей: {len(df)}")
print(f"Столбцы: {list(df.columns)}")

# 2. Разделение на обучающую и тестовую выборки 80/20 ДО любой предобработки
# (чтобы статистики для заполнения пропусков и стандартизации вычислялись только на train)
np.random.seed(42)
y = df['Survived'].values.astype(float)
n = len(df)
idx = np.random.permutation(n)
n_train = int(0.8 * n)
train_idx = idx[:n_train]
test_idx = idx[n_train:]
df_train = df.iloc[train_idx].reset_index(drop=True)
df_test = df.iloc[test_idx].reset_index(drop=True)
print(f"\nОбучающая выборка: {len(df_train)}, тестовая: {len(df_test)}")
print(f"Доля выживших в train: {df_train['Survived'].mean():.3f}, в test: {df_test['Survived'].mean():.3f}")

# 3. Предобработка — статистики считаются только на train, затем применяются к train и test
def preprocess(df_part, train_stats=None, fit=False):
    df_part = df_part.copy()
    # Категориальный признак Embarked: заполнение пропусков и one-hot кодирование
    if fit:
        train_stats = {}
        train_stats['age_median'] = df_part['Age'].median()
        train_stats['fare_median'] = df_part['Fare'].median()
        train_stats['embarked_mode'] = df_part['Embarked'].mode()[0]
    # Числовые пропуски
    df_part['Age'] = df_part['Age'].fillna(train_stats['age_median'])
    df_part['Fare'] = df_part['Fare'].fillna(train_stats['fare_median'])
    df_part['Embarked'] = df_part['Embarked'].fillna(train_stats['embarked_mode'])
    # Категориальные признаки
    df_part['Sex'] = (df_part['Sex'] == 'female').astype(int)
    # One-hot кодирование Embarked (без искусственного порядка 0/1/2)
    embarked_dummies = pd.get_dummies(df_part['Embarked'], prefix='Embarked')
    df_part = pd.concat([df_part, embarked_dummies], axis=1)
    # Стандартизация числовых признаков (параметры из train)
    num_cols = ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare']
    if fit:
        train_stats['num_mean'] = df_part[num_cols].mean().to_dict()
        train_stats['num_std'] = df_part[num_cols].std().to_dict()
        train_stats['num_std'] = {k: (v if v != 0 else 1.0) for k, v in train_stats['num_std'].items()}
    for c in num_cols:
        df_part[c] = (df_part[c] - train_stats['num_mean'][c]) / train_stats['num_std'][c]
    # Исключаем неинформативные для модели признаки
    df_part = df_part.drop(columns=['Cabin', 'Name', 'Ticket', 'PassengerId', 'Embarked'])
    return df_part, train_stats

df_train_proc, train_stats = preprocess(df_train, fit=True)
df_test_proc, _ = preprocess(df_test, train_stats=train_stats, fit=False)

# Матрицы признаков и целевой вектор
feature_cols = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare',
                'Embarked_S', 'Embarked_C', 'Embarked_Q']
X_train = df_train_proc[feature_cols].values.astype(float)
X_test = df_test_proc[feature_cols].values.astype(float)
y_train = df_train['Survived'].values.astype(float).reshape(-1, 1)
y_test = df_test['Survived'].values.astype(float).reshape(-1, 1)

print(f"Число признаков после one-hot: {X_train.shape[1]}")

# 4. Описательная статистика (пункт 3 задания) — explorative, на всех данных после заполнения пропусков train-статистиками
df_all_for_stats = df.copy()
df_all_for_stats['Age'] = df_all_for_stats['Age'].fillna(train_stats['age_median'])
df_all_for_stats['Fare'] = df_all_for_stats['Fare'].fillna(train_stats['fare_median'])
df_all_for_stats['Embarked'] = df_all_for_stats['Embarked'].fillna(train_stats['embarked_mode'])
stats = df_all_for_stats[['Survived', 'Pclass', 'Age', 'SibSp', 'Parch', 'Fare']].describe()
stats_path = os.path.join(DATA_DIR, 'lab6_statistics.csv')
stats.to_csv(stats_path)
print("\nОписательная статистика (все 891 запись после заполнения пропусков):")
print(stats.to_string())

# Добавляем столбец смещения (bias)
def add_bias(X):
    return np.hstack([np.ones((X.shape[0], 1)), X])

X_train_b = add_bias(X_train)
X_test_b = add_bias(X_test)

# 5. Реализация логистической регрессии с нуля (пункт 5 задания)
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def log_loss(y_true, p):
    eps = 1e-12
    p = np.clip(p, eps, 1.0 - eps)
    return -float(np.mean(y_true * np.log(p) + (1.0 - y_true) * np.log(1.0 - p)))

def gradient_descent(X, y, lr, n_iter):
    w = np.zeros((X.shape[1], 1))
    history = []
    for _ in range(n_iter):
        p = sigmoid(X @ w)
        grad = X.T @ (p - y) / X.shape[0]
        w = w - lr * grad
        history.append(log_loss(y, p))
    return w, history

def newton_method(X, y, n_iter):
    w = np.zeros((X.shape[1], 1))
    history = []
    for _ in range(n_iter):
        p = sigmoid(X @ w)
        grad = X.T @ (p - y) / X.shape[0]
        W = np.diag((p * (1.0 - p)).ravel())
        H = (X.T @ W @ X) / X.shape[0]
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(H) @ grad
        w = w - step
        history.append(log_loss(y, p))
    return w, history

def predict(X, w):
    return (sigmoid(X @ w) >= 0.5).astype(int)

def classification_metrics(y_true, y_pred):
    y_true = y_true.ravel()
    y_pred = y_pred.ravel()
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    acc = (tp + tn) / max(len(y_true), 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2.0 * prec * rec / max(prec + rec, 1e-12)
    return acc, prec, rec, f1, tp, tn, fp, fn

# 6. Исследование гиперпараметров (пункт 6 задания)
lrs = [0.01, 0.1, 0.5]
iters_list = [100, 500, 1000]
results = []

print("\n=== Исследование гиперпараметров (градиентный спуск) ===")
for lr in lrs:
    for n_it in iters_list:
        w, hist = gradient_descent(X_train_b, y_train, lr, n_it)
        y_pred = predict(X_test_b, w)
        m = classification_metrics(y_test, y_pred)
        results.append({
            'method': 'GD', 'lr': lr, 'iters': n_it,
            'final_loss': hist[-1], 'acc': m[0], 'prec': m[1], 'rec': m[2], 'f1': m[3],
            'tp': m[4], 'tn': m[5], 'fp': m[6], 'fn': m[7],
        })
        print(f"GD lr={lr} iters={n_it} loss={hist[-1]:.4f} acc={m[0]:.4f} prec={m[1]:.4f} rec={m[2]:.4f} f1={m[3]:.4f}")

print("\n=== Исследование гиперпараметров (метод Ньютона) ===")
for n_it in iters_list:
    w, hist = newton_method(X_train_b, y_train, n_it)
    y_pred = predict(X_test_b, w)
    m = classification_metrics(y_test, y_pred)
    results.append({
        'method': 'Newton', 'lr': None, 'iters': n_it,
        'final_loss': hist[-1], 'acc': m[0], 'prec': m[1], 'rec': m[2], 'f1': m[3],
        'tp': m[4], 'tn': m[5], 'fp': m[6], 'fn': m[7],
    })
    print(f"Newton iters={n_it} loss={hist[-1]:.4f} acc={m[0]:.4f} prec={m[1]:.4f} rec={m[2]:.4f} f1={m[3]:.4f}")

res_df = pd.DataFrame(results)
res_path = os.path.join(DATA_DIR, 'lab6_hyperparams.csv')
res_df.to_csv(res_path, index=False)

best = res_df.loc[res_df['f1'].idxmax()]
print("\nЛучшая комбинация:")
print(best.to_string())

# 7. Сохранение предобработанных данных для отчёта
df_train_proc.to_csv(os.path.join(DATA_DIR, 'lab6_train_preprocessed.csv'), index=False)
df_test_proc.to_csv(os.path.join(DATA_DIR, 'lab6_test_preprocessed.csv'), index=False)

# 8. Графики из фактических данных (пункт 3 задания — визуализация статистики)
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 9.5

# Гистограмма целевой переменной
plt.figure(figsize=(6, 4))
df_all_for_stats['Survived'].value_counts().sort_index().plot(kind='bar',
    color=['#c44e52', '#4c72b0'], edgecolor='black')
plt.title('Распределение целевой переменной Survived')
plt.xlabel('Survived (0 = не выжил, 1 = выжил)')
plt.ylabel('Количество пассажиров')
plt.tight_layout()
plt.savefig(os.path.join(GRAPHICS_DIR, 'lab6_survived.png'), dpi=150)
plt.close()

# Гистограммы числовых признаков
num_cols_hist = ['Age', 'Fare', 'SibSp', 'Parch']
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
for ax, col in zip(axes.ravel(), num_cols_hist):
    df_all_for_stats[col].hist(ax=ax, bins=30, color='#4c72b0', edgecolor='black')
    ax.set_title(col)
    ax.set_xlabel('')
fig.suptitle('Гистограммы числовых признаков')
fig.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.savefig(os.path.join(GRAPHICS_DIR, 'lab6_histograms.png'), dpi=150)
plt.close()

# Кривая обучения для лучшей комбинации GD
best_gd = res_df[res_df['method'] == 'GD'].loc[res_df[res_df['method'] == 'GD']['f1'].idxmax()]
lr_best = float(best_gd['lr'])
it_best = int(best_gd['iters'])
w_best, hist_best = gradient_descent(X_train_b, y_train, lr_best, it_best)
plt.figure(figsize=(6, 4))
plt.plot(hist_best, color='#4c72b0', linewidth=2)
plt.title(f'Кривая обучения (GD, lr={lr_best}, итерации={it_best})')
plt.xlabel('Итерация')
plt.ylabel('Log loss')
plt.tight_layout()
plt.savefig(os.path.join(GRAPHICS_DIR, 'lab6_learning_curve.png'), dpi=150)
plt.close()

# Тепловая карта F1 по гиперпараметрам GD
pivot = res_df[res_df['method'] == 'GD'].pivot_table(values='f1', index='lr', columns='iters', aggfunc='max')
fig, ax = plt.subplots(figsize=(6.5, 4))
im = ax.imshow(pivot.values, aspect='auto', cmap='viridis')
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_xlabel('Количество итераций')
ax.set_ylabel('Learning rate')
ax.set_title('F1-Score (градиентный спуск)')
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        ax.text(j, i, f"{pivot.values[i, j]:.2f}", ha='center', va='center', color='white')
fig.colorbar(im, ax=ax, label='F1-Score')
fig.tight_layout()
plt.savefig(os.path.join(GRAPHICS_DIR, 'lab6_hyperparam_heatmap.png'), dpi=150)
plt.close()

print("\nГотово: статистика и гиперпараметры в data/, графики в graphics/.")
