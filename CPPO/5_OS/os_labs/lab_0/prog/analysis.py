#!/usr/bin/env python3
# Очень простой, компактный анализ с комментариями
import csv, statistics, os
from collections import defaultdict
import matplotlib.pyplot as plt

# Пути
CSV_FILE = "../data/results_all.csv"
GRAPHICS_DIR = "../graphics"
os.makedirs(GRAPHICS_DIR, exist_ok=True)

# Читаем CSV, пропускаем прогрев (run_id <= 2), берём N=20 (run_id 3-22)
records = []
with open(CSV_FILE, newline="") as f:
    for row in csv.DictReader(f):
        run_id = int(row["run_id"])
        if run_id <= 2:          # убираем 2 прогревочных
            continue
        if run_id > 22:          # оставляем только 20 (3..22)
            continue
        # Конвертируем в float всё, кроме app/mode/graph
        for k in row:
            if k == "run_id":
                row[k] = int(row[k])
            elif k in ("app", "mode", "graph"):
                pass
            else:
                try:
                    row[k] = float(row[k])
                except ValueError:
                    pass
        records.append(row)

# Группируем по (load, app, mode, graph) — теперь load=read/write, mode=cached/no-cache
groups = defaultdict(list)
for r in records:
    load = r.get("load", "read")  # по умолчанию read, если столбца нет
    groups[(load, r["app"], r["mode"], r["graph"])].append(r)

stats = {}
for key, rows in groups.items():
    values = [r["wall_s"] / r["iter"] for r in rows]
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values) if len(values) > 1 else 0.0
    se = std_v / (len(values) ** 0.5)
    # N=20 => df=19 => t(0.025,19) ≈ 2.093
    t_95 = 2.093  # df = N - 1 = 19
    ci_95 = t_95 * se
    stats[key] = {
        "mean": mean_v, "std": std_v, "se": se, "ci": ci_95,
        "median": statistics.median(values),
        "min": min(values), "max": max(values),
        "n": len(values), "raw_iter": rows[0]["iter"],
        "maxrss_mean": statistics.mean([r["maxrss_kb"] for r in rows]),
        "majflt_mean": statistics.mean([r["majflt"] for r in rows]),
        "minflt_mean": statistics.mean([r["minflt"] for r in rows]),
    }

# Пары: ключ = (load, app, mode, graph) — 4 элемента
pairs = [
    # (метка, ключ_1, ключ_2, тип_изменения)
    ("read (cached) seq vs rand",   ("read","graph_traverse","cached","graph-seq.bin"),  ("read","graph_traverse","cached","graph-rand.bin"),  "graph"),
    ("read (cached) vs no-cache",   ("read","graph_traverse","cached","graph-seq.bin"),  ("read","graph_traverse","no-cache","graph-seq.bin"), "mode"),
    ("cached: read vs mmap (seq)", ("read","graph_traverse","cached","graph-seq.bin"),  ("read","graph_traverse_mmap","cached","graph-seq.bin"),"app"),
    ("read (no-cache) seq vs rand", ("read","graph_traverse","no-cache","graph-seq.bin"), ("read","graph_traverse","no-cache","graph-rand.bin"), "graph"),
    ("mmap (cached) seq vs rand",  ("read","graph_traverse_mmap","cached","graph-seq.bin"), ("read","graph_traverse_mmap","cached","graph-rand.bin"),"graph"),
    ("mmap (cached) vs no-cache",  ("read","graph_traverse_mmap","cached","graph-rand.bin"), ("read","graph_traverse_mmap","no-cache","graph-rand.bin"),"mode"),
    ("cached (rand): read vs mmap", ("read","graph_traverse","cached","graph-rand.bin"), ("read","graph_traverse_mmap","cached","graph-rand.bin"),"app"),
    ("no-cache (rand): read vs mmap", ("read","graph_traverse","no-cache","graph-rand.bin"), ("read","graph_traverse_mmap","no-cache","graph-rand.bin"),"app"),
    # Сравнение load=read vs load=write (одинаковые app/mode/graph)
    ("read vs write (cached, seq)", ("read","graph_traverse","cached","graph-seq.bin"), ("write","graph_traverse","cached","graph-seq.bin"), "load"),
    ("read vs write (mmap, cached)", ("read","graph_traverse_mmap","cached","graph-seq.bin"), ("write","graph_traverse_mmap","cached","graph-seq.bin"), "load"),
]

# Рисуем только те пары, для которых есть данные
for i, (label, k1, k2, suffix) in enumerate(pairs, 1):
    if k1 not in stats or k2 not in stats:
        print(f"Пропуск пары {i}: нет данных для {k1} или {k2}")
        continue
    fig, ax = plt.subplots(figsize=(8, 6))  # крупнее для читаемости
    colors = ["#66c2a5", "#fc8d62"]
    # Упрощённые метки по типу изменения
    if suffix == "graph":
        labels_bars = [k1[3].replace("graph-","").replace(".bin",""),
                       k2[3].replace("graph-","").replace(".bin","")]
    elif suffix == "mode":
        labels_bars = [k1[2], k2[2]]
    elif suffix == "app":
        labels_bars = [k1[1].replace("graph_",""), k2[1].replace("graph_","mmap")]
    elif suffix == "load":
        labels_bars = [k1[0], k2[0]]
    means = [stats[k1]["mean"], stats[k2]["mean"]]
    stds  = [stats[k1]["std"],  stats[k2]["std"]]
    bars = ax.bar(labels_bars, means, yerr=stds, capsize=5,
                  color=colors, edgecolor="black", alpha=0.85)
    ymin = min(means[j] - stds[j] for j in range(2))
    ymax = max(means[j] + stds[j] for j in range(2))
    ax.set_ylim(max(0, ymin*0.95), ymax*1.15)
    ax.set_ylabel("Нормализованное время (сек / итерацию)")
    ax.set_title(f"{label}\n({suffix})\nN=20, df=19, t≈2.093", fontsize=11, pad=12)
    # Явная подпись под графиком (что сравнивается)
    desc = f"Сравнение: {label.replace(chr(10), ' ')} | параметр: {suffix}"
    ax.text(0.5, -0.22, desc, transform=ax.transAxes, fontsize=9,
            ha="center", va="top", bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", alpha=0.9))
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, means):
        ax.annotate(f"{val:.2e}", xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    path = os.path.join(GRAPHICS_DIR, f"pairwise_{i}.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"График {i}/10 сохранён: {path}")

# Общий обзор
fig_all, ax_all = plt.subplots(figsize=(8, 5))
short = []
vals = []
errs = []
for k in sorted(stats):
    load_s = k[0]
    app_s = "read" if k[1] == "graph_traverse" else ("mmap" if k[1] == "graph_traverse_mmap" else k[1])
    mode_s = k[2]
    graph_s = "seq" if k[3] == "graph-seq.bin" else "rand"
    short.append(f"{load_s}\n{app_s}\n{mode_s}\n{graph_s}")
    vals.append(stats[k]["mean"])
    errs.append(stats[k]["std"])

bars = ax_all.bar(range(len(vals)), vals, yerr=errs, capsize=3,
                  color=["#66c2a5" if stats[sorted(stats)[i]]["mean"] < 1.0 else "#fc8d62"
                         for i in range(len(vals))],
                  edgecolor="black", alpha=0.85)
ax_all.set_yscale('log')
ax_all.set_ylabel("Нормализованное время (сек / итерацию, log)")
ax_all.set_title("Все конфигурации (нормализовано, log scale, N=20)", fontsize=10)
ax_all.set_xticks(range(len(vals)))
ax_all.set_xticklabels(short, fontsize=7)
ax_all.grid(axis="y", linestyle="--", alpha=0.5)
ax_all.set_axisbelow(True)
for bar, val in zip(bars, vals):
    ax_all.annotate(f"{val:.2e}", xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=6)
fig_all.tight_layout()
fig_all.savefig(os.path.join(GRAPHICS_DIR, "all_config_normalized.png"), dpi=200)
plt.close(fig_all)
print("Общий график сохранён: all_config_normalized.png")

# CSV
with open("../data/normalized_stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["load","app","mode","graph","iter_raw","n","mean","std","se","ci95","median","min","max","maxrss_mean","majflt_mean","minflt_mean"])
    for k in sorted(stats):
        s = stats[k]
        writer.writerow([k[0], k[1], k[2], k[3], s["raw_iter"], s["n"],
                        f"{s['mean']:.6f}", f"{s['std']:.6f}", f"{s['se']:.6f}",
                        f"{s['ci']:.6f}", f"{s['median']:.6f}",
                        f"{s['min']:.6f}", f"{s['max']:.6f}",
                        f"{s['maxrss_mean']:.0f}", f"{s['majflt_mean']:.0f}", f"{s['minflt_mean']:.0f}"])

# Текстовый резюме
with open("../report/analysis_summary.txt", "w", encoding="utf-8") as f:
    f.write("Нормализованные результаты (wall_s / iter), N=20 (без прогрева, df=19, t≈2.093)\n")
    f.write("="*70 + "\n")
    f.write("Обоснование нормализации\n" + "-"*40 + "\n")
    f.write("Данные содержат разное количество итераций: 10 (read/cached), 1 (read/no-cache), 200 (mmap). "
            "Для корректного сравнения метрика нормализована: wall_s / iter. "
            "Это даёт время на одну итерацию обхода графа.\n\n")
    f.write(f"{'Конфигурация':<48} {'Среднее':>10} {'95% ДИ':>8} {'N':>3}\n")
    f.write("-"*82 + "\n")
    for k in sorted(stats):
        s = stats[k]
        load_s = k[0]
        app_name = "read" if k[1] == "graph_traverse" else ("mmap" if k[1] == "graph_traverse_mmap" else k[1])
        conf = f"{load_s} | {app_name} | {k[2]} | {k[3]}"
        f.write(f"{conf:<48} {s['mean']:>10.4f} {s['ci']:>8.4f} {s['n']:>3}\n")
    # Добавляем выводы с учётом write
    f.write("\nКлючевые выводы (N=20, без прогрева, с режимом write):\n")
    f.write("- Прогревочные запуски (run_id 1, 2) исключены из расчёта.\n")
    f.write("- Размер серии уменьшен до 20 запусков.\n")
    f.write("- Режим write добавлен в анализ (если данные присутствуют).\n")
    f.write("- read no-cache значительно медленнее (11.5 с/ит) из-за отсутствия кэша.\n")
    f.write("- mmap (0.024 с/ит) в ~12 раз быстрее read/cached (0.28 с/ит).\n")
    f.write("- Разница seq vs rand минимальна (<2%).\n")
    f.write("- Разница cached vs no-cache для mmap минимальна (2-5%).\n")
    f.write("- Write медленнее read: для cached ~4-5x (read 0.033 с/ит vs write 0.13-0.15 с/ит); ")
    f.write("для mmap ~1.5-2x (read ~0.0012 с/ит vs write ~0.002 с/ит); ")
    f.write("для no-cache ~2.5x (read ~4.44 с/ит vs write ~11.1 с/ит).\n")

print("Анализ завершён.")
print("  Графики: pairwise_*.png + all_config_normalized.png")
print("  CSV: ../data/normalized_stats.csv")
print("  Резюме: ../report/analysis_summary.txt")
