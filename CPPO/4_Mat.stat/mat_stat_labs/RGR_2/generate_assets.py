import csv
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
OUT = BASE / 'plots'
OUT.mkdir(exist_ok=True)


def load_data():
    rows = []
    with (BASE / 'data_rgr_2.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            rows.append({k: float(v) for k, v in row.items()})
    return {
        'X1': np.array([r['X1'] for r in rows], dtype=float),
        'X2': np.array([r['X2'] for r in rows], dtype=float),
        'X3': np.array([r['X3'] for r in rows], dtype=float),
        'X4': np.array([r['X4'] for r in rows], dtype=float),
    }


def qq_plot(ax, x, title):
    x = np.sort(x)
    n = len(x)
    p = (np.arange(1, n + 1) - 0.5) / n
    z = np.array([NormalDist().inv_cdf(float(pi)) for pi in p])
    ax.scatter(z, x, s=14, alpha=0.8)

    # Reference line for N(mu, sigma^2): sample quantile ~= mu + sigma * z
    mu = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    z_line = np.array([z.min(), z.max()])
    x_line = mu + sd * z_line
    ax.plot(z_line, x_line, 'r--', lw=1.2, label='Теор. прямая N(μ,σ²)')

    ax.set_title(title)
    ax.set_xlabel('Теоретические квантили N(0,1)')
    ax.set_ylabel('Выборочные квантили, мс')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)


def main():
    cols = load_data()
    x1, x2, x3, x4 = cols['X1'], cols['X2'], cols['X3'], cols['X4']
    n = len(x1)

    for name, x in cols.items():
        print(f"{name}: n={len(x)}, mean={x.mean():.6f}, var={x.var(ddof=1):.6f}, sd={x.std(ddof=1):.6f}, min={x.min():.2f}, max={x.max():.2f}")

    m1, m2, m3 = x1.mean(), x2.mean(), x3.mean()
    s1, s2, s3 = x1.var(ddof=1), x2.var(ddof=1), x3.var(ddof=1)
    sp = ((n - 1) * s1 + (n - 1) * s2) / (2 * n - 2)
    t_pooled = (m1 - m2) / math.sqrt(sp * (2 / n))
    se = math.sqrt(s1 / n + s2 / n)
    t_welch = (m1 - m2) / se
    df_welch = (s1 / n + s2 / n) ** 2 / ((s1 / n) ** 2 / (n - 1) + (s2 / n) ** 2 / (n - 1))
    mu0 = 62.55
    t3 = (m3 - mu0) / math.sqrt(s3 / n)
    print(f"X1/X2 pooled: t={t_pooled:.6f}, df={2*n-2}")
    print(f"X1/X2 Welch:  t={t_welch:.6f}, df={df_welch:.6f}")
    print(f"X3: xbar={m3:.6f}, s={math.sqrt(s3):.6f}, t={t3:.6f}, df={n-1}")

    lmbd = 0.085
    k = 8
    bounds = [0.0]
    for i in range(1, k):
        bounds.append(-math.log(1 - i / k) / lmbd)
    bounds.append(float('inf'))
    obs = []
    exp = []
    for i in range(k):
        a, b = bounds[i], bounds[i + 1]
        cnt = int(np.sum((x4 >= a) & (x4 < b)))
        obs.append(cnt)
        p = math.exp(-lmbd * a) - (math.exp(-lmbd * b) if math.isfinite(b) else 0.0)
        exp.append(n * p)
    chi2 = sum((o - e) ** 2 / e for o, e in zip(obs, exp))
    print('X4 bins:')
    for i in range(k):
        a, b = bounds[i], bounds[i + 1]
        br = f"{b:.4f}" if math.isfinite(b) else 'inf'
        print(f"  {i+1}: [{a:.4f}; {br}) o={obs[i]} e={exp[i]:.3f}")
    print(f"X4 chi2={chi2:.6f}, df={k-1}")

    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11})

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs = axs.ravel()
    for ax, x, title, color in [
        (axs[0], x1, 'X1: гистограмма', '#4C78A8'),
        (axs[1], x2, 'X2: гистограмма', '#F58518'),
    ]:
        ax.hist(x, bins=10, density=True, color=color, alpha=0.75, edgecolor='white')
        mu, sd = x.mean(), x.std(ddof=1)
        xs = np.linspace(x.min() - 5, x.max() + 5, 300)
        pdf = (1 / (sd * math.sqrt(2 * math.pi))) * np.exp(-0.5 * ((xs - mu) / sd) ** 2)
        ax.plot(xs, pdf, 'k', lw=1.5, label='N(μ,σ²)')
        ax.set_title(title)
        ax.set_xlabel('мс')
        ax.set_ylabel('Плотность')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
    qq_plot(axs[2], x1, 'X1: QQ-plot')
    qq_plot(axs[3], x2, 'X2: QQ-plot')
    fig.suptitle('Диагностика нормальности для X1 и X2', y=1.02, fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / 'x1_x2_diagnostics.png', dpi=200, bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot([x1, x2], tick_labels=['X1', 'X2'], patch_artist=True,
               boxprops=dict(facecolor='#d9e8fb'), medianprops=dict(color='red'))
    ax.set_title('X1 и X2: boxplot')
    ax.set_ylabel('мс')
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / 'x1_x2_boxplot.png', dpi=200, bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(x3, bins=10, density=True, color='#54A24B', alpha=0.75, edgecolor='white')
    mu, sd = x3.mean(), x3.std(ddof=1)
    xs = np.linspace(x3.min() - 5, x3.max() + 5, 300)
    pdf = (1 / (sd * math.sqrt(2 * math.pi))) * np.exp(-0.5 * ((xs - mu) / sd) ** 2)
    ax.plot(xs, pdf, 'k', lw=1.5, label='N(μ,σ²)')
    ax.axvline(mu0, color='crimson', linestyle='--', linewidth=2, label=r'$H_0: \mu = 62.55$')
    ax.axvline(mu, color='black', linestyle=':', linewidth=2, label=rf'$\bar{{x}} = {mu:.2f}$')
    ax.set_title('X3: гистограмма и гипотезное значение среднего')
    ax.set_xlabel('мс')
    ax.set_ylabel('Плотность')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / 'x3_hist.png', dpi=200, bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    idx = np.arange(k)
    ax.bar(idx - 0.2, obs, width=0.4, label='Наблюдаемые', color='#4C78A8')
    ax.bar(idx + 0.2, exp, width=0.4, label='Ожидаемые', color='#F58518')
    ax.set_xticks(idx)
    ax.set_xticklabels([
        f'{a:.1f}-{b:.1f}' if math.isfinite(b) else f'{a:.1f}+'
        for a, b in zip(bounds[:-1], bounds[1:])
    ], rotation=35, ha='right')
    ax.set_title('X4: наблюдаемые и ожидаемые частоты для критерия Пирсона')
    ax.set_xlabel('Интервалы, мс')
    ax.set_ylabel('Частота')
    ax.legend()
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / 'x4_pearson.png', dpi=200, bbox_inches='tight')
    plt.close(fig)

    summary = {
        'stats': {
            name: {
                'n': int(len(x)),
                'mean': float(x.mean()),
                'var': float(x.var(ddof=1)),
                'sd': float(x.std(ddof=1)),
                'min': float(x.min()),
                'max': float(x.max()),
            }
            for name, x in cols.items()
        },
        'tests': {
            'x1_x2_pooled': {'t': float(t_pooled), 'df': 2 * n - 2},
            'x1_x2_welch': {'t': float(t_welch), 'df': float(df_welch)},
            'x3': {'t': float(t3), 'df': n - 1, 'mu0': mu0},
            'x4': {
                'chi2': float(chi2),
                'df': k - 1,
                'lambda': lmbd,
                'bounds': bounds[:-1],
                'obs': obs,
                'exp': exp,
            },
        },
    }
    (BASE / 'analysis_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved assets to {OUT}')


if __name__ == '__main__':
    main()


