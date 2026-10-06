#!/usr/bin/env python3
import csv, math, statistics, matplotlib.pyplot as plt

files = {
    'read-seq': 'results_read.csv',
    'read-rand': 'results_read.csv',
}

def get_wall(file, graph_filter):
    rows = []
    with open(file) as f:
        for r in csv.DictReader(f):
            if graph_filter in r['graph']:
                rows.append(float(r['wall_time_s']))
    # Отбрасываем прогрев k=2
    return rows[2:] if len(rows) > 2 else rows

data = {
    'read-seq': get_wall('results_read.csv', 'graph-seq'),
    'read-rand': get_wall('results_read.csv', 'graph-rand'),
}

for k, v in data.items():
    mean = statistics.mean(v)
    std = statistics.stdev(v) if len(v) > 1 else 0.0
    ci = 1.96 * std / math.sqrt(len(v))
    print(f"{k}: N={len(v)} mean={mean:.4f} std={std:.4f} CI95={ci:.4f}")

fig, ax = plt.subplots(figsize=(8, 5))
labels = list(data.keys())
means = [statistics.mean(data[k]) for k in labels]
stds = [statistics.stdev(data[k]) if len(data[k]) > 1 else 0 for k in labels]
errors = [1.96 * s / math.sqrt(len(data[k])) for k, s in zip(labels, [statistics.stdev(data[k]) if len(data[k]) > 1 else 0 for k in labels])]
ax.bar(labels, means, yerr=errors, capsize=5, color=['#4c72b0', '#dd8452'])
ax.set_ylabel('Wall time (s)')
ax.set_title('Read traversal: seq vs rand (N=10, k=2 прогрев)')
ax.set_ylim(0, max(means) + max(errors) + 1)
for i, (k, v) in enumerate(data.items()):
    ax.text(i, means[i] + errors[i] + 0.1, f"mean={means[i]:.2f}\nCI±{errors[i]:.2f}", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('analysis_plot.png', dpi=150)
print("analysis_plot.png saved")
