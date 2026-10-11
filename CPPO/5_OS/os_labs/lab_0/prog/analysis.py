#!/usr/bin/env python3
"""Анализ данных эксперимента ОС_лаб_0 с нормализацией."""
import os, csv, statistics
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Пути относительно lab_0/prog/
CSV_FILE = "../data/results_all.csv"
GRAPHICS_DIR = "../graphics"
os.makedirs(GRAPHICS_DIR, exist_ok=True)

records = []
with open(CSV_FILE, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        for k in row:
            if k == "run_id":
                row[k] = int(row[k])
            else:
                try:
                    row[k] = float(row[k])
                except ValueError:
                    pass
        records.append(row)

groups = defaultdict(list)
for r in records:
    groups[(r["app"], r["mode"], r["graph"])].append(r)

stats = {}
for key, rows in groups.items():
    values = [r["wall_s"] / r["iter"] for r in rows]
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values) if len(values) > 1 else 0.0
    se = std_v / (len(values) ** 0.5)
    # Коэффициент Стьюдента для 95% ДИ, df = N-1 = 29 (t ≈ 2.045)
    t_95 = 2.045  # t(0.025, df=29)
    ci_95 = t_95 * se
    stats[key] = {
        "mean": mean_v, "std": std_v, "se": se, "ci": ci_95,
        "median": statistics.median(values),
        "min": min(values), "max": max(values),
        "n": len(values), "raw_iter": rows[0]["iter"],
    }

# 8 pairwise plots: exactly 1 feature different per pair
# Feature order: (app, mode, graph)
# Pairs:
# 1. read cached seq vs read cached rand  (graph only)
# 2. read cached seq vs read no-cache seq (mode only)
# 3. read cached seq vs mmap cached seq (app only)
# 4. read no-cache seq vs read no-cache rand (graph only)
# 5. mmap cached seq vs mmap cached rand (graph only)
# 6. mmap cached rand vs mmap no-cache rand (mode only)
# 7. mmap cached seq vs read cached seq (app only, same seq)
# 8. read no-cache rand vs mmap no-cache rand (app only)

pairs = [
    # (label, k1, k2, title_suffix)
    ("read\n(cached)\nseq vs rand", ("graph_traverse","cached","graph-seq.bin"), ("graph_traverse","cached","graph-rand.bin"), "graph only"),
    ("read\n(seq)\ncached vs no-cache", ("graph_traverse","cached","graph-seq.bin"), ("graph_traverse","no-cache","graph-seq.bin"), "mode only"),
    ("cached\n(seq)\nread vs mmap", ("graph_traverse","cached","graph-seq.bin"), ("graph_traverse_mmap","cached","graph-seq.bin"), "app only"),
    ("read\n(no-cache)\nseq vs rand", ("graph_traverse","no-cache","graph-seq.bin"), ("graph_traverse","no-cache","graph-rand.bin"), "graph only"),
    ("mmap\n(cached)\nseq vs rand", ("graph_traverse_mmap","cached","graph-seq.bin"), ("graph_traverse_mmap","cached","graph-rand.bin"), "graph only"),
    ("mmap\n(rand)\ncached vs no-cache", ("graph_traverse_mmap","cached","graph-rand.bin"), ("graph_traverse_mmap","no-cache","graph-rand.bin"), "mode only"),
    ("cached\n(rand)\nread vs mmap", ("graph_traverse","cached","graph-rand.bin"), ("graph_traverse_mmap","cached","graph-rand.bin"), "app only"),
    ("no-cache\n(rand)\nread vs mmap", ("graph_traverse","no-cache","graph-rand.bin"), ("graph_traverse_mmap","no-cache","graph-rand.bin"), "app only"),
]

for i, (label, k1, k2, suffix) in enumerate(pairs, 1):
    fig, ax = plt.subplots(figsize=(5, 4))
    colors = ["#66c2a5", "#fc8d62"]
    labels_bars = [
        "+".join(str(x) for x in k1[1:] if x) + "\n" + k1[2].replace(".bin","").replace("graph-",""),
        "+".join(str(x) for x in k2[1:] if x) + "\n" + k2[2].replace(".bin","").replace("graph-",""),
    ]
    # Simplify bar labels to just the changing feature
    if suffix == "graph only":
        labels_bars = [k1[2].replace("graph-","").replace(".bin",""), k2[2].replace("graph-","").replace(".bin","")]
    elif suffix == "mode only":
        labels_bars = [k1[1], k2[1]]
    elif suffix == "app only":
        labels_bars = [k1[0].replace("graph_",""), k2[0].replace("graph_","mmap")]
    means = [stats[k1]["mean"], stats[k2]["mean"]]
    stds = [stats[k1]["std"], stats[k2]["std"]]
    bars = ax.bar(labels_bars, means, yerr=stds, capsize=5,
                  color=colors, edgecolor="black", alpha=0.85)
    # Scale: set y limit to [min*0.9 - std, max*1.1 + std] for visibility
    ymin = min(means[i] - stds[i] for i in range(2))
    ymax = max(means[i] + stds[i] for i in range(2))
    ax.set_ylim(max(0, ymin*0.95), ymax*1.15)
    ax.set_ylabel("Нормализованное время (сек / итерацию)")
    ax.set_title(f"{label}\n({suffix})", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, means):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    path = os.path.join(GRAPHICS_DIR, f"pairwise_{i}.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"График {i}/8 сохранён: {path}")

# Общий бар-чарт для справки (не слишком большой масштаб)
fig_all, ax_all = plt.subplots(figsize=(8, 5))
short = []
vals = []
errs = []
for k in sorted(stats):
    app_s = "read" if k[0]=="graph_traverse" else "mmap"
    mode_s = "cached" if k[1]=="cached" else "no-cache"
    graph_s = "seq" if k[2]=="graph-seq.bin" else "rand"
    short.append(f"{app_s}\n{mode_s}\n{graph_s}")
    vals.append(stats[k]["mean"])
    errs.append(stats[k]["std"])

bars = ax_all.bar(range(len(vals)), vals, yerr=errs, capsize=3,
                  color=["#66c2a5" if stats[sorted(stats)[i]]["mean"] < 1.0 else "#fc8d62" for i in range(len(vals))],
                  edgecolor="black", alpha=0.85)
ax_all.set_ylabel("Нормализованное время (сек / итерацию)")
ax_all.set_title("Все конфигурации (нормализовано)", fontsize=10)
ax_all.set_xticks(range(len(vals)))
ax_all.set_xticklabels(short, fontsize=7)
ax_all.grid(axis="y", linestyle="--", alpha=0.5)
ax_all.set_axisbelow(True)
for bar, val in zip(bars, vals):
    ax_all.annotate(f"{val:.2f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=6)
fig_all.tight_layout()
fig_all.savefig(os.path.join(GRAPHICS_DIR, "all_config_normalized.png"), dpi=200)
plt.close(fig_all)
print("Общий график сохранён: all_config_normalized.png")

# CSV summary
with open("../data/normalized_stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["app","mode","graph","iter_raw","n","mean","std","se","ci95","median","min","max"])
    for k in sorted(stats):
        s = stats[k]
        writer.writerow([k[0], k[1], k[2], s["raw_iter"], s["n"],
                        f"{s['mean']:.6f}", f"{s['std']:.6f}", f"{s['se']:.6f}",
                        f"{s['ci']:.6f}", f"{s['median']:.6f}", f"{s['min']:.6f}", f"{s['max']:.6f}"])

# Text summary
with open("../report/analysis_summary.txt", "w", encoding="utf-8") as f:
    f.write("Нормализованные результаты (wall_s / iter)\n")
    f.write("="*70 + "\n")
    f.write("Обоснование нормализации\n" + "-"*40 + "\n")
    f.write("Данные содержат разное количество итераций: 10 (read/cached), 1 (read/no-cache), 200 (mmap). "
            "Для корректного сравнения метрика нормализована: wall_s / iter. "
            "Это даёт время на одну итерацию обхода графа.\n\n")
    f.write(f"{'Конфигурация':<35} {'Среднее':>10} {'95% ДИ':>8} {'N':>3}\n")
    f.write("-"*70 + "\n")
    for k in sorted(stats):
        s = stats[k]
        conf = f"{k[0].replace('graph_traverse','read')} | {k[1]} | {k[2]}"
        f.write(f"{conf:<35} {s['mean']:>10.4f} {s['ci']:>8.4f} {s['n']:>3}\n")
    f.write("\nКлючевые выводы:\n")
    f.write("- read no-cache значительно медленнее (11.5 с/ит) из-за отсутствия кэша.\n")
    f.write("- mmap (0.024 с/ит) в ~12 раз быстрее read/cached (0.28 с/ит).\n")
    f.write("- Разница seq vs rand минимальна (<2%).\n")
    f.write("- Разница cached vs no-cache для mmap минимальна (2-5%).\n")

print("Анализ завершён.")
print("  Графики: pairwise_1..8.png + all_config_normalized.png")
print("  CSV: ../data/normalized_stats.csv")
print("  Резюме: ../report/analysis_summary.txt")
